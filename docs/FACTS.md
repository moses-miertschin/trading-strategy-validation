# FACTS — the verified base for the write-up (2026-08-12)

**Nothing in `writeup/` may state a number that is not on this page.** Each entry
gives the artifact and, where the artifact is a file, the line. Anything I could
not trace is marked **UNSOURCED** and must not be used.

Commands shown were run read-only on 2026-08-12 at HEAD `3b2138e`.

---

## F1 — Scope: how many strategies

| Fact | Value | Source |
|---|---|---|
| Strategies researched | 16 | `reports/Closing_Statement_2026-08-05.md:24` |
| Strategies backtested | 17 | same line |
| Put through full walk-forward validation | **7** | same line; and 7 rows in `reports/Observed_Excess_Vs_Zero_2026-08-03.md:49-55` |
| Non-underscore `.py` in `backtest/strategies/` | 33 | `ls backtest/strategies/*.py \| grep -v "^_" \| wc -l` |

**Note.** 33 is a file count, not a strategy count — it includes grid sweeps,
batteries and report generators. **Do not write "33 strategies".** Use 16 / 17 / 7.

## F2 — The seven walk-forward cycles, and what each returned

Source for excess and interval: `reports/Observed_Excess_Vs_Zero_2026-08-03.md:49-55`
(1-year block length). Source for beat rate: `reports/Retroactive_Power_Audit_2026-07-31.md:49-53`
for the first five; `reports/Master_Strategy_Report.md:359` (XATSM7) and `:517` (XATSM8).
The gate is a walk-forward Sharpe beat rate **> 60%**.

| Strategy | Windows | Beat rate | Observed excess | 95% interval | Contains 0 |
|---|---|---|---|---|---|
| SMA200 (regime allocation) | 27 | 7.4% | **+0.0785** | [−0.1902, +0.3436] | yes |
| Momentum 12-1 | 27 | 14.8% | **+0.0960** | [−0.1486, +0.3643] | yes |
| Volatility-Targeted SPY | 28 | 25.0% | **+0.1224** | [−0.0307, +0.2689] | yes |
| Sector Rotation | 21 | 47.6% | **−0.0667** | [−0.2955, +0.1326] | yes |
| Inverse-Volatility Sector | 22 | 36.4% | **−0.0374** | [−0.1276, +0.0419] | yes |
| Cross-Asset TSM (7-asset) | 14 | 50.0% | **+0.1424** | [−0.2030, +0.4352] | yes |
| Cross-Asset TSM (8-asset) | 26 | 30.8% | **+0.1472** | [−0.1721, +0.4781] | yes |

- **Zero is inside all seven intervals.** Two excesses are negative.
- **None passed the 60% gate.** Highest beat rate is 50.0%.
- **Largest observed excess: +0.1472** (XATSM8).
- Intervals also computed at 0.5y and 2y block lengths; **all still contain zero**
  — `Observed_Excess_Vs_Zero_2026-08-03.md:68-...`.

## F3 — The detection curve on the real 8-asset universe

Source: `reports/Real_Universe_Detection_Curve_2026-08-03.md`. Protocol is the
unchanged three-gate Phase 3 protocol, LEGACY geometry, 200 draws per tier,
500 at the null (`:79-83`, `:87-95`).

