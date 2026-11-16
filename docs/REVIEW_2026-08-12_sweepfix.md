# Adversarial Review of Tasks 2, 3 and 4 — 2026-08-12 (sweep-fix run)

**15 findings from a refutation subagent. I re-verified all 15 independently and
confirmed all 15 — none rejected. 2 FATAL, 7 MAJOR, 6 MINOR.**

**Both FATAL findings are about work committed earlier the same day, and both are
the same shape: a fix that was real and a demonstration that was against a copy
of it.**

Everything is fixed here except where noted. The subagent was briefed read-only
and told not to run `ops/daily.py`, `ops/capture.py` or the sweep; it ran none.

---

## 1. The two FATAL findings

### F1 — Fix D was protected by nothing. Reverting it left every check green.

Task 3 added five checks "demonstrating" that a `CONTAMINATED` abort cannot write
the canonical record. **They never execute `main()`.** Each builds its own

```python
def name_for(results):
    partial = RS.PARTIAL or RS.truncated(results)
    return RS.PARTIAL_REPORT_NAME if partial else RS.FULL_REPORT_NAME
```

which is a **copy** of the three lines inside `main()`, not a call into them. Fix
D's actual value is `main()` handing that name to the writer. The reviewer
restored F7 verbatim — `out = os.path.join(BASE, "reports", REPORT_NAME)` — and
**all five Task-3 checks plus all six Fix A/C checks stayed green.**

Re-verified: `REPORT_NAME` now survives only in a `print()` at line 824 and in
comments. The three perturbations TD1–TD3 all perturb `truncated()`, the one
function the checks call directly, so the demonstration was against the shared
helper rather than against the fix.

**Fixed** by extracting `report_destination(results)` — one function, called by
`main()` and by the checks — and adding `test_fix_d_destination_is_not_bypassed`,
which walks `main()`'s AST and requires the writer's argument to be the computed
`report_name` and requires `main()` to obtain it from `report_destination`.
Demonstrated by TD4 (writer reverted) and TD5 (destination inlined).

### F2 — There was a THIRD fingerprint implementation, already diverged.

Task 5 found one diverged copy of the N4 fingerprint and reported it fixed:
*"Both implementations now return `0acf168e73b106c9`."* **There were three.** The
third is a subprocess source string inside `test_n4_covers_the_timeout`, about
300 lines above the fix. Its function list was picked up by the de-duplication;
its **constants** list was hand-copied and never gained `repr(sorted(RS.SCRUBBED))`,
the term Fix E had added to both other copies hours earlier. It computed
`627331a97490e2b2`.

**It could never have detected its own drift**, because its assertion is
*relative*: `fp("3600") != fp(None)`. It stays green at any absolute value.

**Fixed**: the third implementation now includes the same term. The deeper
lesson is recorded rather than solved — three copies existed because each was
written to avoid a cost the previous one had, and a relative assertion cannot
anchor an absolute value.

## 2. MAJOR, all fixed

| | Finding | What was wrong | Fix |
|---|---|---|---|
| **F3** | `truncated()` covered **2 of the project's own 5** absent-verdict classes | A default-cap run producing **TIMEOUTs — the exact 2026-08-02 damage** — still wrote the canonical record. Fix C only diverts a non-default *cap*, not a timeout *at* the default | `ABSENT_VERDICTS` = the same five-set N2 and `test_regression.py` use; all five now divert, `DIFFERS` correctly does not |
| **F4** | The report sentence rendered `{len(SCRUBBED)}` = **53** "project knobs plus `PYTHONHASHSEED`" | Asserts 54 removals where there are 53, and calls `PYTHONHASHSEED` one of the 53 while separately adding it — contradicting the comment 790 lines above | `{len(PROJECT_KNOBS)}` = 52 |
| **F5** | The launch check asserted the keyword **name**, not its value | `env=dict(os.environ)` — the literal pre-Fix-E behaviour — passed it. The check was exactly as wide as the one perturbation that removed `env=` | Asserts the value is a call to `child_env`; the pipeline call was inlined so the AST can read it |
| **F6** | The knob scan was a regex requiring the literal token `os.` | `from os import environ`, `import os as o` and `from os import getenv` **all escaped both the scan and the "any other way" guard** | Rebuilt on AST with import-alias resolution |
| **F7** | *"Every read has a default, so a scrub structurally cannot crash a script"* was true and **unpoliced** | The scan admitted a one-argument `.get("KNOB")`, scrubbed it, and would hand `None` to the `int(...)` every such read wraps | The scan now requires a default and fails on a defaultless read |
| **F8** | `SESSION_HANDOFF.md` contradicted itself in five places | N4 recorded as both HOLDS and FAILS; the check-first list promising "nothing is wrong" against a suite that exits 1; **F7 and F8 still listed as open** hours after being fixed; "a full sweep is running" when none was; "15 verdict-deciding functions" when there are 17 | All five corrected |
| **F9** | Tasks 3–5 invalidated **seven counts in `writeup/`** that Task 2 had verified hours earlier | 521 → 546, 116 → 141, 121 → 142, "115 of 116" → "140 of 141", "180 of 181" → "205 of 206", 15 → 17, and **"all passing" is false while N4 is deliberately red** | All corrected, and the red check is now explained in `ENGINEERING.md` rather than hidden |

