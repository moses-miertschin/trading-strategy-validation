"""Registered perturbation sets, one per suite.

Each entry is (name, path, anchor, replacement). The driver refuses any entry
whose anchor or replacement contains a mutating git verb (guard G2), so a
perturbation can never again insert an executable side effect the way the
2026-08-05 `git commit -am auto` did.

G2 FORCED ONE REAL CHANGE, AND IT IS AN IMPROVEMENT. The ops check "no ops
module invokes a mutating git verb" used to be demonstrated by inserting
`["git", "commit", ...]` into `daily.py` behind `if False:`. G2 now refuses
that -- correctly, because text inspection cannot distinguish inert from live,
and the live version of exactly that perturbation created a commit. The check
is instead demonstrated from both sides without any git verb ever being
written into an executable file:

    R10  narrow the pattern  -> the POSITIVE CONTROL fails (it no longer
                               catches the realistic commit forms)
    R11  widen the pattern   -> the OFFENDERS check fails (it now matches
                               something every module contains)

Detection capability is proved by the positive control over eight real commit
spellings; the scanning path is proved by making it fire. Strictly safer than
the old approach, and it loses nothing.
"""

CAP = "ops/capture.py"
REV = "ops/revisions.py"
DAILY = "ops/daily.py"
TOPS = "ops/tests/test_ops.py"
PAN = "ops/pair_analysis.py"

MCR = "trading-research/followups/matched_control_recheck.py"
SWEEP = "trading-research/tests/reproducibility_sweep.py"
RFC = "trading-research/validation/_retro_floor_common.py"
CYC = "trading-research/followups/tie_structure_all_cycles.py"
CLAUDE = "trading-research/CLAUDE.md"
MSR = "trading-research/reports/Master_Strategy_Report.md"
TFU = "trading-research/followups/test_followups.py"
CMP = "ops/compare_all.py"
SSD = "trading-research/followups/swept_script_drift.py"
WC = "trading-research/followups/withdrawal_census.py"
PES = "trading-research/validation/power_engineering_study.py"
RDF = "trading-research/validation/retro_detection_floors.py"
REG = "trading-research/tests/test_regression.py"
HANDOFF = "SESSION_HANDOFF.md"
REC = "trading-research/reports/Reproducibility_Sweep.md"
WUR = "writeup/README.md"
CS = "trading-research/reports/Closing_Statement_2026-08-05.md"
GATES = "trading-research/docs/phase-gates.md"
DC = "trading-research/validation/detection_curve.py"

