# Verdict — 2026-08-12, sweep-fix run

**Committed before anything launches.**

**Safety unchanged.** No broker, API key, `.env`, order execution, paper trading,
live trading, leverage, futures, options, crypto, smart contract or copy-trading.
`yfinance` read-only. No strategy advanced a phase; this run granted no Phase 3 or
Phase 4 authorization and re-decided no verdict. All commits local; nothing
pushed. The tag was not created, moved or evaluated. The school vault was never
touched.

---

## 1. Which conditions fail, and why

| | Condition | State |
|---|---|---|
| N1 | every `.py` in the swept directories is covered | HOLDS |
| N2 | no absent verdicts | HOLDS |
| N3 | every DIFFERS carries a written, classified cause | HOLDS |
| N4 | the record was produced by this tree's verdict logic | **FAILS** |
| N5 | withdrawn claims marked in place | HOLDS |
| N6 | no swept script has drifted since the record | HOLDS |

**Exactly one condition fails, and it is N4.**

```
5f1d86106dca75dd   the fingerprint the committed record was produced under
2172b8021628bc92   after Fix D
0acf168e73b106c9   after Fix E
7184ba717ea362ba   after the adversarial-review fixes   <- this tree
```

`test_regression.py` reports **339 passed, 1 failed**. That single failure is N4
saying, correctly, that the committed record was made by an older harness.
`VERDICT_LOGIC_FINGERPRINT` was deliberately **not** updated: doing so would make
the check green by telling it to expect what it found, which is precisely the
re-anchoring N4 exists to catch.

### N6 is NOT firing, and the prompt's premise on this is wrong for the third time

The authorizing prompt said Tasks 3 and 4 would "move the fingerprint, **fire
N6**, and leave the record not describing this tree". Two of the three are right.

**N6 does not fire and cannot.** N6 tracks drift in *swept scripts*, and
`SWEPT_DIRS = ("validation", "backtest/strategies", "data")`. The sweep harness
lives in `trading-research/tests/`, which is outside it. `swept_script_drift.py`
reports `anchor VERIFIED`, 96 in baseline, 96 in tree, `CHANGED 0 ADDED 0
REMOVED 0`, exit 0 — verified after every commit today.

**The mechanism working is N4 firing, not N6.** They answer different questions:
N6 asks "did a measured thing change?", N4 asks "did the *measuring apparatus*
change?". Today only the apparatus changed, so only N4 objects. If N6 had fired
it would mean something worse — that a fix to the sweep had reached into the
scripts the sweep measures.

## 2. What the pending sweep must return for the record to be whole

The launched run must produce `reports/Reproducibility_Sweep.md` — **the canonical
name, not `_partial`** — containing:

1. **A verdict for every runnable script.** Zero `TIMEOUT`, `ERROR`,
   `CONTAMINATED`, `NOT RUN`, `SKIPPED`. **This is now enforced twice**: N2
   detects such a record afterwards, and as of Fix D the sweep will not write the
   canonical name at all if any of the five appears. If the report lands under
   `Reproducibility_Sweep_partial.md`, the run failed and the old record survives
   untouched — which is the intended behaviour, not an error to work around.
2. **Coverage of 86 scripts, 7 EXCLUDED, 79 runnable**, unless the partition
   changed — it has not; `partition_gaps()` returns `([], [], [])`.
3. **`power_engineering_study.py` DIFFERS**, with its `NONDETERMINISTIC` cause.
   It seeds from a per-process hash and cannot reproduce itself. **A run in which
   it does NOT differ would be the surprising result** and would need explaining
   before the record is trusted.
4. **Ideally nothing else differing.** A second DIFFERS is not automatically a
   defect in the sweep — see §3 — but it is not automatically fine either, and
   N3 will fail until someone writes down its cause.

**Then, and only then:** update `VERDICT_LOGIC_FINGERPRINT` to the tree's value,
re-run the four suites, and re-verify all six conditions. **Not before.**

## 3. Whether Fix E can change a verdict, stated precisely