| Quantity | Point | 95% interval | Line |
|---|---|---|---|
| Effect detected **80%** of the time | **0.2998** | [0.2821, 0.3170] | `:167` |
| Effect detected **50%** of the time | **0.1997** | [0.1849, 0.2174] | `:168` |
| Detection rate at **+0.1472** (XATSM8's own excess) | **0.2906** | [0.2213, 0.3611] | `:170` |
| Detection rate at **+0.1173** (mean positive excess) | **0.1838** | [0.1283, 0.2397] | `:169` |
| Zero-amplitude tier delivers | **−0.0928** | — | `:95` |

### F3a — THE PROMPT'S "0.32" IS A TIER LABEL, NOT THE CROSSING

The task prompt says *"the instrument resolves an edge at roughly 0.32 excess
Sharpe"*. **0.32 is the tier TARGET in the ladder** (`:93`); that tier's
**delivered** effect is **+0.3407** and its detection rate is **90.5%**.

**The 80% crossing is 0.2998, not 0.32.** Quoting the label would be the exact
defect this project documented six times — `CLAUDE.md`'s *"Tier rule: a LABEL is
not an EFFECT SIZE"*. **Write 0.2998, or "about 0.30".**

### F3b — Three caveats that must travel with any detection number

1. **The rung bracketing the numbers of interest is not separated.** Adjacent-rung
   separation on the delivered axis is 2.54σ between +0.1175 and +0.1421, against
   a Bonferroni z of 2.576 for a family of 5. **It does not clear it**, and that is
   precisely the pair bracketing +0.1173 and +0.1472. The 18.0% and 29.0% readings
   "rest on a rung pair that is not separated at Bonferroni". `:111-118`
2. **The 0% false-positive rate is one gate's property.** The walk-forward gate
   cannot fire at the null on 26 windows: a strict >60% needs 16/26 = 61.54% and
   500 null draws never exceeded 53.8%. The permutation gates fired 5/500 and
   9/500 and contributed nothing. `:136-148`
3. **The ladder's origin is not zero** (−0.0928 at zero amplitude), so any
   crossing quoted beside a real excess carries an offset. `:95`

## F4 — The reproducibility sweep

Source: `reports/Reproducibility_Sweep.md`, header lines and the verdict table
(counted by regex over `| \`script\` | VERDICT |` rows).

| Fact | Value |
|---|---|
| Run date | **2026-08-13** |
| Total runtime | **502.5 minutes** |
| Per-script timeout | 14400 s |
| Scripts in the table | **86** |
| EXCLUDED (network) | **7** |
| Runnable, all with a verdict | **79** |
| REPRODUCES (byte-identical) | **66** |
| REPRODUCES\* (timestamp/date only, every number identical) | **12** |
| DIFFERS | **1** — `power_engineering_study.py`, classified `NONDETERMINISTIC` |
| TIMEOUT / ERROR / CONTAMINATED / NOT RUN / SKIPPED | **0** |

### F4a — Two records now precede this one, and the split is stable

**The 2026-08-13 sweep re-ran everything after the harness was changed and
returned 66 / 12 / 1 / 7 — identical to 2026-08-07, script for script.** Only
the runtime and the run date moved. So the verdict split has now survived a
change to the verdict logic itself, which is a stronger statement than either
run alone supports.

### F4b — The Closing Statement quotes an EARLIER sweep

`Closing_Statement_2026-08-05.md:141-143` says *"62 byte-identical, 16
timestamp-only"*. That is the **2026-08-05** sweep. The current record is the
**2026-08-07** re-sweep: **66 / 12**. Both sum to 79. **Use 66 / 12 and cite the
2026-08-07 run.** Do not quote the closing statement's split as current.

## F5 — The four suites, run at HEAD 3b2138e on 2026-08-12

| Suite | Checks |
|---|---|
| `trading-research/tests/test_regression.py` | **340** |
| `ops/tests/test_ops.py` | **61** |
| `trading-research/followups/test_followups.py` | **116** |
| `tools/mutate.py --self-test` | **4** |
| **Total** | **548** |

All PASSED. `swept_script_drift.py` (N6): `anchor VERIFIED` at `10e5f8c`,
96 scripts, `CHANGED 0 ADDED 0 REMOVED 0`, exit 0.

**340 is pinned by the tag annotation** ("Regression suite: 340 checks"), which is
why later checks went to `test_followups.py` — `SESSION_HANDOFF.md:151-154`.

## F6 — Perturbations

`python tools/mutate.py --audit-anchors`, and `tools/perturbations.py::SETS`:

| Set | Suite it perturbs | Count |
|---|---|---|
| `driver` | `tools/mutate.py --self-test` | 4 |
| `ops` | `ops/tests/test_ops.py` | 43 |
| `followups` | `trading-research/followups/test_followups.py` | 74 |
| **Total registered anchors** | | **121** |

Audit at HEAD: **121 anchors, 0 dead, 1 ambiguous** (`T2`, pre-existing).

**Mutation coverage measured 2026-08-12:** ops **61/61** checks demonstrated
failing; followups **115/116** (the one gap, "MOM121: a financially-null control
DOES move it", is pre-existing and known since 2026-08-07); driver 4/4.
Source: `ops/Review_2026-08-12.md` §4 and the Task 3 commit `39f873f`.

**Not every one of the 548 checks has a perturbation.** 146 perturbations cover
the ops, followups and driver suites. **The 340-check regression suite is not in
any registered perturbation set.** Do not write "every check has a perturbation".
What is true: **every check added since the rule was adopted on 2026-08-03 was
demonstrated failing before it was committed**, and the rule is recorded in
`CLAUDE.md:400-416`.

## F7 — Adversarial review rounds

Each round: a reviewer briefed to **refute**, then every finding independently
re-verified before being accepted.

| Date | Subject | Findings | Confirmed | Rejected / cleared | Source |
|---|---|---|---|---|---|
| 2026-08-01 | Lever composition | 12 | 10 | **2 rejected** | `Lever_Composition_Adversarial_Review_2026-08-01.md:5,11-12` |
| 2026-08-02 | Test-statistic study | 16 | 16 (one "framing partly REJECTED") | 0 | `Test_Statistic_Adversarial_Review_2026-08-02.md:28-43` |
| 2026-08-02 | Calibration / sample requirement | — | all | **0** | `Sample_Requirement_Adversarial_Review_2026-08-02.md:41` |
| 2026-08-03 | The decisive measurement | **20** | 20 | **0** | `Best_Cell_Adversarial_Review_2026-08-03.md:8,42` |
| 2026-08-03 | Observed excess (2nd that day) | **11** | 11 | **0** | `Observed_Excess_Adversarial_Review_2026-08-03.md:12-13` |
| 2026-08-04 | Tasks 1–3 | **14** | 13 | **1 rejected** | `reports/Review_2026-08-04.md:1,7` |
| 2026-08-07 | Record restoration | **9** | 7 | **2 cleared**, 1 FATAL | `followups/Review_2026-08-07.md:3` |
| 2026-08-07 | Closing run | **8** | 8 | **0** | `followups/Review_2026-08-07_close.md:3-4` |
| 2026-08-12 | ops Tasks 0–2 | **16** | 16 | **0** | `ops/Review_2026-08-12.md:3-4` |

- **At least 9 review rounds.** The Lever Composition round's 12 break down as
  6 confirmed by direct computation, 3 confirmed-but-smaller, 1 cosmetic,
  2 rejected (`:11-12`).
- The 2026-08-02 calibration round's **finding count is UNSOURCED** — the document
  states "nothing was rejected" without a headline count. **Do not give it a
  number.**
- **Reviews repeatedly overturned same-day work.** Findings concerning work done
  that same day: 3 of 7 on 2026-08-06, 4 of 8 on 2026-08-07, **12 of 16 on
  2026-08-12** — `SESSION_HANDOFF.md:77-81`.

## F8 — Withdrawn claims

`python trading-research/followups/withdrawal_census.py`, run 2026-08-12:

| Fact | Value |
|---|---|
| Struck claims censused (marker + followable struck span) | **25** |
| Signature-level gaps | **1** |
| Distinct documents with a gap | **1** — `reports/Power_Engineering_Study_2026-07-31.md`, a **declared debt** |
| Withdrawal markers in the corpus | **99** |
| Markers the census cannot follow to a struck span | **63** |

`test_regression.py::WITHDRAWN_CLAIMS` pins **5** specific claim/document pairs
that must carry a withdrawal marker in place (N5) — `tests/test_regression.py:1158-1164`.

**Careful phrasing required.** 99 is a count of *markers*, not of distinct
withdrawn claims; 25 is the number the census can verify structurally; 63 are
markers in a form it cannot follow. **Write "the census verifies 25 struck claims
and counts 99 withdrawal markers it cannot all follow", not "99 claims were
withdrawn".**

## F9 — The tagging conditions

Six, all HOLD at HEAD (`SESSION_HANDOFF.md:169-183`; verified 2026-08-12):

| | Condition |
|---|---|
| N1 | every `.py` in the swept directories is covered by the sweep |
| N2 | no absent verdicts |
| N3 | every DIFFERS carries a written, classified cause |
| N4 | the record was produced by this tree's verdict logic (fingerprint `5f1d86106dca75dd`) |
| N5 | withdrawn claims marked in place |
| N6 | no swept script has drifted since the record (baseline `10e5f8c`, 96 scripts) |

**They were rewritten.** The conditions "as rewritten on 2026-08-04" are named in
the tag annotation itself (`git tag -n99 project-capstone-2026-08-03`). N6 was
added 2026-08-06 (`SESSION_HANDOFF.md:332-333` refers to it as added then).

**SOURCED 2026-08-12, during Task 3 — this was marked UNSOURCED and is not.**
`reports/Tagging_Conditions_2026-08-04.md:3-8` states the motivation verbatim:

> *"The five conditions on this project's record were written to answer **"did the
> sweep finish?"**. It has finished. They do not answer the question that matters
> now, which is **"is the sweep's verdict trustworthy?"**"*

The commit that made the change is `18d1f72`, *"Task 5: the five tagging
conditions rewritten to ask whether the verdict is trustworthy"*.

**The concrete defect that drove it**, same document, N4's row: *"13 `REPRODUCES*`
verdicts were produced by a keyword filter and then quoted as though produced by a
numeric one. Nothing checked that the record and the checker were the same
generation."* The opening paragraph gives the same figure as *"13 of 77 verdicts
rested on a filter that never checked a number"*.

**Also usable, same table:** old condition 1 required that the report *"has been
read by a human"*, dropped because *"'Read by a human' is not checkable from
committed evidence — it is a claim about someone's attention."*

## F10 — Named defects available as concrete examples

Each is a specific, quotable defect with an artifact.

| # | Defect | Source |
|---|---|---|
| D1 | A regex pattern beginning with a literal **backspace byte** matched nothing, passed vacuously, and carried a failure message describing a real defect. One of **five** checks written 2026-08-02 that could not fail; all five found by adversarial review, none by the suite. | `CLAUDE.md:400-434` |
| D2 | A look-ahead bug in one of four copy-pasted sector scripts inflated Sharpe from a corrected **0.46 to 1.11**. | `CLAUDE.md:61-67`, `:121-125` |
| D3 | `pipeline_detection_floor.py` — the published record of the 0.90 floor — **could not run at all** for **five days**; it inherited a moved default, measured 13 windows instead of 14, and its own assertion aborted every run. | `CLAUDE.md:171-181` |
| D4 | The sweep's CONTAMINATED path `continue`d **without restoring**, so a later script came back **byte-identical** against a dirty tree — "a false clean bill of health". | `CLAUDE.md:568-584` |
| D5 | `git()` swallowed the return code: a transient failure made `head()` return `""` (false CONTAMINATED) and `dirty()` return `[]` (false REPRODUCES). **A broken command produced the best possible verdict.** | `CLAUDE.md:586-593` |
| D6 | The mutation driver damaged the repository **three times**, "and every time it was `git status` that noticed, not the driver": a leaked fixture, a stale `.pyc`, and a **text-mode restore that rewrote a file inside the tagged tree** while reporting `restored=True`. In the same session a perturbation containing a live `git commit` **executed**. | `tools/mutate.py:3-17` |
| D7 | `record_commit()` used `git log -1 -- RECORD`, which returns the commit that most recently **touched** the path **including a deletion** — so N6 printed `anchor VERIFIED` about a commit where the record does not exist. "The word *touched* stood in for *carries*." | `followups/Review_2026-08-07_close.md:14-33` |
| D8 | A claim that re-anchoring "requires FORGING THE RECORD ITSELF" was measured and **the real cost was one blank line**. | `followups/Review_2026-08-07_close.md:57-86` |
| D9 | A handoff check parsed **four** verdict counts and asserted **three**; the handoff could claim `99 EXCLUDED` and pass. | `followups/Review_2026-08-07_close.md:36-44` |
| D10 | `--generate HEAD` stored the literal string `"HEAD"`, so the anchor silently re-resolved on every run while still printing `anchor VERIFIED`. | `followups/Review_2026-08-07_close.md:46-52` |
| D11 | A 35-point grid maximum (40.7%) was written up as what a null control *reaches*; the derived ceiling is **55.6%** and a 4,000-draw random search attained **51.9%**. The correct bound had been derived and then **retracted for not being a measurement**. | `CLAUDE.md:668-702` |
| D12 | On 2026-08-12 a regression check was written in the morning pinned to a biased sample and **would have failed the same afternoon** when the scheduled capture landed. | `ops/Review_2026-08-12.md` F2 |
| D13 | An irreversible capture was triggered by `python ops/daily.py --help`; `daily.py` parses no arguments. **The handoff listed that command as the first thing a returning reader should run.** | `ops/Orientation_2026-08-12.md` §0; `SESSION_HANDOFF.md:9-31` |
| D14 | A check `test_log_covers_every_snapshot` was **inert for the one date that went wrong**, because an orphan `run_end` pre-vouched it. | `ops/Review_2026-08-12.md` F14 |

### F10a — D1's sibling, needed for Task 4's "isfile(x) == isfile(x)" example

The prompt asks for a check that asserted `isfile(x) == isfile(x)`. The real
artifact says:

> *"A separate 'the log gained no test rows' check was written here and DELETED
> rather than repaired — it read `os.path.isfile(real_log) == os.path.isfile(real_log)`,
> which is true by definition and is the first known-vacuous shape in
> trading-research/CLAUDE.md. A redundant check is not worth repairing."*

Source: `ops/tests/test_ops.py`, comment above the "not one byte under ops/
changed" check. **This is verbatim and usable.**

A second deletion, from today: a check asserting a partition is disjoint and
covering was deleted before commit as true-by-definition — `ops/tests/test_ops.py`
(comment in `test_interior_holes_are_not_window_slide`), commit `39f873f`.

## F11 — Phase gates

- Phases require a **written approval note in `docs/phase-gates.md`** before
  moving forward — `CLAUDE.md:27-31`.
- **No strategy ever advanced past Phase 3** — `Closing_Statement_2026-08-05.md:10`.
- **Phase 3 WAS authorized in writing, four times on dated approvals**:
  2026-07-05 (`docs/phase-gates.md:94`), 2026-07-06 (`:266`), 2026-07-30
  (`:719,725`, quoting the owner's brief verbatim) and a **conditional**
  authorization of 2026-07-30/31 (`:973`). There are **nine** `## Phase 3`
  sections in that file; the other five record results and closures under those
  grants.
- **Phase 4 was never granted, never requested and never reached.** The
  `## Phase 4` section (`:1502`) says *"Gate requires: Phase 4 approval written
  above"* and no approval is written; every closed cycle records Phase 4
  eligibility as `BLOCKED`.

  > **CORRECTED 2026-08-12.** This entry previously cited
  > `Closing_Statement:165-168`'s *"neither was ever granted"* as a fact. **It is
  > false for Phase 3.** The source has been corrected in place (Task 1). **The
  > prompt authorizing that correction said "six dated Phase 3 authorizations";
  > the count I can defend from explicit granting lines is FOUR**, and the
  > distinction is exactly the kind this project exists to make.
- No broker, wallet, exchange, API-key, order-execution, paper-trading or
  live-trading code has ever existed in the repository — `Closing_Statement_2026-08-05.md:6-11`.

## F12 — What could not be determined

Three, from `Closing_Statement_2026-08-05.md:83-132`:

1. **Whether the effects were real but unresolvable, or never there.** All seven
   intervals contain zero; upper bounds reach **+0.52**. Needs more history, and
   more history does not exist — 31 years of monthly data on 8 assets is the
   sample. `:88-99`
2. **Whether a detection curve's slope transfers between universes.** Resolution
   ≈ **±0.084**; every level's difference contains zero. Dominant uncertainty is
   *path* variance, which more draws cannot reduce. Now moot. `:103-116`
3. **Whether the three-gate protocol is three-gate at 26 windows.** See F3b(2).
   A window-count effect; the window count is fixed by the data. `:118-132`

## F13 — Compute cost

- *"Roughly thirty hours of measured compute, and more than half the artifacts in
  the repository"* went into measuring the protocol rather than the strategies —
  `Closing_Statement_2026-08-05.md:56-58`.
- The 2026-08-13 sweep: **502.5 minutes** (~8.4 h) — F4. The 2026-08-07 run before it took 467.8 min (~7.8 h) and returned **identical verdicts**.

---

## UNSOURCED — must not appear in the write-up unless sourced in Task 5

| Claim | Why it is not usable |
|---|---|
| "the instrument resolves an edge at roughly **0.32**" | 0.32 is a tier label. The crossing is **0.2998** [0.2821, 0.3170]. See F3a. |
| A total count of findings across all review rounds | One round has no headline count (F7). A total would be a floor, not a total. **Write "at least 9 rounds" and give the per-round numbers.** |
| "every check is demonstrated failing under a perturbation" | 142 perturbations do not cover the 340-check regression suite. See F6 for the true statement. |
| "99 claims were withdrawn" | 99 is a marker count. See F8. |
| Number of hours of human time spent | Nowhere in the record. |
| Any statement that a strategy "works", "shows promise", or "was profitable" | Contradicted by F2. |