OPS = [
    ("P1 overwrite instead of exclusive-link", CAP,
     '    try:\n        os.link(tmp, final)\n        return "WROTE", sha',
     '    try:\n        if os.path.exists(final):\n            os.remove(final)\n'
     '        os.link(tmp, final)\n        return "WROTE", sha'),
    ("P2 drop the STALE branch", CAP,
     '    if rows[-1]["date"] != today:\n        return "STALE", meta',
     '    if False:\n        return "STALE", meta'),
    ("P3 call an empty feed OK", CAP,
     '    if not rows:\n        return "EMPTY", {"rows": 0}',
     '    if not rows:\n        return "OK", {"rows": 0}'),
    ("P4 let a fetch error propagate", CAP,
     "        except Exception as exc:                       # recorded, never raised",
     "        except ZeroDivisionError as exc:               # PERTURBED"),
    ("P5 test dividend before split", REV,
     "    price_moved = [f for f in PRICE_FIELDS if f in by_field]",
     '    if "adj_close" in by_field:\n'
     '        r = _common_ratio([c["ratio"] for c in by_field["adj_close"]])\n'
     "        if r is not None:\n"
     '            return [{"kind": "DIVIDEND", "ratio": r, "bars": dates,\n'
     '                     "note": "PERTURBED"}]\n'
     "    price_moved = [f for f in PRICE_FIELDS if f in by_field]"),
    ("P6 blind tolerance", REV, "UNCHANGED_TOL = 1e-6", "UNCHANGED_TOL = 1e-1"),
    ("P7 remove the capture-date format guard", REV,
     '    if not re.fullmatch(r"\\d{4}-\\d{2}-\\d{2}", str(old_capture_date)):',
     "    if False:"),
    ("P8 stop sweeping interrupted temp files", CAP,
     '    junk = [f for f in os.listdir(day_dir) if ".csv.tmp-" in f]',
     "    junk = []"),
    # P9 REMOVED, and guard G3 is why. It deleted the suite's log redirect so
    # the suite wrote to the REAL ops/logs/ops.jsonl. That demonstrated the
    # digest check -- but it left a MODIFIED TRACKED FILE that the driver's
    # stray-removal (new files only) cannot undo, and every session it had to
    # be repaired with `git checkout` by hand. G3 refuses it now, correctly.
    # P20 demonstrates the same "not one byte under ops/ changed" check from
    # the NEW-FILE side, which the stray-remover does clean, so no coverage is
    # lost -- only a perturbation that quietly dirtied the repository.
    ("P10 report ALREADY on a fresh write", CAP,
     '        return "WROTE", sha', '        return "ALREADY", sha'),
    ("P11 keep a numbered copy on collision", CAP,
     "    except FileExistsError:\n        stored = hashlib.sha256(",
     "    except FileExistsError:\n"
     '        open(final + ".1", "w", encoding="utf-8").write(text)\n'
     "        stored = hashlib.sha256("),
    ("P12 refuse to store a stale bar", CAP,
     "        if rows:\n            written, sha = store(",
     '        if rows and status != "STALE":\n            written, sha = store('),
    ("P13 stop recording the last bar date", CAP,
     '    meta = {"rows": len(rows), "first_bar": rows[0]["date"],\n'
     '            "last_bar": rows[-1]["date"]}',
     '    meta = {"rows": len(rows), "first_bar": rows[0]["date"]}'),
    ("P14 store even when nothing came back", CAP,
     "        if rows:\n            written, sha = store(",
     "        if True:\n            written, sha = store("),
    ("P15 accept a missing field instead of PARTIAL", CAP,
     '    if bad:\n        meta["bad_rows"] = bad[:10]',
     '    if False:\n        meta["bad_rows"] = bad[:10]'),
    ("P16 sweep renames interrupted writes into place", CAP,
     "    for f in junk:\n        os.remove(os.path.join(day_dir, f))",
     "    for f in junk:\n        os.replace(os.path.join(day_dir, f),\n"
     '                   os.path.join(day_dir, f.split(".csv.tmp-")[0] + ".csv"))'),
    ("P17 invert the reported split ratio", REV,
     '                return [{"kind": "SPLIT", "ratio": r,',
     '                return [{"kind": "SPLIT", "ratio": 1.0 / r,'),
    ("P18 stop at the first changed field per bar", REV,
     "            (provisional if d >= old_capture_date else changes).append(rec)",
     "            (provisional if d >= old_capture_date else changes).append(rec)\n"
     "            break"),
    ("P19 count unsettled bars as revisions", REV,
     "            (provisional if d >= old_capture_date else changes).append(rec)",
     "            changes.append(rec)"),
    ("P20 memoise by writing a sidecar", REV,
     "    return compare(read_snapshot(old_path), read_snapshot(new_path),",
     '    open(old_path + ".cache", "w").write("x")\n'
     "    return compare(read_snapshot(old_path), read_snapshot(new_path),"),
    ("P21 record a raising feed as OK", CAP,
     '            manifest["tickers"][t] = {"status": "ERROR",',
     '            manifest["tickers"][t] = {"status": "OK",'),
    ("P22 abandon the run at the first raising ticker", CAP,
     '                error=f"{type(exc).__name__}: {exc}")\n            continue',
     '                error=f"{type(exc).__name__}: {exc}")\n            break'),

    ("R1 weekday test dropped", DAILY,
     "        if d.weekday() < 5:", "        if True:"),
    ("R2 inclusive upper bound (today counted as missed)", DAILY,
     "    while d < end:", "    while d <= end:"),
    ("R3 empty history invents a miss", DAILY,
     "    if not past:\n        return []",
     '    if not past:\n        return ["1970-01-01"]'),
    ("R5 the job stops touching git at all", DAILY,
     '["git", "status", "--porcelain", "--", "ops/snapshots"]',
     '["gitx", "status", "--porcelain", "--", "ops/snapshots"]'),
    ("R6 scan from the last list element instead of the latest date", DAILY,
     "    last = dt.date.fromisoformat(max(past))",
     "    last = dt.date.fromisoformat(past[-1])"),
    ("R7 future-dated directories no longer excluded", DAILY,
     "    past = [h for h in have if h < today]", "    past = list(have)"),
    ("R8 the git scanner's filter stops matching", TOPS,
     '        if not fn.endswith(".py"):', '        if not fn.endswith(".pyx"):'),
    ("R9 revert to the loose date test", DAILY,
     "        try:\n            dt.date.fromisoformat(d)\n"
     "        except ValueError:\n            continue",
     "        if not (len(d) == 10 and d[4] == chr(45)):\n            continue"),
    # See the module docstring: R10/R11 replace the old R4, which G2 refuses.
    # --- Task 1: the snapshot comparison ---
    ("S1 the probe lands inside the record", CMP,
     'PROBE = os.path.join(OPS, "probe")',
     'PROBE = os.path.join(OPS, "snapshots", "probe")'),
    ("S2 any directory name counts as a capture date", CMP,
     "        try:\n            dt.date.fromisoformat(d)\n"
     "        except ValueError:\n            continue",
     "        if False:\n            continue"),
    ("S3 views lose their record/probe label", CMP,
     "    return [by_date[d] for d in sorted(by_date)]",
     '    return [(a, b, "other") for a, b, _ in\n'
     "            (by_date[d] for d in sorted(by_date))]"),
    ("S4 the provisional cut uses the NEWER capture date", CMP,
     "            rep = revisions.compare_files(f1, f2, d1)",
     "            rep = revisions.compare_files(f1, f2, d2)"),
    # S4 empties the provisional list, so the "dated on or after" check passes
    # vacuously over nothing. Inverting the comparison puts SETTLED bars into
    # the provisional bucket instead, which is what that check exists to catch.
    ("S5 the provisional comparison is inverted", REV,
     "            (provisional if d >= old_capture_date else changes).append(rec)",
     "            (provisional if d <= old_capture_date else changes).append(rec)"),

    ("R10 narrow the pattern to the one form it used to catch", TOPS,
     '        r"git\\W{0,8}(commit|push|add|reset|checkout|rm|mv|tag|stash)", re.I)',
     '        r"NOTHINGMATCHESTHIS", re.I)'),
    ("R11 widen the pattern until everything is an offender", TOPS,
     '        r"git\\W{0,8}(commit|push|add|reset|checkout|rm|mv|tag|stash)", re.I)',
     '        r"git\\W{0,8}(commit|push|add|reset|checkout|rm|mv|tag|stash)|import",'
     " re.I)"),

    # ---- 2026-08-12: the audit trail must cover every snapshot (F-C) --------
    # RE-ANCHORED 2026-08-12, hours after being written, by the F14 fix in the
    # same run. Third anchor this session killed by improving the code it points
    # at (after X2 and H5). `--audit-anchors` caught all three before commit,
    # which is the argument for running it after every edit rather than before
    # every mutation run.
    ("L1 the run_end parse matches nothing", TOPS,
     '                if (rec.get("event") in ("run_end", "reclassified_to_probe")',
     '                if (rec.get("event") in ("run_ended", "reclassified_to_probe")'),
    ("L2 the explained-gap registry names a date that is not the gap", TOPS,
     '    "2026-08-07":\n        "Found 2026-08-12',
     '    "2026-08-99":\n        "Found 2026-08-12'),

    # ---- 2026-08-12: an interior hole is not the window sliding ------------
    ("H1 classify every missing bar as a slide", TOPS,
     "        first = min(new_bars)\n        return (sorted(b for b in gone if b < first),",
     "        first = max(new_bars)\n        return (sorted(b for b in gone if b < first),"),
    ("H2 never report a slide at all", TOPS,
     "        return (sorted(b for b in gone if b < first),\n"
     "                sorted(b for b in gone if b >= first))",
     "        return ([],\n"
     "                sorted(b for b in gone if b >= first))"),
    ("H3 a real interior hole drops out of the known set", TOPS,
     '    ("VB", "2026-07-21"), ("VB", "2026-07-22"), ("VB", "2026-07-31"),',
     '    ("VB", "2026-07-21"), ("VB", "2026-07-22"),'),

    # ---- 2026-08-12: the canonical analysis never reads a probe ------------
    # Both perturb pair_analysis rather than the suite, so they break the thing
    # the checks protect rather than the checks themselves.
    # FIRST VERSION WAS DECORATION AND THE DRIVER SAID SO. It unioned the probe
    # listing into the loop but left the `isdir(join(root, d))` filter intact,
    # so a probe-only date was admitted to the loop and then dropped one line
    # later -- fails=0, "THIS CHECK CANNOT FAIL". The perturbation has to defeat
    # the filter too, or it is not perturbing what the check protects.
    ("H4 canonical_dates also scans the sibling probe directory", PAN,
     "    out = []\n"
     "    for d in sorted(os.listdir(root)):\n"
     "        if not os.path.isdir(os.path.join(root, d)):\n"
     "            continue",
     "    out = []\n"
     '    _pr = os.path.join(os.path.dirname(root), "probe")\n'
     "    for d in sorted(set(os.listdir(root)) | set(os.listdir(_pr))):\n"
     "        if not (os.path.isdir(os.path.join(root, d))\n"
     "                or os.path.isdir(os.path.join(_pr, d))):\n"
     "            continue"),
    # Anchored through the docstring: `root = root or capture.SNAPSHOTS` occurs
    # in BOTH canonical_dates() and analyse(), and replace(old, new, 1) would
    # have silently perturbed whichever came first.
    ("H5 the default root becomes the probe directory", PAN,
     '    """Capture dates on the RECORD, sorted. Probes are not the record."""\n'
     "    root = root or capture.SNAPSHOTS",
     '    """Capture dates on the RECORD, sorted. Probes are not the record."""\n'
     '    root = root or os.path.join(OPS, "probe")'),
]

