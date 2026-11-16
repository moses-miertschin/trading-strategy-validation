"""Mutation-testing driver, hardened, and versioned so the hardening persists.

WHY THIS FILE EXISTS AT ALL. This driver has damaged this repository three
times, and every time it was `git status` that noticed, not the driver:

  1. a perturbation LEAKED a fixture file; on the next run the baseline digest
     already contained it, so the check it was meant to break passed instead.
  2. bytecode is keyed on (mtime, size) and the driver rewrites files
     sub-second, so one perturbation ran against another's stale `.pyc` and
     reported that perturbation's failure as its own.
  3. on 2026-08-05 it restored files in TEXT mode -- which reads CRLF as LF and
     writes LF back -- so on a CRLF file the restore was not byte-exact. It
     rewrote `trading-research/tests/reproducibility_sweep.py`, INSIDE THE
     TAGGED TREE, and reported `restored=True` because it compared text to
     text. The same session, a perturbation containing a live `git commit`
     EXECUTED, committing the perturbed source and every other modified file.

It lived in a scratchpad, so each session re-derived it and re-earned the same
defects. It is now in the repository, with four guards, each demonstrated
firing by `--self-test`. **A driver that audits other code and not itself is
the shape this project has spent a week catching.**

THE FOUR GUARDS
  G1  RESTORE IS BYTE-EXACT AND NEVER TEXT MODE. Read `rb`, write `wb`, and
      compare bytes afterwards. A mismatch aborts the whole run.
  G2  A PERTURBATION CONTAINING A MUTATING GIT VERB IS NEVER EXECUTED. The
      pattern is the widened one the ops suite uses, so the driver and the
      suite agree on what "a commit" looks like. Checked BEFORE anything is
      written.
  G3  THE WORKING TREE MUST BE BYTE-IDENTICAL AFTERWARDS. `git status
      --porcelain` is captured before the run and compared after every single
      perturbation. Any difference aborts loudly, naming the paths.
  G4  BYTECODE IS CLEARED BEFORE EVERY SUITE RUN.

Placement: `tools/` is outside `SWEPT_DIRS = ("validation", "backtest/
strategies", "data")`, so nothing here can break N1 or move the N4 fingerprint.

Usage:
    python tools/mutate.py --self-test        # demonstrate all four guards
    python tools/mutate.py --audit-anchors    # every anchor still exists (fast)
    python tools/mutate.py <suite-name>       # run a registered suite's set

WHY --audit-anchors EXISTS. `run_set` already reports a skipped anchor and fails
the run, so nothing is silent -- but it only says so after the whole set has
run, which is tens of minutes. An anchor dies when the code it points at is
IMPROVED, which is exactly when someone is in a hurry. This is the same audit,
statically, in under a second, and it also reports an anchor that matches more
than once: `src.replace(old, new, 1)` perturbs only the first occurrence, so an
ambiguous anchor may be perturbing something other than what its name says.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The SAME pattern ops/tests/test_ops.py uses. If the two ever diverge, the
# driver would happily execute something the suite forbids.
MUTATING_GIT = re.compile(
    r"git\W{0,8}(commit|push|add|reset|checkout|rm|mv|tag|stash)", re.I)

# WIDENED 2026-08-06 after adversarial review defeated the pattern above with
# `["git", "-C", REPO, "commit", ...]` (a word character lands inside the
# \W{0,8} gap), with verbs the alternation never listed, and -- the sharpest --
# with a perturbation that EDITS AN EXISTING git call, so its own text never
# contains "git" at all: anchor '"status", "--porcelain"' -> replacement
# '"stash", "--porcelain"'.
#
# For perturbation text -- short, hand-written strings -- adjacency is the wrong
# model. The driver is deliberately conservative instead: any mutating verb
# anywhere in the text, when "git" appears in EITHER the anchor or the
# replacement, is refused. A false positive costs one rewritten perturbation.
MUTATING_VERB = re.compile(
    r"\b(commit|push|add|reset|checkout|clean|restore|switch|branch|merge|"
    r"rebase|revert|stash|gc|worktree|update-ref|symbolic-ref|prune|"
    r"filter-branch|rm|mv|tag)\b", re.I)
# Narrow on purpose. `os.remove` appears in legitimate perturbations -- P1
# introduces one against a file in a throwaway snapshot directory -- so a broad
# rule refuses honest work. Only the catastrophic, unrecoverable shapes are
# pre-empted here; everything else is left to G3, which now compares HEAD and
# every ref as well as the worktree. G3 DETECTS rather than PREVENTS, and that
# asymmetry is deliberate: the cost of a false refusal is a rewritten
# perturbation, and the cost of a false pass is a damaged repository.
DESTRUCTIVE_PY = re.compile(r"(rmtree|\.git\b|git\.Repo)")

BANNER_OK, BANNER_FAIL = "CHECKS PASSED", "CHECK(S) FAILED"


class DriverAbort(Exception):
    """The driver has stopped trusting itself. Never caught internally."""


def clear_bytecode(roots):                                            # G4
    n = 0
    for r in roots:
        for dp, dn, _ in os.walk(r):
            for d in list(dn):
                if d == "__pycache__":
                    shutil.rmtree(os.path.join(dp, d), ignore_errors=True)
                    n += 1
    return n


def tree_state(repo):                                                 # G3
    """The repository's observable state: worktree, HEAD, and every ref.

    WIDENED 2026-08-06 after adversarial review. `git status --porcelain` alone
    describes the WORKTREE and INDEX only. It is silent about HEAD, branches
    and **tags** -- so a perturbation that deleted
    `project-capstone-2026-08-03`, or switched branches, left porcelain
    byte-identical and G3 saw nothing. On a repository whose five conditions
    hang off a tag, that was the wrong thing to be blind to.

    `__pycache__` is excluded: a build artefact G4 removes anyway, gitignored in
    the real repository, and G3 fired on its own bytecode without this.
    """
    out = []
    for cmd in (["git", "status", "--porcelain"],
                ["git", "rev-parse", "HEAD"],
                ["git", "for-each-ref", "--format=%(refname) %(objectname)"]):
        r = subprocess.run(cmd, cwd=repo, capture_output=True, text=True)
        if r.returncode != 0:
            raise DriverAbort(f"{' '.join(cmd)} failed: {r.stderr.strip()}")
        out += sorted(l for l in r.stdout.splitlines()
                      if l.strip() and "__pycache__" not in l)
    return "\n".join(out)


def files_under(root):
    out = set()
    if not os.path.isdir(root):
        return out
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d != "__pycache__"]
        out.update(os.path.join(dp, f) for f in fn)
    return out


def restore_bytes(full, raw):                                         # G1
    """Put the original bytes back and PROVE it. Extracted so the self-test can
    exercise the guard directly and fail by name instead of aborting."""
    open(full, "wb").write(raw)
    if open(full, "rb").read() != raw:
        raise DriverAbort(
            f"BYTE-EXACT RESTORE FAILED for {full}. This is the 2026-08-05 "
            "defect: a text-mode restore rewrites CRLF as LF and still looks "
            "correct to a text comparison.")


def refuse_if_mutating(name, old, new):                               # G2
    for label, text in (("anchor", old), ("replacement", new)):
        m = MUTATING_GIT.search(text)
        if m:
            raise DriverAbort(
                f"REFUSED {name}: its {label} contains {m.group(0)!r}. A "
                "perturbation must never insert an executable side effect "
                "outside the file under test -- one such perturbation ran and "
                "created a commit on 2026-08-05.")
    # Conservative second pass: "git" anywhere in the pair, plus a mutating verb
    # anywhere in either half. Catches `git -C <path> commit`, unlisted verbs,
    # and a perturbation that rewrites the verb of an EXISTING git call.
    # INTRODUCES, not merely contains. A perturbation that DISABLES a
    # destructive call necessarily quotes it -- D4 wraps `shutil.rmtree` in
    # `if False:` -- and a "contains" rule refused the very perturbation that
    # demonstrates G4. What matters is whether the replacement adds a verb the
    # anchor did not already have.
    def introduced(pattern):
        seen = {m.group(0).lower() for m in pattern.finditer(old)}
        for m in pattern.finditer(new):
            if m.group(0).lower() not in seen:
                return m.group(0)
        return None

    if "git" in (old + new).lower():
        v = introduced(MUTATING_VERB)
        if v:
            raise DriverAbort(
                f"REFUSED {name}: a git call is in scope and the replacement "
                f"introduces the mutating verb {v!r}. Rewrite the perturbation "
                "so it cannot run a repository-mutating command -- see R10/R11 "
                "for how to demonstrate such a check without one.")
    v = introduced(DESTRUCTIVE_PY)
    if v:
        raise DriverAbort(
            f"REFUSED {name}: its replacement introduces {v!r}. A perturbation "
            "does not need to delete anything, and G3 detects the damage only "
            "after it is done.")


def run_suite(suite, repo):
    """`suite` may carry arguments, so the driver's own --self-test can be a
    registered suite and be audited by the same mechanism as everything else."""
    return subprocess.run([sys.executable] + suite.split(), cwd=repo,
                          capture_output=True, text=True)


def apply_one(name, path, old, new, suite, repo, roots, baseline):
    """One perturbation, with all four guards. Returns a result dict."""
    refuse_if_mutating(name, old, new)                                # G2
    full = os.path.join(repo, path.replace("/", os.sep))
    raw = open(full, "rb").read()                                     # G1
    src = raw.decode("utf-8")
    if old not in src:
        return {"name": name, "path": path, "skipped": True}

    before = {r: files_under(r) for r in roots}
    try:
        open(full, "wb").write(src.replace(old, new, 1).encode("utf-8"))
        clear_bytecode(roots)                                         # G4
        r = run_suite(suite, repo)
    finally:
        restore_bytes(full, raw)                                      # G1

    for root in roots:
        for stray in files_under(root) - before[root]:
            os.remove(stray)
    clear_bytecode(roots)                                             # G4

    after = tree_state(repo)                                          # G3
    if after != baseline:
        raise DriverAbort(
            f"{name}: THE WORKING TREE IS NOT WHAT IT WAS.\n"
            f"--- before ---\n{baseline}\n--- after ---\n{after}\n"
            "A perturbation had a side effect the driver does not undo. "
            "Nothing further is trustworthy; fix the perturbation.")

    out = r.stdout
    return {"name": name, "path": path, "skipped": False,
            "fails": [l.strip()[7:] for l in out.splitlines()
                      if l.strip().startswith("[FAIL]")],
            "crashed": BANNER_OK not in out and BANNER_FAIL not in out,
            "tail": (out + r.stderr).splitlines()[-4:]}


def run_set(suite, perturbations, roots, repo=REPO):
    print(f"MUTATION RUN -- {suite}\n" + "=" * 70)
    baseline = tree_state(repo)
    print(f"baseline working tree: {len(baseline.splitlines())} changed path(s)")
    ok, demonstrated = True, set()

    for name, path, old, new in perturbations:
        res = apply_one(name, path, old, new, suite, repo, roots, baseline)
        if res.get("skipped"):
            print(f"\n{name}\n  SKIPPED: anchor not found in {path}")
            ok = False
            continue
        demonstrated.update(res["fails"])
        print(f"\n{name}   [{path}]")
        print(f"  fails={len(res['fails'])} crashed={res['crashed']}")
        for f in res["fails"]:
            print(f"    FAILED: {f}")
        if res["crashed"]:
            for l in res["tail"]:
                print("      " + l)
        if not res["fails"] and not res["crashed"]:
            print("    *** THIS CHECK CANNOT FAIL -- it is decoration ***")
            ok = False

    clear_bytecode(roots)
    clean = run_suite(suite, repo)
    if BANNER_OK not in clean.stdout:
        raise DriverAbort("the suite does not pass cleanly after the run")
    names = [l.strip()[7:] for l in clean.stdout.splitlines()
             if l.strip().startswith("[PASS]")]
    uncovered = [n for n in names if n not in demonstrated]
    print("\n" + "=" * 70)
    print(f"COVERAGE: {len(names) - len(uncovered)}/{len(names)} demonstrated")
    for n in uncovered:
        print(f"  NEVER OBSERVED TO FAIL: {n}")
    if tree_state(repo) != baseline:
        raise DriverAbort("the working tree changed across the whole run")
    return 0 if (ok and not uncovered) else 1


# ---------------------------------------------------------------------------
# Self-test: every guard demonstrated FIRING, in a throwaway git repository so
# a demonstration can never touch the real one.
# ---------------------------------------------------------------------------
def _mk_repo():
    d = tempfile.mkdtemp(prefix="mutate_selftest_")
    for cmd in (["git", "init", "-q"],
                ["git", "config", "user.email", "t@t"],
                ["git", "config", "user.name", "t"]):
        subprocess.run(cmd, cwd=d, capture_output=True)
    # CRLF on purpose: this is the file class the text-mode restore corrupted.
    open(os.path.join(d, "mod.py"), "wb").write(
        b"MARKER = 1\r\nVALUE = 2\r\n")
    open(os.path.join(d, "suite.py"), "wb").write(
        b"import mod\nprint('  [PASS] value is 2' if mod.VALUE == 2 else\n"
        b"      '  [FAIL] value is 2')\nprint('ALL 1 CHECKS PASSED')\n")
    open(os.path.join(d, "tracked.txt"), "wb").write(b"original\n")
    subprocess.run(["git", "add", "-A"], cwd=d, capture_output=True)
    subprocess.run(["git", "commit", "-qm", "init"], cwd=d, capture_output=True)
    return d


def self_test():
    print("=" * 70)
    print("mutate.py self-test -- every guard demonstrated FIRING")
    print("=" * 70)
    passed = failed = 0

    def check(name, cond, detail=""):
        nonlocal passed, failed
        if cond:
            passed += 1
            print(f"  [PASS] {name}")
        else:
            failed += 1
            print(f"  [FAIL] {name}" + (f"\n         {detail}" if detail else ""))

    # ONE CHECK PER GUARD, each demonstrable by exactly one perturbation of
    # this file (D1-D4 in tools/perturbations.py). An earlier version had ten
    # checks, seven of which were supporting assertions that no perturbation
    # could fail individually -- decoration by the project's own definition.
    # The supporting conditions are merged into the four that remain.
    d = _mk_repo()
    roots = [d]
    base = tree_state(d)
    full = os.path.join(d, "mod.py")
    raw = open(full, "rb").read()
    try:
        # ---- G1 ---------------------------------------------------------
        print("\n== G1: restore is byte-exact, never text mode ==")
        # The 2026-08-05 defect, reproduced exactly: READ through text mode
        # (universal newlines turn CRLF into LF in memory) and write back. It
        # is the READ that corrupts, which is why decoding the bytes instead
        # does not reproduce it -- the first version of this demonstration made
        # that mistake and passed while proving nothing.
        mangled = open(full, encoding="utf-8").read()
        open(full, "w", encoding="utf-8", newline="").write(mangled)
        was_corrupted = open(full, "rb").read() != raw
        try:
            restore_bytes(full, raw)
            restored_exactly = open(full, "rb").read() == raw
        except DriverAbort:
            restored_exactly = False
        check("G1: a text-mode round trip corrupts a CRLF file, and "
              "restore_bytes puts it back exactly",
              was_corrupted and restored_exactly,
              f"corrupted={was_corrupted} restored={restored_exactly}")

        # ---- G2 ---------------------------------------------------------
        print("\n== G2: a mutating git verb is never executed ==")
        forms = ['subprocess.run(["git", "commit", "-am", "x"])',
                 "subprocess.run(['git', 'commit'])",
                 'os.system("git commit -am x")',
                 'subprocess.run("git push", shell=True)',
                 '[ "git" , "commit" ]',
                 'repo.git.commit(m="x")',
                 '["git", "Commit"]',
                 '["git", "reset", "--hard"]',
                 # The evasions adversarial review found on 2026-08-06.
                 '["git", "-C", REPO, "commit", "-am", "x"]',
                 'subprocess.run(["git", "clean", "-fdx"])',
                 'subprocess.run(["git", "restore", "."])',
                 'subprocess.run(["git", "switch", "-c", "other"])',
                 'shutil.rmtree(".git")']
        refused = 0
        for f in forms:
            try:
                apply_one("g2", "mod.py", "VALUE = 2", "VALUE = 2\n" + f,
                          "suite.py", d, roots, base)
            except DriverAbort:
                refused += 1
        try:                       # a benign perturbation must NOT be refused
            apply_one("g2 benign", "mod.py", "VALUE = 2", "VALUE = 4",
                      "suite.py", d, roots, base)
            benign_ran = True
        except DriverAbort:
            benign_ran = False
        check("G2: every realistic commit form is refused, the file is never "
              "written, and a benign perturbation still runs",
              refused == len(forms) and open(full, "rb").read() == raw
              and benign_ran,
              f"{refused}/{len(forms)} refused, benign_ran={benign_ran}")

        # ---- G3 ---------------------------------------------------------
        print("\n== G3: the working tree must be byte-identical afterwards ==")
        subprocess.run(["git", "tag", "demo-tag"], cwd=d, capture_output=True)
        base = tree_state(d)
        side_effect = ("VALUE = 2\nopen(__file__.replace('mod.py',"
                       "'tracked.txt'), 'w').write('CHANGED')\n")
        fired = False
        try:
            apply_one("g3", "mod.py", "VALUE = 2", side_effect,
                      "suite.py", d, roots, base)
        except DriverAbort as exc:
            fired = "NOT WHAT IT WAS" in str(exc)
        subprocess.run(["git", "checkout", "--", "."], cwd=d,
                       capture_output=True)
        # A REF-ONLY change: porcelain stays byte-identical, so the pre-2026-08-06
        # tree_state saw nothing. This repository's five conditions hang off a tag.
        subprocess.run(["git", "tag", "-d", "demo-tag"], cwd=d,
                       capture_output=True)
        ref_change_seen = tree_state(d) != base
        subprocess.run(["git", "tag", "demo-tag"], cwd=d, capture_output=True)
        check("G3: a modified tracked file aborts, a deleted TAG is seen, and "
              "the tree is recoverable afterwards",
              fired and ref_change_seen and tree_state(d) == base,
              f"fired={fired} ref_change_seen={ref_change_seen}")

        # ---- G4 ---------------------------------------------------------
        print("\n== G4: bytecode is cleared between runs ==")
        pyc = os.path.join(d, "__pycache__")
        os.makedirs(pyc, exist_ok=True)
        open(os.path.join(pyc, "stale.pyc"), "wb").write(b"x")
        removed = clear_bytecode(roots)
        check("G4: a stale __pycache__ is removed",
              removed >= 1 and not os.path.isdir(pyc), f"removed={removed}")
    finally:
        shutil.rmtree(d, ignore_errors=True)

    print("\n" + "=" * 70)
    if failed:
        print(f"{failed} CHECK(S) FAILED, {passed} passed")
        print("=" * 70)
        return 1
    print(f"ALL {passed} CHECKS PASSED")
    print("=" * 70)
    return 0


def audit_anchors(sets, repo=REPO):
    """Every registered anchor still exists, exactly once. Pure read."""
    print("ANCHOR AUDIT\n" + "=" * 70)
    dead = ambiguous = total = 0
    for suite, (_, perturbations, _) in sorted(sets.items()):
        for name, path, old, _ in perturbations:
            total += 1
            full = os.path.join(repo, path.replace("/", os.sep))
            if not os.path.isfile(full):
                print(f"  MISSING FILE  {suite}/{name}: {path}")
                dead += 1
                continue
            n = open(full, "rb").read().decode("utf-8").count(old)
            if n == 0:
                print(f"  DEAD ANCHOR   {suite}/{name}\n"
                      f"                would SKIP; anchor not in {path}")
                dead += 1
            elif n > 1:
                print(f"  AMBIGUOUS x{n} {suite}/{name}\n"
                      f"                only the FIRST occurrence in {path} is "
                      f"perturbed")
                ambiguous += 1
    print("=" * 70)
    print(f"{total} anchors: {dead} dead, {ambiguous} ambiguous")
    if not dead and not ambiguous:
        print("every anchor resolves to exactly one site")
    return 1 if dead else 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        sys.exit(self_test())
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from perturbations import SETS                              # noqa: E402
    if "--audit-anchors" in sys.argv:
        sys.exit(audit_anchors(SETS))
    if len(sys.argv) != 2 or sys.argv[1] not in SETS:
        print(f"usage: python tools/mutate.py [--self-test|{'|'.join(SETS)}]")
        sys.exit(2)
    suite, perturbations, roots = SETS[sys.argv[1]]
    sys.exit(run_set(suite, perturbations,
                     [os.path.join(REPO, r.replace("/", os.sep))
                      for r in roots]))