## 3. MINOR, all fixed or recorded

- **F10** — the three "count independence" cases exercise **one disjunct three
  times**: every abort appends a `CONTAMINATED` row before the `NOT RUN` rows, so
  no reachable `results` has `NOT RUN` without it, and `truncated()`'s `NOT RUN`
  arm was dead code. **The genuinely different case was F3's**, and there are now
  three checks for it.
- **F11 — the counting pass published an uncounted count.** Task 2 reported
  *"10 findings, 10 verbs/quantifiers, 0 numbers"* and *"26 of 27"*. Its own
  table classifies R8's class as **disclosure**, which is neither a verb nor a
  quantifier. Corrected below and in `PROVENANCE.md`.
- **F12** — the report's blanket *"no environment flags set"* was false for the
  pipeline replay, which is deliberately given `REFINE_REPORT_ONLY=1`. The
  sentence now names the exception.
- **F13** — the knob scan never looked at `backtest/engine/`, which
  `spy_200_sma_backtest.py` runs as a grandchild. Isolation itself survived (the
  grandchild inherits the already-scrubbed environment); the *police* did not
  cover it. Domain widened.
- **F14** — the new banner degenerated to *"0 later script(s) were never run…
  those 0, however few they are"* in exactly the abort-on-the-last-script case
  Fix D calls its most important demonstration. Reworded to count absent
  verdicts.
- **F15** — *"child_env is byte-identical right now, so no verdict will change"*
  measured the right thing and drew too broad a conclusion: it licenses a claim
  about a **future** process from a snapshot of this shell. And the concrete
  counterexample is real — `DIFFERS_EXPLAINED` records that
  `power_engineering_study.py`'s floors *"change on every run unless
  `PYTHONHASHSEED` is pinned"*, so a launcher that pins it would have that
  verdict changed **by Fix E**. Restated, and the launch re-checks the shell.

## 4. The corrected prose-pass count (F11)

| pass | findings | verb | quantifier | attribution | **disclosure** | number |
|---|---|---|---|---|---|---|
| provenance (figures) | 4 | — | 1 | — | — | **3** |
| overclaim, first | 17 | | | | | 1 |
| overclaim, second | 10 | 3 | 5 | 1 | **1** | **0** |

**Corrected statement: "10 findings — 3 verbs, 5 quantifiers, 1 attribution, 1
disclosure, 0 numbers. Across the two prose passes, 25 of 27 were verbs,
quantifiers or attribution, and 26 of 27 were not numbers."**

The "0 numbers" framing survives. The "all ten" framing does not, and a pass whose
own rule is *"for every 'every', 'each', 'all': count it"* publishing an uncounted
"all ten" is the finding holding itself to its own standard.

## 5. What survived

The subagent's own list of what it attacked and could not break is worth keeping,
because several were its best shots:

- **"52 knobs, 44 in SWEPT_DIRS"** — exact, verified by an independent AST walk in
  both directions: no stale registry entry, no missing one.
- **The transitive import closure.** It resolved every import of all 86 swept
  candidates — 96 modules — and **every one lands inside `SWEPT_DIRS`**. This was
  its best hope for a clean isolation kill and it failed.
- **The grandchild inherits the scrubbed environment**, so isolation is transitive.
- **The banner cannot be emitted with an empty reason list** — every disjunct of
  `partial_run` contributes one.
- **`PARTIAL` and `report_name` can only disagree in the safe direction**, because
  `partial_run` is a strict widening.
- **A crash or kill before the writer is not an evasion** — nothing is written and
  the previous record survives.
- **Editing the sweep harness does not fire N6**, verified two ways. Task 0's
  premise correction was right.
- **`VERDICT_LOGIC_FINGERPRINT` deliberately not updated** — correct, and the
  reasoning holds.

## 6. Score

| Error class | Findings | Confirmed | Rejected |
|---|---|---|---|
| E1 — an isolation claim outrunning its implementation | 5 | 5 | 0 |
| E2 — a guard as wide as its evasions | 3 | 3 | 0 |
| E3 — a fix demonstrated only on its motivating case | 4 | 4 | 0 |
| E4 — a verb stronger than its evidence | 3 | 3 | 0 |
| **Total** | **15** | **15** | **0** |

**Every finding concerned work committed earlier the same day.** The two FATAL
ones share a shape worth naming: **a check that reimplements the thing it
protects will pass when that thing is removed.** It happened twice in one day, in
two different subsystems, written by someone who had just spent a session writing
about exactly this class.

*Nothing here is evidence about any strategy's edge.*