FOLLOWUPS = [
    ("Q1 shuffle returns its input", MCR,
     '    assert out.sum() == sig01.sum(), "exposure budget not preserved"\n    return out',
     '    assert out.sum() == sig01.sum(), "exposure budget not preserved"\n    return sig01'),
    ("Q2 i.i.d. shuffle instead of a run shuffle", MCR,
     "    rr = runs(sig01)\n    ones = [ln for v, ln in rr if v == 1.0]",
     "    return rng.permutation(sig01)\n    rr = runs(sig01)\n"
     "    ones = [ln for v, ln in rr if v == 1.0]"),
    ("Q3 wrong SMA window", MCR,
     "def sig_sma200(close, window=200):", "def sig_sma200(close, window=150):"),
    ("Q5 shuffle-count default drifts off the recorded value", MCR,
     'SHUFFLES = int(os.environ.get("MCR_SHUFFLES", "200"))',
     'SHUFFLES = int(os.environ.get("MCR_SHUFFLES", "100"))'),
    ("Q6 followups added to the swept directories", SWEEP,
     'SWEPT_DIRS = ("validation", "backtest/strategies", "data")',
     'SWEPT_DIRS = ("validation", "backtest/strategies", "data", "followups")'),
    ("Q7 memoise into the frozen validation/ tree", MCR,
     "def sig_mom121(close, lookback=252, skip=21):",
     "def sig_mom121(close, lookback=252, skip=21):\n"
     "    open(os.path.join(BASE, 'validation', '_cache.tmp'), 'w').write('x')"),
    ("Q8 break Sharpe scale-invariance in the frozen harness", RFC,
     "    return float(np.mean(returns)) / sd * math.sqrt(periods_per_year) if sd > 0 else 0.0",
     "    return (float(np.mean(returns)) - 1e-5) / sd * math.sqrt(periods_per_year) if sd > 0 else 0.0"),
    ("Q9 drop the budget asserts and zero a run", MCR,
     "        out[pos:pos + ln] = v\n        pos += ln\n    assert pos == len(sig01)\n"
     '    assert out.sum() == sig01.sum(), "exposure budget not preserved"',
     "        out[pos:pos + ln] = v if oi != 1 else 0.0\n        pos += ln"),
    ("Q10 empty SWEPT_DIRS makes the candidate list vacuous", SWEEP,
     'SWEPT_DIRS = ("validation", "backtest/strategies", "data")',
     "SWEPT_DIRS = ()"),
    ("Q11 seed default drifts off the recorded value", MCR,
     'SEED = int(os.environ.get("MCR_SEED", "20260805"))',
     'SEED = int(os.environ.get("MCR_SEED", "1"))'),
    ("Q12 report path drifts to a different document", MCR,
     'REPORT = os.path.join(HERE, "Matched_Control_Recheck_2026-08-05.md")',
     'REPORT = os.path.join(HERE, "Placement_Cost_2026-08-05.md")'),
    # Q8 at 1e-5 moves the per-window gap to ~1e-2: enough to fail the ulp
    # check, still under the smallest NON-tie Sharpe difference, so no non-tie
    # window flips. 1e-3 moves it past that. The pair proves the two checks are
    # not redundant.
    ("Q13 break scale-invariance hard enough to flip a non-tie", RFC,
     "    return float(np.mean(returns)) / sd * math.sqrt(periods_per_year) if sd > 0 else 0.0",
     "    return (float(np.mean(returns)) - 1e-3) / sd * math.sqrt(periods_per_year) if sd > 0 else 0.0"),
    # --- Task 2: N6 ---
    ("N1 raw bytes instead of git blob ids", SSD,
     '    out = _git("hash-object", "--stdin-paths", stdin="\\n".join(rels) + "\\n")\n'
     "    return dict(zip(rels, [ln.strip()[:16] for ln in out.splitlines()]))",
     "    import hashlib\n"
     "    return {r: hashlib.sha256(open(os.path.join(REPO, "
     'r.replace("/", os.sep)), "rb").read()).hexdigest()[:16] for r in rels}'),
    ("N2 the domain drops underscore modules", SSD,
     '                if f.endswith(".py"):',
     '                if f.endswith(".py") and not f.startswith("_"):'),
    ("N3 the baseline is re-anchored to HEAD", SSD,
     "def load_baseline():\n"
     '    with open(BASELINE, encoding="utf-8") as fh:\n'
     "        return json.load(fh)",
     "def load_baseline():\n"
     '    with open(BASELINE, encoding="utf-8") as fh:\n'
     "        b = json.load(fh)\n"
     '    b["sweep_record_commit"] = _git("rev-parse", "HEAD").strip()\n'
     "    return b"),
    # A domain of ONE LF-only file, not an empty one: an empty domain makes
    # `git hash-object --stdin-paths` error and the suite abort, which
    # demonstrates nothing by name. detection_curve.py is LF on disk, so the
    # CRLF anti-vacuity check fails cleanly.
    ("N4 the domain collapses to a single LF-only script", SSD,
     '                if f.endswith(".py"):',
     '                if f == "detection_curve.py":'),

    # --- Task 3: the census ---
    ("C1 the claim threshold excludes every claim", WC,
     "MIN_CLAIM = 40", "MIN_CLAIM = 5000"),
    ("C2 the debt registry is emptied", WC,
     '    "trading-research/reports/Power_Engineering_Study_2026-07-31.md":',
     'KNOWN_DEBT = {}\n_UNUSED = {\n    "reports/Retroactive_Power_Audit_2026-07-31.md":'),
    ("C3 a debt is declared for a document that has none", WC,
     '    "trading-research/reports/Power_Engineering_Study_2026-07-31.md":',
     'KNOWN_DEBT = {\n    "trading-research/reports/Closing_Statement_2026-08-05.md": "bogus",\n'
     '    "trading-research/reports/Retroactive_Power_Audit_2026-07-31.md":'),
    ("C4 signatures stop tolerating paraphrase", WC,
     "    for drop in range(0, 5):", "    for drop in range(0, 0):"),

    # --- Task 4: the two rules ---
    ("U1 the bound rule heading is renamed", CLAUDE,
     "### Bound rule: a sample maximum is not a bound (2026-08-06)",
     "### Bound rule: some thoughts on maxima (2026-08-06)"),
    ("U2 the LOWER-bound sentence is softened", CLAUDE,
     "**A maximum over a grid of settings is a LOWER bound on the maximum. It is never",
     "**A maximum over a grid of settings is usually about right. It is never"),
    ("U3 the do-not-delete-the-bound sentence goes", CLAUDE,
     # SINGLE-LINE anchor: CLAUDE.md has CRLF, so a "\n" here never matches.
     # Third time this trap has been walked into; the rule is now absolute.
     "**The right response to a bound you cannot reach is to search harder, not to",
     "**A bound you cannot reach is not worth keeping, not to"),
    ("U4 the authorization rule heading is renamed", CLAUDE,
     "### Authorization rule: capability is not authorization (2026-08-06)",
     "### Authorization rule: some notes on scope (2026-08-06)"),
    ("U5 the authorized-not-reachable sentence is softened", CLAUDE,
     "**When scope must expand mid-run, the line is what was AUTHORIZED, not what can",
     "**When scope must expand mid-run, use judgement, not what can"),
    ("U6 the authorize-a-claim corollary goes", CLAUDE,
     "**Corollary for whoever writes the authorization: authorize a CLAIM or an",
     "**Corollary: write clear authorizations, or an"),

    # --- Task 1: the seed defect, pinned as a fact about the tree ---
    ("V1 the legacy seed becomes deterministic", PES,
     "    return abs(hash(label)) % 100000", "    return 42"),
    ("V2 the legacy seed becomes unstable even when pinned", PES,
     "    return abs(hash(label)) % 100000",
     "    import random\n    return random.randrange(100000)"),
    ("V3 the study stops using the legacy seed", PES,
     "                                      seed_fn=legacy_label_seed)",
     "                                      seed_fn=stable_label_seed)"),
    ("V4 the study pins PYTHONHASHSEED", PES,
     "def legacy_label_seed(label):",
     'os.environ["PYTHONHASHSEED"] = "0"\n\n\n'
     "def legacy_label_seed(label):"),
    ("X3 the fingerprint check stops including TIMEOUT", TFU,
     '"repr(tuple(RS.SWEPT_DIRS)),repr(sorted(RS.SCRUBBED)),"',
     '"repr(tuple(RS.SWEPT_DIRS))];"'),

    # --- Task 2: the two withdrawals, marked in the generators ---
    ("W4 RPA generator loses its strikethrough", RDF,
     "buy-and-hold. ~~That control differs from the strategy in every window, so it has",
     "buy-and-hold. That control differs from the strategy in every window, so it has"),
    ("W5 RPA generator loses its WITHDRAWN marker", RDF,
     "> **WITHDRAWN 2026-08-06.** The struck sentence is **false, and it was measured",
     "> **Note 2026-08-06.** The struck sentence is **false, and it was measured"),
    ("W6 RPA generator paraphrases the claim away", RDF,
     "buy-and-hold. ~~That control differs from the strategy in every window, so it has",
     "buy-and-hold. ~~That control was thought to help, so it has"),
    ("W7 PES generator loses its strikethrough", PES,
     "More, shorter windows versus fewer, longer ones. ~~**This lever costs nothing —",
     "More, shorter windows versus fewer, longer ones. **This lever costs nothing —"),
    ("W8 PES generator loses its WITHDRAWN marker", PES,
     "> **WITHDRAWN 2026-08-01** (`reports/Power_Study_Seed_Audit_2026-08-01.md`).",
     "> **Note 2026-08-01** (`reports/Power_Study_Seed_Audit_2026-08-01.md`)."),
    ("W9 PES generator paraphrases the claim away", PES,
     "More, shorter windows versus fewer, longer ones. ~~**This lever costs nothing —",
     "More, shorter windows versus fewer, longer ones. ~~**This lever is free —"),

    # --- Task 3: N4 covers the timeout ---
    ("X1 TIMEOUT drops out of the fingerprint", REG,
     "              repr(RS.TIMEOUT)]", "              ]"),
    # RE-ANCHORED 2026-08-12, and I rotted it myself. Task 2 (Fix C) extracted
    # the literal into a named `DEFAULT_TIMEOUT`, so the old anchor
    # `TIMEOUT = int(os.environ.get("SWEEP_TIMEOUT", 14400))` no longer exists
    # and this perturbation SKIPPED. It is the fourth instance in this project
    # of a perturbation dying because the code it was anchored to was improved,
    # and the first where the same run both broke it and repaired it. The static
    # static anchor audit (`python tools/mutate.py --audit-anchors`) exists
    # because of this one.
    ("X2 the sweep timeout default moves off the record's value", SWEEP,
     "DEFAULT_TIMEOUT = 14400", "DEFAULT_TIMEOUT = 7200"),

    # --- Task 3 (2026-08-12): Fix C, the SWEEP_TIMEOUT divert ---
    # One anchor, three replacements: the guard has three distinct ways to be
    # wrong and each check must be shown failing on its own.
    ("Y10 the timeout knob stops diverting entirely", SWEEP,
     "PARTIAL = bool(ONLY) or FAST or TIMEOUT != DEFAULT_TIMEOUT",
     "PARTIAL = bool(ONLY) or FAST"),
    ("Y11 only a LOWERED timeout diverts", SWEEP,
     "PARTIAL = bool(ONLY) or FAST or TIMEOUT != DEFAULT_TIMEOUT",
     "PARTIAL = bool(ONLY) or FAST or TIMEOUT < DEFAULT_TIMEOUT"),
    ("Y12 the guard keys on the variable being SET, not on its value", SWEEP,
     "PARTIAL = bool(ONLY) or FAST or TIMEOUT != DEFAULT_TIMEOUT",
     'PARTIAL = bool(ONLY) or FAST or "SWEEP_TIMEOUT" in os.environ'),

    # --- Task 4: N6 distinguishes expected from unexplained drift ---
    # Y1 REPOINTED 2026-08-07, same rot as Y2 and worse: it emptied
    # EXPECTED_DRIFT, and after the sweep discharged both entries the registry
    # IS empty, so there was nothing left to empty and the anchor died. The
    # check it demonstrates -- "every drifting script is declared with a reason"
    # -- can only fail when drift actually EXISTS, so the perturbation must
    # create drift rather than remove a declaration. It now edits a swept script
    # directly, which is undeclared drift by construction.
    ("Y1 a swept script drifts with nothing declaring it",
     "trading-research/validation/detection_curve.py",
     "import numpy as np",
     "import numpy as np  # PERTURBATION: undeclared swept-script drift"),
    # Y2 REPOINTED 2026-08-07. Its anchor was a line inside EXPECTED_DRIFT, and
    # emptying that registry after the sweep killed the anchor -- the driver
    # reported SKIPPED and the check silently stopped being demonstrated. A
    # perturbation anchored on data rots when the data does; anchor on the
    # structure instead.
    ("Y2 a script is declared that is not drifting", SSD,
     "EXPECTED_DRIFT = {",
     'EXPECTED_DRIFT = {\n    "trading-research/validation/detection_curve.py":\n'
     '        "PERTURBATION: declared but not drifting",'),
    ("Y3 drift is silenced entirely", SSD,
     "    changed = sorted(k for k in set(old) & set(now) if old[k] != now[k])",
     "    changed = []"),
    ("Y4 THE BASELINE IS RE-ANCHORED TO HEAD", SSD,
     "def load_baseline():\n"
     '    with open(BASELINE, encoding="utf-8") as fh:\n'
     "        return json.load(fh)",
     "def load_baseline():\n"
     '    with open(BASELINE, encoding="utf-8") as fh:\n'
     "        b = json.load(fh)\n"
     '    b["sweep_record_commit"] = _git("rev-parse", "HEAD").strip()\n'
     "    return b"),

    # --- 2026-08-07: Tasks 1-4 of the closing run ------------------------
    # Each breaks the THING the check protects, not the check's own wording.
    ("Z1 Fix A: --fast can write the canonical record again", SWEEP,
     "PARTIAL = bool(ONLY) or FAST",
     "PARTIAL = bool(ONLY)"),
    # Z2/Z3 PERTURB THE RECORD, NOT THE DETECTOR. The first version of both
    # blinded the check's own regex -- which makes the check PASS, so the driver
    # correctly reported them as never demonstrated. Breaking a detector proves
    # nothing; break the thing it protects. That is the "compute a value and
    # assert a different one" shape CLAUDE.md lists as known-vacuous, and it was
    # caught by the driver rather than by review, which is the driver working.
    ("Z2 Fix A: a SKIPPED row appears in the canonical record", REC,
     "| `validation/detection_curve.py` | REPRODUCES | byte-identical | 0.0 |",
     "| `validation/detection_curve.py` | SKIPPED | slow (--fast) | 0.0 |"),
    # REPOINTED 2026-08-13: the anchor carried the record's RUN DATE, so it died
    # the moment a new sweep landed -- an anchor guaranteed to rot on exactly the
    # event it exists to police. Re-anchored to the date-independent label so the
    # next sweep does not kill it again.
    ("Z3 Fix A: the record's header declares fast mode", REC,
     "**Run:** ",
     "**Run:**  (fast mode - slow scripts skipped) "),
    ("Z8 Fix A: the CONTROL -- everything diverts, so nothing is protected",
     SWEEP,
     "PARTIAL = bool(ONLY) or FAST",
     "PARTIAL = True"),
    ("Z9 Fix A: SWEEP_ONLY stops being diverted", SWEEP,
     "PARTIAL = bool(ONLY) or FAST",
     "PARTIAL = FAST"),
    ("Z4 Task 1: a live sweep banner returns to the handoff", HANDOFF,
     "## State of the record",
     "## A FULL SWEEP IS RUNNING - DO NOT TOUCH THE REPOSITORY\n\n"
     "## State of the record"),
    ("Z5 Task 1: the handoff reverts to the 2026-08-05 verdict counts",
     HANDOFF,
     "**66 REPRODUCES, 12 REPRODUCES\\*, 1 DIFFERS**",
     "**62 REPRODUCES, 16 REPRODUCES\\*, 1 DIFFERS**"),
    # Z10 exists because review F5 found the handoff check PARSING the EXCLUDED
    # count and never comparing it -- so the handoff could claim any number and
    # the check passed. Registered so the repaired comparison cannot rot back.
    ("Z10 Task 1: the handoff's EXCLUDED count is wrong", HANDOFF,
     "1 DIFFERS**, 7 EXCLUDED",
     "1 DIFFERS**, 99 EXCLUDED"),
    ("Z6 Task 4: verify_anchor stops checking WHICH commit", SSD,
     "    if stored_full != rec:",
     "    if False:"),
    ("Z7 Task 4: verify_anchor stops checking the hashes", SSD,
     '        if at_rec != base.get("hashes"):',
     "        if False:"),

    ("Q14 wrong momentum lookback", MCR,
     "def sig_mom121(close, lookback=252, skip=21):",
     "def sig_mom121(close, lookback=200, skip=21):"),

    # --- Task 2: the corrected companion rule (edits the TAGGED tree; the
    # driver restores byte-exactly and G3 verifies the tree afterwards) ---
    ("F1 companion-rule heading renamed", CLAUDE,
     "## Companion Rule: Long/Cash Strategies Need an Exposure-Matched Control",
     "## Companion Rule: Something Else Entirely"),
    # Single-line anchors only for CLAUDE.md: it has CRLF endings, so a
    # multi-line anchor written with "\n" never matches. That is how the first
    # version of F2 came back SKIPPED.
    ("F2 the false claim paraphrased away", CLAUDE,
     "> own average exposure, remainder in cash. **It differs from the strategy in",
     "> own average exposure, remainder in cash. **It was thought to help. Before"),
    ("F3 strikethrough removed", CLAUDE,
     "> ~~Use the **exposure-matched control**", "> Use the **exposure-matched control**"),
    ("F4 withdrawal marker removed", CLAUDE,
     "### ~~Use the exposure-matched control~~ — WITHDRAWN 2026-08-06",
     "### ~~Use the exposure-matched control~~ — note 2026-08-06"),
    ("F5 replacement control unnamed", CLAUDE,
     "**Use a timing-destroyed control instead:",
     "**Use some other control instead:"),
    ("F6 the null is allowed to be 50% again", CLAUDE,
     "2. **The skill-free null is NOT 50%.** A strict `>` counts every tie against the",
     "2. **The null needs no adjustment.** A strict `>` counts every tie against the"),
    ("F7 the binding-uncertainty sentence weakened", CLAUDE,
     "**The binding uncertainty is the WINDOW count, not the shuffle count.**",
     "**Uncertainty comes from several places.**"),
    ("F8 the real-record tie shares altered", CLAUDE,
     "**11.1% (3/27) for SMA200 and 40.7% (11/27) for Momentum 12-1**",
     "**a third of windows for both**"),

    # --- Task 3: the seven-cycle measurement ---
    ("T1 stop detecting exact ties", CYC,
     "    beat = int((ss > cs).sum())\n    tie = int((ss == cs).sum())",
     "    beat = int((ss > cs).sum())\n    tie = 0"),
    ("T2 daily/monthly walk-forward geometry drifts off legacy", CYC,
     "        en = st + pd.DateOffset(years=RFC.OOS_YEARS_LEGACY)",
     "        en = st + pd.DateOffset(years=RFC.OOS_YEARS_DEFAULT)"),
    ("T3 cross-asset walk-forward geometry drifts off legacy", CYC,
     "        en = st + pd.DateOffset(years=CATC.OOS_YEARS_LEGACY)",
     "        en = st + pd.DateOffset(years=CATC.OOS_YEARS_DEFAULT)"),
    ("T4 a non-power-of-two smuggled into the powers-of-two list", CYC,
     "POWERS_OF_TWO = [0.125, 0.25, 0.5, 2.0, 4.0, 8.0]",
     "POWERS_OF_TWO = [0.125, 0.25, 0.5, 2.0, 4.0, 0.3]"),
    # Additive, not multiplicative: an additive shift breaks Sharpe's
    # scale-invariance, so it moves the ZERO-TIE cycles too. A multiplicative
    # nudge cannot -- which is the whole finding, and is why the first version
    # of T5 was a no-op on five of seven cycles.
    ("T5 the control is nudged, so a null sweep is no longer null", CYC,
     "def score(cyc, strat, ctrl, d):",
     "def score(cyc, strat, ctrl, d):\n"
     "    ctrl = np.asarray(ctrl) + 1e-3"),
    # WIDEN, not narrow. near_1e3 already equals the exact-tie count on every
    # cycle -- that is the measurement -- so narrowing the threshold changes
    # nothing and demonstrated nothing.
    ("T6 near-tie thresholds widened until near-ties appear", CYC,
     "                near_1e3=int((np.abs(d) < 1e-3).sum()),",
     "                near_1e3=int((np.abs(d) < 2e-1).sum()),"),
    ("T8 exact ties detected by tolerance instead of equality", CYC,
     "    tie = int((ss == cs).sum())",
     "    tie = int((np.abs(ss - cs) < 2e-1).sum())"),
    # --- Task 6: the withdrawal must be marked in EVERY document that
    # published the prescription, or the gap named ---
    ("W1 the prescription is no longer findable", MSR,
     "buy-and-hold. ~~That control differs from the strategy in every window and has no",
     "buy-and-hold. ~~That control is unlike the strategy and has no"),
    ("W2 a surviving copy loses its withdrawal marker", MSR,
     "> **WITHDRAWN 2026-08-06.** The struck sentence is **false, and it was measured",
     "> **Note 2026-08-06.** The struck sentence is **false, and it was measured"),
    # W3 RETIRED 2026-08-07: it perturbed test_followups.py's own copy of
    # the debt registry, and that copy has been DELETED -- two registries
    # of one fact went stale the moment the census's copy changed. C3
    # covers the same check against the single remaining registry.
    # --- 2026-08-12 Task 1: the Phase 3 authorization claim ---
    ("PH1 a document re-asserts that Phase 3 was never granted", CS,
     "`docs/phase-gates.md`. **Phase 3 WAS granted**",
     "`docs/phase-gates.md`. Neither was ever granted. **Phase 3**"),
    # REPOINTED 2026-08-12, same day, because the first version DEMONSTRATED
    # NOTHING. It replaced ONE alternative of a three-way alternation, so the
    # pattern still matched its quoted occurrences and the anti-vacuity check
    # stayed green. A perturbation against an alternation must disable all of it.
    ("PH2 the claim pattern stops matching anything", TFU,
     'r"neither (was|has been) ever granted"\n'
     '    r"|neither was ever granted or requested"\n'
     '    r"|none\\s+was granted or requested", re.I)',
     'r"NOTHINGMATCHESTHISCLAIM"\n'
     '    r"|NOTHINGELSEEITHER"\n'
     '    r"|NORDOESTHIS", re.I)'),
    ("PH3 phase-gates.md stops recording the grant the correction cites", GATES,
     "**Implementation approval:** Phase 3 implementation approved",
     "**Implementation approval:** Phase 3 implementation pending"),

    # --- 2026-08-12 Task 3 / Fix D: a truncated run cannot become the record ---
    ("TD1 truncation detection is switched off entirely", SWEEP,
     '    return any(v in ABSENT_VERDICTS for _, v, _, _ in results)',
     "    return False"),
    ("TD2 truncation is decided by a THRESHOLD instead of by any", SWEEP,
     '    return any(v in ABSENT_VERDICTS for _, v, _, _ in results)',
     '    return sum(1 for _, v, _, _ in results if v == "NOT RUN") > 10'),
    ("TD3 every run is called truncated, so nothing can be the record", SWEEP,
     '    return any(v in ABSENT_VERDICTS for _, v, _, _ in results)',
     "    return True"),

    # --- 2026-08-12 Task 4 / Fix E: environment isolation ---
    ("FE1 a knob drops out of the scrub registry", SWEEP,
     '"OEZ_PERM", "P3_FIXED_PERMS",',
     '"OEZ_PERM",'),
    ("FE2 the knob scan stops finding anything", TFU,
     '            if isinstance(f, ast.Attribute) and f.attr == "get" and is_environ(f.value):',
     '            if False:'),
    ("FE3 a swept script reads the environment a way the scan cannot see", DC,
     "import os",
     "import os\n_UNSEEN = os.getenv('DC_HIDDEN', '0')"),
    ("FE4 child_env stops scrubbing and inherits everything", SWEEP,
     "    env = {k: v for k, v in os.environ.items() if k not in SCRUBBED}",
     "    env = dict(os.environ)"),
    ("FE5 child_env keeps ONLY the knobs and drops the platform", SWEEP,
     "    env = {k: v for k, v in os.environ.items() if k not in SCRUBBED}",
     "    env = {k: v for k, v in os.environ.items() if k in SCRUBBED}"),
    ("FE6 the deliberate knob stops being applied", SWEEP,
     "    if extra:\n        env.update(extra)",
     "    if False:\n        env.update(extra)"),
    ("FE7 a swept script is launched with an inherited environment", SWEEP,
     "                               timeout=TIMEOUT, env=child_env())",
     "                               timeout=TIMEOUT)"),
    ("FE8 a launch site becomes invisible to the AST walk", SWEEP,
     '            p = subprocess.run([PY, os.path.join("trading-research", rel)],',
     '            p = subprocess.run([sys.executable, os.path.join("trading-research", rel)],'),
    # --- 2026-08-12 adversarial review: the fixes for F1, F3, F5, F6, F7 ---
    ("TD4 the writer is reverted to the import-time constant (F7 restored)", SWEEP,
     '    out = os.path.join(BASE, "reports", report_name)',
     '    out = os.path.join(BASE, "reports", REPORT_NAME)'),
    ("TD7 main() builds a second, ambiguous report output path", SWEEP,
     '    out = os.path.join(BASE, "reports", report_name)',
     '    out = os.path.join(BASE, "reports", report_name)\n'
     '    out = os.path.join(BASE, "reports", REPORT_NAME)'),
    ("TD5 main() computes the destination inline instead of via the shared fn", SWEEP,
     "    report_name = report_destination(results)",
     "    report_name = PARTIAL_REPORT_NAME if PARTIAL else FULL_REPORT_NAME"),
    ("TD6 truncation narrows back to two of the five absent verdicts", SWEEP,
     '    return any(v in ABSENT_VERDICTS for _, v, _, _ in results)',
     '    return any(v in ("CONTAMINATED", "NOT RUN") for _, v, _, _ in results)'),
    ("FE9 a launch passes an INHERITED env instead of child_env", SWEEP,
     "                               timeout=TIMEOUT, env=child_env())",
     "                               timeout=TIMEOUT, env=dict(os.environ))"),
    ("FE10 a swept script gains a knob read with NO DEFAULT", DC,
     "import os",
     "import os\n_NODEFAULT = os.environ.get('DC_NODEFAULT')"),
    ("FE11 a swept script reads the environment under a DYNAMIC name", DC,
     "import os",
     "import os\n_DYN = os.environ.get(''.join(['DC','_DYN']), '0')"),
    ("FE12 a swept script reads the environment through an IMPORT ALIAS", DC,
     "import os",
     "from os import environ as _E\nimport os\n_ALIAS = _E.get('DC_ALIAS', '0')"),
    # --- 2026-08-13: the check total is computed, not transcribed ---
    # TT1 breaks the THING PROTECTED -- a document's stated total. TT2 and TT3
    # break the two anti-vacuity guards, which is the only way those can be
    # shown failing: what they protect against IS the scan finding nothing.
    ("TT1 a document states a check total the run does not produce", WUR,
     "= 548 automated checks**",
     "= 999 automated checks**"),
    ("TT2 the document scan stops finding any document", TFU,
     'DOCS_THAT_COUNT = ("writeup", "SESSION_HANDOFF.md", "trading-research/CLAUDE.md")',
     'DOCS_THAT_COUNT = ("nosuchdirectory_xyzzy",)'),
    ("TT3 a sibling suite's count becomes unreadable", TFU,
     '    r"ALL (\\d+) CHECKS PASSED|(\\d+) CHECK\\(S\\) FAILED, (\\d+) passed")',
     '    r"NOTHINGMATCHESTHISBANNER (\\d+)|(\\d+) NOPE, (\\d+) passed")'),
]