Fix E removes 52 project knobs plus `PYTHONHASHSEED` from the environment every
swept script runs in. Before it, they inherited the operator's shell.

**In the shell this sweep was launched from, no scrubbed name was set** — checked
immediately before launch, not inferred from an earlier measurement. So
`child_env()` returned an environment equal to the parent's and every script ran
exactly as it would have before the fix. **On that basis I do not expect any
verdict to change, and if one does the cause is not Fix E.**

**One caveat, and it is specific.** `DIFFERS_EXPLAINED` records that
`power_engineering_study.py`'s floors *"change on every run unless
`PYTHONHASHSEED` is pinned, and neither script pins it."* If a future sweep is
launched from a shell that **does** pin `PYTHONHASHSEED`, Fix E will strip it and
that script will be nondeterministic where it would otherwise have been
reproducible. That is Fix E working as designed — the record must describe a run
with no environment flags set — but it means **the launching shell is now part of
the protocol and must be checked, not assumed.**

## 4. Every figure in `writeup/` that depends on the sweep record

**This is the thing most at risk of becoming a claim that outlives its evidence,
and `writeup/` is the worst possible place for one.** Every figure below is
**pinned to the 2026-08-07 record** and may be superseded the moment the pending
sweep lands.

| Figure | Where |
|---|---|
| 86 scripts / 7 EXCLUDED / 79 runnable | `README.md:100-102`, `ENGINEERING.md:120-121`, `FACTS.md` F4, `PROVENANCE.md` row 18 |
| **66** byte-identical | same |
| **12** timestamp-only (`REPRODUCES*`) | same |
| **1** DIFFERS, `power_engineering_study.py`, `NONDETERMINISTIC` | same, plus `ENGINEERING.md:126-129` |
| Zero TIMEOUT / ERROR | `ENGINEERING.md:122` |
| **467.8 minutes** / "a 7.8-hour run" | `README.md:103`, `ENGINEERING.md:123`, `FACTS.md:92,317`, `PROVENANCE.md` rows 18 and 42 |
| "the 7.8-hour sweep" as the cost of a re-run | `ENGINEERING.md:249,268` |
| "14 published floors would move" | `ENGINEERING.md:126-129` — depends on the DIFFERS staying nondeterministic |

**Not affected**, and worth separating so a future reader does not over-correct:
the seven-cycle table, the detection-curve figures, the strategy counts, the
phase-gate facts and the suite counts. **None of those comes from the sweep
record.** The research finding does not move if the sweep result does.

`writeup/PROVENANCE.md` now carries a section recording that each of these is
pinned to the pre-fix record and must be re-verified once the sweep completes.

## 5. What changed today, and the honest shape of it

Five defects fixed — the false Phase 3 claim in four documents, Fix D, Fix E, and
the two FATAL review findings against Fix D and the fingerprint duplication — plus
a third prose pass and 24 new checks.

**Every one of the 15 review findings was about work committed earlier the same
day.** The two FATAL ones share a shape: **a check that reimplements the thing it
protects will pass when that thing is removed.** Fix D's five checks copied the
destination rule instead of calling it, and F7 restored verbatim left them all
green. The fingerprint had three implementations, one of which could never detect
its own drift because its assertion was relative.

**The self-audit trend across four runs is now 3 of 7, 4 of 8, 12 of 16, and 15 of
15.** The handoff already names improving the checking apparatus as the trap. This
run was authorized to touch the apparatus and it produced the highest
same-session defect rate yet. That is not an argument that the work was wrong —
F8 was a false claim in the record the tag certifies, and it needed fixing — but
it is a measurement, and the measurement says the next session should not go
looking for more apparatus work.

**What I would not claim.** That the fixes are correct. They are demonstrated
failing under 143 perturbations and re-verified against 15 adversarial findings,
and the last two rounds each found something FATAL in the previous round's work.
A sixteenth finding is more likely than not.

*Nothing in this document is evidence about any strategy's edge.*