MUT = "tools/mutate.py"

# The driver's own self-test, audited by the driver. Each entry disables one
# guard and must make the check that demonstrates that guard fail. A driver
# that audits other code and not itself is the shape this project keeps
# catching.
DRIVER = [
    ("D1 restore in text mode instead of bytes", MUT,
     '    open(full, "wb").write(raw)\n    if open(full, "rb").read() != raw:',
     # The corruption is the CRLF->LF translation a TEXT-MODE READ performs.
     # `raw.decode()` does not translate, so a perturbation using it restores
     # correctly and demonstrates nothing -- the mistake this very guard exists
     # to catch, made once more in the perturbation itself.
     '    open(full, "w", encoding="utf-8", newline="").write(\n'
     '        raw.decode().replace("\\r\\n", "\\n"))\n'
     "    if False:"),

    # Must disable the WHOLE guard. Disabling only the first pass left the
    # widened second pass refusing everything, so the perturbation demonstrated
    # nothing -- a guard grew and its perturbation did not.
    ("D2 stop refusing mutating git verbs", MUT,
     "def refuse_if_mutating(name, old, new):                               # G2",
     "def refuse_if_mutating(name, old, new):                               # G2\n"
     "    return"),

    ("D3 stop comparing the working tree", MUT,
     "    if after != baseline:\n        raise DriverAbort(",
     "    if False:\n        raise DriverAbort("),

    ("D4 stop clearing bytecode", MUT,
     "                if d == \"__pycache__\":\n"
     "                    shutil.rmtree(os.path.join(dp, d), ignore_errors=True)\n"
     "                    n += 1",
     "                if False:\n"
     "                    shutil.rmtree(os.path.join(dp, d), ignore_errors=True)\n"
     "                    n += 1"),
]

SETS = {"driver": (f"{MUT} --self-test", DRIVER,
                   ["ops", "trading-research/followups",
                    "trading-research/validation", "trading-research/tests"]),
        "ops": ("ops/tests/test_ops.py", OPS,
                ["ops", "trading-research/followups",
                 "trading-research/validation", "trading-research/tests"]),
        "followups": ("trading-research/followups/test_followups.py", FOLLOWUPS,
                      ["ops", "trading-research/followups",
                       "trading-research/validation", "trading-research/tests"])}
