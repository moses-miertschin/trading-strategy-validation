# PROVENANCE — every claim in the write-up, checked

**Every number and every quotation** in `README.md`, `ENGINEERING.md` and
`WHAT_WENT_WRONG.md`, its source, and whether it verified. **Claims that did not
verify were changed in the document, not footnoted here.**

**84 claims checked in the first pass (80 rows + P-A…P-D). 80 verified as written.
4 did not and were fixed or cut.** A second pass — the overclaim review in §Q —
found **17 more**, and a third pass found **10 more**. **Corrected 2026-08-12
by adversarial review (F11): the third pass reported "10 of 10 verbs or
quantifiers" when its own table classifies R8 as *disclosure*.** The honest split
is 3 verbs, 5 quantifiers, 1 attribution, 1 disclosure, **0 numbers** — so 9 of 10
are verbs/quantifiers/attribution and 25 of 27 across the two prose passes, while
26 of 27 were not numbers. A pass whose own rule is "count every 'every'"
published an uncounted "all ten".

> **CORRECTED 2026-08-12.** This line read *"58 claims checked. 54 verified."*
> **The table has 80 numbered rows.** 58 was the count before the 22
> WHAT_WENT_WRONG rows were appended and I never re-counted. It understates rather
> than overstates, which is why it survived — but a headline number in the
> accountability document that fails a ten-second count is exactly the thing this
> document exists to prevent. The stale figure is also in commit `df01c6f`'s
> subject line, where it cannot be corrected without rewriting history.

> **AND THE COMPLETENESS CLAIM WAS TOO BROAD.** This said *"each substantive
> claim"*. It was not true: the first pass checked **figures and quotations
> thoroughly and verbs and quantifiers not at all** — "caught", "held", "every",
> "each", "entire". Sixteen of the seventeen findings in the overclaim review live
> in exactly those words. Narrowed above, and §Q covers what the first pass missed.

Verification was done at HEAD `3b2138e` on 2026-08-12 by re-reading the artifact,
re-running the command, or recomputing the arithmetic — not by consulting
`FACTS.md`, which is itself a derived document.

---

## Did not verify — changed in the document

### P-A — "missed four times in five" — **WRONG, corrected**

`README.md` said an edge the size of the largest observed *"would have been missed
four times in five."*

**Recomputed:** detection at +0.1472 is **0.2906**, so the miss rate is **70.94%**
— about **seven times in ten**. "Four times in five" is 80% missed, which
corresponds to 20% detection, a level this curve never reports.

**Where the wrong number came from, which is the instructive part.** The Closing
Statement describes XATSM8's interval as *"consistent with… one it should have
caught four times in five"* — that phrase refers to the **80% detection crossing
at the interval's upper bound**, not to the observed point estimate. I attached a
figure about the top of the interval to the middle of it.

**Corrected to** "missed about seven times in ten."

### P-B — "N4 caught a defect of mine on the day it was introduced" — **MISATTRIBUTED, rewritten**

`ENGINEERING.md` said N4 caught a defect when *"a stray environment variable in my
shell changed the fingerprint input and the check went red on an otherwise
untouched tree."*

**That is not N4 catching a defect. It is a defect in N4** — recorded as finding
F4 of the 2026-08-07 closing review, still open. Framing an open false-alarm bug
as a success is exactly the overclaim this write-up is supposed to avoid.

**There is a real "the fingerprint caught its own defect" story**, verified in
`tests/test_regression.py:1126-1130`: the first version hashed sets directly, and
`repr()` of a set iterates in CPython's per-process randomised hash order, so the
fingerprint **differed between runs on an unchanged tree**.

**Rewritten** to tell that story, and the environment-variable issue is now stated
where it belongs — as a known open limitation, with the note that it fails in the
safe direction.

### P-C — "the tagging conditions were rewritten because they asked *did the sweep finish*" — **was UNSOURCED, now sourced**

Marked UNSOURCED in `FACTS.md` F9 during Task 1, because I had the fact of the
rewrite and its date but no document stating the motivation.

**Sourced during Task 3**: `reports/Tagging_Conditions_2026-08-04.md:3-8` states it
verbatim, and commit `18d1f72` carries the same wording in its subject line.
`FACTS.md` F9 was updated and the UNSOURCED row removed. **Usable, and used.**

### P-D — "0.32 excess Sharpe" — **cut before it was ever written**

The task prompt asked for the constraint to be stated as *"roughly 0.32 excess
Sharpe"*. **0.32 is the tier TARGET in the ladder**
(`Real_Universe_Detection_Curve_2026-08-03.md:93`); that tier's **delivered**
effect is +0.3407 at a 90.5% detection rate. The measured 80% crossing is
**0.2998**, interval [0.2821, 0.3170].

Quoting 0.32 would have been this project's own documented "a LABEL is not an
EFFECT SIZE" defect, of which `CLAUDE.md` records six instances. **Never entered
any document**; the write-up says 0.2998 / "about 0.30" throughout.

---

## Verified — README.md

| # | Claim | Source | |
|---|---|---|---|
| 1 | No broker / API keys / `.env` / order-execution / paper / live trading ever existed | `Closing_Statement_2026-08-05.md:6-11` | ✅ |
| 2 | No strategy advanced past Phase 3; advancing needs a written note first | `Closing_Statement:10,165-168`; `CLAUDE.md:27-31` | ✅ |
| 3 | `yfinance` used read-only for historical prices | `Closing_Statement:9-10` | ✅ |
| 4 | The question, quoted | `Closing_Statement:17-18` | ✅ |
| 5 | 16 researched, 17 backtested, 7 walk-forward | `Closing_Statement:24` | ✅ |
| 6 | Controls: neutralising for the 4 cross-sectional cycles, raw buy-and-hold for the 3 long/cash and vol-targeted ones, rule adopted after | `Closing_Statement:32-38`; `CLAUDE.md:33-59,737-751` | ✅ *(rewritten by Q6)* |
| 7 | Seven-cycle table: windows, beat rates, excesses, intervals | `Observed_Excess_Vs_Zero_2026-08-03.md:49-55`; `Retroactive_Power_Audit_2026-07-31.md:49-53`; `Master_Strategy_Report.md:359,517` | ✅ |
| 8 | Zero inside every interval; two excesses negative | same table | ✅ |
| 9 | Best beat rate 50.0% against a >60% gate | `Master_Strategy_Report.md:359` | ✅ |
| 10 | Measured on real returns, no simulation between returns and the table | `Closing_Statement:45-50` | ✅ |
| 11 | 80% detection at **0.2998**, [0.2821, 0.3170] | `Real_Universe_Detection_Curve:167` | ✅ |
| 12 | Detection at +0.1472 is **~29%** (0.2906) | same, `:170` | ✅ |
| 13 | "roughly twice as coarse" | 0.2998 / 0.1472 = **2.04** | ✅ |
| 14 | 31 years of monthly data on 8 assets is the sample | `Closing_Statement:99-100` | ✅ |
| 15 | 340 + 61 + 143 + 4 = **548** checks, all passing | all four suites run 2026-08-13 | ✅ *(was 521, then 546, then 545 — now asserted at runtime, §T)* |
| 16 | **121** registered perturbations | `tools/mutate.py --audit-anchors` | ✅ |
| 17 | Checks that could not be made to fail were deleted | `ops/tests/test_ops.py:722-726` | ✅ |
| 18 | Sweep: 86 scripts, 79 runnable, 66 / 12 / 1, 8.4 h | `Reproducibility_Sweep.md` (**2026-08-13 run**); 502.5 min = 8.38 h | ✅ *(re-verified §S)* |
| 19 | **At least nine** rounds of adversarial review, briefed to refute | 9 rounds enumerated, `FACTS.md` F7 | ✅ *("each" dropped by Q15)* |
| 20 | Review repeatedly overturned same-day conclusions | 3/7, 4/8, 12/16 — `SESSION_HANDOFF.md:77-81` | ✅ |
| 21 | Nothing was ever pushed | `Closing_Statement:11,171-172` | ✅ |

**Note on #19.** Stated as "at least nine" and not as a total, because one round
(`Sample_Requirement_Adversarial_Review_2026-08-02.md`) publishes no headline
finding count. A total would be a floor presented as a total.

## Verified — ENGINEERING.md

| # | Claim | Source | |
|---|---|---|---|
| 22 | Every defect in the project's history was a silent numeric change | `CLAUDE.md:121-125` | ✅ |
| 23 | Look-ahead bug inflated a Sharpe from 0.46 to 1.11 | `CLAUDE.md:61-67` | ✅ |
| 24 | The mutation rule, as quoted | `CLAUDE.md:407-416` | ✅ |
| 25 | Five checks written 2026-08-02 could not fail | `CLAUDE.md:400-405` | ✅ |
| 26 | One was a regex beginning with a literal backspace byte, matched nothing, carried a failure message describing a real defect | `CLAUDE.md:402-405` | ✅ |
| 27 | All five found by review, none by the suite | `CLAUDE.md:402-403` | ✅ |
| 28 | Root cause was heredoc authoring | `CLAUDE.md:428-431` | ✅ |
| 29 | The five known-vacuous shapes | `CLAUDE.md:418-426` | ✅ |
| 30 | The driver prints "THIS CHECK CANNOT FAIL — it is decoration" and fails the run | `tools/mutate.py:250-252` | ✅ |
| 31 | It reports checks no perturbation ever broke | `tools/mutate.py:259-263` | ✅ |
| 32 | Coverage: ops 61/61, followups 115/116, driver 4/4 | measured 2026-08-12, commit `39f873f` | ✅ |
| 33 | The `isfile(x) == isfile(x)` check, quoted, deleted not repaired | `ops/tests/test_ops.py:722-726`, verbatim | ✅ |
| 34 | A second deletion on 2026-08-12 — a partition's disjointness/coverage, true by definition | `ops/tests/test_ops.py`, commit `39f873f` | ✅ |
| 35 | A perturbation of mine returned `fails=0` and was rewritten | commit `39f873f`; `ops/Review_2026-08-12.md` | ✅ |
| 36 | 121 perturbations do **not** cover the 340-check regression suite | `tools/perturbations.py::SETS` — three sets, none is the regression suite | ✅ |
| 37 | The sweep re-runs with no env vars set, compares bytes, restores the tree | `CLAUDE.md:161-169` | ✅ |
| 38 | Eight artifacts carried prose their generator never emitted | `CLAUDE.md:156-159` | ✅ |
| 39 | A report generated at `P3_FIXED_PERMS=10000` against a script defaulting to 5000 | `CLAUDE.md:136-140` | ✅ |
| 40 | The knob-default rule that followed | `CLAUDE.md:147-148` | ✅ |
| 41 | `pipeline_detection_floor.py` could not run at all, for five days | `CLAUDE.md:171-181` | ✅ |
| 42 | Sweep tallies and 502.5 minutes | `Reproducibility_Sweep.md` (**2026-08-13 run**) | ✅ *(re-verified §S)* |
| 43 | The one DIFFERS seeds from a per-process hash; regenerating moves **14** published floors | `withdrawal_census.py` output; `Seed_Recoverability_2026-08-07.md` | ✅ |
| 44 | Phase gate is a written note in `docs/phase-gates.md` before work | `CLAUDE.md:27-31` | ✅ |
| 45 | Phase 3 / Phase 4 never granted, never requested | `Closing_Statement:165-168` | ✅ |
| 46 | "Capability is not authorization", and the overrun that produced it | `CLAUDE.md:704-735` | ✅ |
| 47 | Reviewer briefed to refute; "looks good" is a failed review | `Lever_Composition_Adversarial_Review_2026-08-01.md:3-5` | ✅ |
| 48 | Findings were rejected — one round returned 12, 2 did not survive | same, `:11-12` | ✅ |
| 49 | Round tallies: 20/20, 14→13+1, 9→7+2, 16/16 | `FACTS.md` F7, each with its own source | ✅ |
| 50 | "Requires forging the record itself" measured at **one blank line** | `Review_2026-08-07_close.md:57-72` | ✅ |
| 51 | `git log -1 -- <path>` returns the commit that *deleted* the file; "touched" for "carries" | `Review_2026-08-07_close.md:14-33` | ✅ |
| 52 | "Exactly the same seven bars" was ten across six | `ops/Review_2026-08-12.md` F1 | ✅ |
| 53 | Six conditions, and the wording of each | `SESSION_HANDOFF.md:169-183` | ✅ |
| 54 | The rewrite quote: *"did the sweep finish?" … "is the sweep's verdict trustworthy?"* | `Tagging_Conditions_2026-08-04.md:3-6`, verbatim | ✅ |
| 55 | **13 of 77** verdicts came from a keyword filter, quoted as numeric | `Tagging_Conditions_2026-08-04.md:6` and the N4 row | ✅ |
| 56 | "Read by a human" dropped as not checkable from committed evidence | `Tagging_Conditions_2026-08-04.md`, §1 row 1 | ✅ |
| 57 | Fingerprint covers **15** functions, every registry, `SWEPT_DIRS`, the timeout; value `5f1d86106dca75dd` | `test_regression.py:1137-1152` — count is 15 | ✅ |
| 58 | The fingerprint's first version was unstable under set-ordering | `test_regression.py:1126-1130` | ✅ |

## Verified — WHAT_WENT_WRONG.md

| # | Claim | Source | |
|---|---|---|---|
| 59 | "Damaged this repository three times… every time it was `git status` that noticed" | `tools/mutate.py:3-4`, verbatim modulo line wrap | ✅ |
| 60 | Leaked fixture → the check it should have broken passed | `tools/mutate.py:6-8` | ✅ |
| 61 | Stale `.pyc` → one perturbation's failure reported as another's | `tools/mutate.py:8-10` | ✅ |
| 62 | Text-mode restore rewrote the sweep harness inside the tagged tree, reporting `restored=True` | `tools/mutate.py:11-16` | ✅ |
| 63 | A perturbation containing a live `git commit` executed | `tools/mutate.py:14-16` | ✅ |
| 64 | Four guards, each demonstrated firing by the self-test | `tools/mutate.py:23-33`; 4 checks pass | ✅ |
| 65 | G3 widened to refs because a deleted **tag** left the worktree looking clean | `tools/mutate.py:98-110` | ✅ |
| 66 | 7-character baseline vs 40-character `rev-parse HEAD`; could never fail | `Verdict_2026-08-07.md:41-46`; `Withdrawals_Marked_2026-08-07.md:130-136` | ✅ |
| 67 | Setting the baseline to HEAD left the suite green at **100/100** | `Conditions_2026-08-07.md:46-47` | ✅ |
| 68 | The false claim stood in at least three documents, incl. the handoff and the previous day's verdict | `Conditions_2026-08-07.md:47-49` | ✅ |
| 69 | Found **while demonstrating a different change** | `Conditions_2026-08-07.md:43-44` | ✅ |
| 70 | The `anchor VERIFIED: b9efd35` output, quoted | `Review_2026-08-07_close.md:20-22` | ✅ |
| 71 | Reproduced in a clone before being accepted | `Review_2026-08-07_close.md:17-19` | ✅ |
| 72 | Four of eight instruments checked; ten holes across six | `ops/Review_2026-08-12.md` F1 | ✅ |
| 73 | The pinned check would have failed that afternoon | `ops/Review_2026-08-12.md` F2 | ✅ |
| 74 | `daily.py` never reads `sys.argv`; capture is unconditional | `ops/daily.py:100-145` | ✅ |
| 75 | The handoff listed it first, and warned against it two sections below | `SESSION_HANDOFF.md:395-408` (quoted removals) | ✅ |
| 76 | Snapshots are write-once; first write for a date wins | `ops/capture.py:97-124` | ✅ |
| 77 | Nothing was deleted in the recovery | `ops/Orientation_2026-08-12.md` §0 | ✅ |
| 78 | The new check was inert for the date that caused it | `ops/Review_2026-08-12.md` F14 | ✅ |
| 79 | Same-session finding rates 3/7, 4/8, 12/16 | `SESSION_HANDOFF.md:77-81` | ✅ |
| 80 | Attribution table: 3 review, 2 person, 1 check | derived from #59–#78; each row traced above | ✅ |

---

## Q — Second pass: the overclaim review (17 findings, 17 confirmed, 0 rejected)

A reviewer was briefed to find **overclaiming in the writing** rather than defects
in the code. Every finding was independently re-verified here before being applied;
all 17 held. **Sixteen of the seventeen are verbs or quantifiers, not numbers** —
which is the single most useful thing this document learned about itself.

| # | Overclaim | Verified against | Fix |
|---|---|---|---|
| Q1 | *"the scheduled run, **which then wrote** the real snapshot"* — narrating a **future** event in the past tense | `ls ops/snapshots/` has no `2026-08-12`; `date` = 14:41; the source says *"will now write"* | Rewritten to future tense |
| Q2 | *"Phase 3 and Phase 4 authorization was **never granted**"* | `docs/phase-gates.md` has 6 dated Phase 3 authorization sections and `:94` *"Phase 3 implementation approved — 2026-07-05"* | Rewritten: Phase 3 was granted repeatedly; **Phase 4** never was |
| Q3 | *"a precommitment mechanism, **and it held under pressure**"* — the next four sentences describe it being overrun | `CLAUDE.md:704-735` | Rewritten: *"the first time it was put under real pressure it was overrun"* |
| Q4 | *"Two more classes **it caught**"* — the sweep did not catch the `P3_FIXED_PERMS` defect | `Reproducibility_Sweep.md:9` — *"That was found by accident. This sweep looks for the rest on purpose."* | Re-split into "built because of" and "caught" |
| Q5 | Column header *"Beat rate (**gate: >60%**)"* invites reading 7.4% as far from a reachable bar | `CLAUDE.md:604-606` — SMA200/Momentum **cannot pass at any edge size**, ceilings 56.3% / 49.6% | Header narrowed; reachability stated under the table |
| Q6 | *"each against a control **chosen to neutralise** the thing that strategy changed"* — false for 3 of 7 rows | `Closing_Statement:34-36` — those three used raw SPY buy-and-hold | Rewritten to say which cycles, and that the rule came *after* |
| Q7 | *"fires about **29%**"* — no interval, and the source says it must not be read as a point | `Real_Universe_Detection_Curve:170` [0.2213, 0.3611]; `:111-118` the 2.54σ rung | Interval and Bonferroni caveat added |
| Q8 | *"The largest edge I ever observed was **0.1472**"* placed on the curve bare | same, `:228-230` — *"Placing it on this curve is legitimate only with that interval attached"* | Interval [−0.19, +0.52] attached |
| Q9 | *"**58** claims checked"* | 80 numbered rows counted by regex | Corrected to 84 / 80 |
| Q10 | *"**Each substantive claim**"* — completeness overstated | Verbs and quantifiers were unchecked | Narrowed to numbers and quotations; this section added |
| Q11 | *"**The entire** published record"* / *"**Every** published number"* | `SWEPT_DIRS = ("validation", "backtest/strategies", "data")`; 8 `ops/*.md` + 21 `followups/*.md` outside it, and 1 script genuinely DIFFERS | Narrowed to the generated half / published *measurements* |
| Q12 | *"a system built so that I **could not** quietly fool myself, which then **caught me trying**"* — a prevention claim | `WHAT_WENT_WRONG.md` §7: 3 review / 2 person / 1 check | Rewritten to what the evidence says |
| Q13 | *"they are **the strongest evidence the process works**"* — the document's own §7 argues the opposite | `WHAT_WENT_WRONG.md:175-199` | Opening rewritten |
| Q14 | *"**After each** work session a reviewer was spawned"* | 10 distinct work dates in `git log`; review rounds on 7 | *"After most work sessions"* |
| Q15 | *"**each** briefed to refute"* — universal sourced from one document | Row 47 sources one round's briefing | *"briefed to refute"* |
| Q16 | 121 perturbations placed adjacent to ~~521~~ checks, implying coverage | `perturbations.py::SETS` — three sets, none the regression suite | README now states the gap explicitly |
| Q17 | *"**every failure above was found**"* — true by construction, the list is *of* found failures | Tautology; the preceding sentence disclaims the same shape | Replaced with the verifiable half (corrected in place) |

### A defect in FOUR sources, found by Q2 — **fixed 2026-08-12**

`reports/Closing_Statement_2026-08-05.md:167-168` stated:

> *"Phase 3 and Phase 4 each require explicit written human authorization in
> `docs/phase-gates.md`. **Neither was ever granted.**"*

**That is false for Phase 3**, and the sentence matters because it describes the
phase gate **as having been bypassed** — the opposite of what happened. Advancing
*to* Phase 3 required a written note and got one; advancing *past* it never
happened.

**Q2 recorded this as unfixed because that session's authorization covered
`writeup/` only.** A later session authorized the CLAIM rather than a file, and
the search it required found **four** documents carrying it, not the two that were
known:

| Document | Wording | Status |
|---|---|---|
| `reports/Closing_Statement_2026-08-05.md:168` | "Neither was ever granted." | **corrected in place** |
| `reports/Project_Capstone_2026-08-03.md:882` | "Neither has been granted." | **corrected in place** |
| `reports/Verdict_Which_Ending_2026-08-03.md:149-150` | "and none was granted or requested" | **corrected in place** |
| `SESSION_HANDOFF.md:438-439` | "neither was ever granted or requested" | **corrected in place** |

**None is a generated artifact** — no script writes any of them, so nothing had to
be regenerated and no sweep verdict is affected by the edits.

**The true statement, now in all four:** Phase 3 was granted in writing on four
dated approvals — 2026-07-05, 2026-07-06, 2026-07-30, and conditionally
2026-07-30/31 — across nine `## Phase 3` sections. Phase 4 was never granted,
never requested and never reached, and every closed cycle records it `BLOCKED`.

> **And a correction to the correction.** The prompt authorizing this work said
> *"six dated Phase 3 authorizations"*. **Four is the count I can defend** from
> explicit granting lines; the other five `## Phase 3` sections record results and
> closures under those grants. `ENGINEERING.md` had said *"at least six times"* —
> my own number, carried from the prompt without counting — and it is now four.

## R — Third pass: my own attack on the prose (10 findings, all fixed)

Task 6 of the previous session found 17, of which **16 were verbs or
quantifiers**. This pass was run to test whether that ratio holds. **It does, and
more strongly: 10 findings, 10 verbs or quantifiers, 0 numbers.**

| # | Class | Overclaim | Verified against | Fix |
|---|---|---|---|---|
| R1 | verb | *"the thing that **proves** the other checks work"* | The driver demonstrates checks *can fail*; it says nothing about whether they check the right thing | *"demonstrates the other checks can fail — which is weaker than 'work', and is the strongest claim available"* |
| R2 | verb | *"Five mechanisms, each with the specific defect **it caught**"* | False since Q4: §2's first example was *built because of* a defect, and §3's example is the mechanism being **overrun** | *"the specific defect behind it — which in two cases is the defect that caused the mechanism to exist"* |
| R3 | quantifier | *"the fingerprint covers … **every registry**"* | Enumerated the module's registry-like constants: **`DIFFERS_EXPLAINED` is one and is NOT hashed** | *"seven of the module's registries"*, with the gap named |
| R4 | quantifier | *"**Every** published measurement in this project lives in a … generated report"* | `ops/All_Pairs_Comparison_2026-08-12.md` is hand-written — its own footer says so — and publishes measurements | Scoped to `trading-research/`, with the exception named |
| R5 | quantifier | *"121 perturbations proving that **the checks** in three of those four suites can fail"* | Coverage is 61/61, 115/116, 4/4 — **180 of 181**, not all | Exact counts given |
| R6 | **system credited for a person** | *"the fingerprint's first version **caught a defect in itself**"* | Nothing detected it; the value visibly differed between runs and I noticed | *"had a defect that its own instability made obvious… I noticed the value would not sit still, which is a person reading output"* |
| R7 | quantifier | *"three of **my six worst mistakes**"* | "Worst" is an uncounted superlative over an unbounded set | *"three of the six failures I have written up"*, plus "I do not know what a further round would find" |
| R8 | **disclosure** | *"nine rounds of adversarial review"* with no statement of what the reviewer was | The reviewer is a **separate AI agent instance**, not a person. An interviewer asks this immediately and the omission reads as concealment | Stated plainly in README and ENGINEERING §4, including that it is *"not independent in the way a second engineer would be"* |
| R9 | quantifier | *"~~521~~ checks pass on **every run**"* | Passes on the runs actually made | *"every run I have made of them"* |
| R10 | verb | *"which is **how you know it is real**"* — an inference from one instance | One perturbation of mine returned `fails=0` | *"that is the most convincing thing I can say about it"* |

**The ratio held, with one correction made by the next review.** The split is
**3 verbs, 5 quantifiers, 1 attribution, 1 disclosure, 0 numbers** — R8 is a
disclosure gap, not a verb or a quantifier, so it is **9 of 10**, and **25 of 27**
across the two prose passes. **26 of 27 were not numbers**, which is the claim
that survives. The numeric layer has now
survived three attacks; the prose layer has produced a finding every time it has
been read by someone looking for one.

R6 and R8 are the two I would not have found by re-reading. R6 is the exact
residual class the previous pass named and could not clear from its own text; R8
is not an overclaim in any sentence but an omission that makes the whole practice
sound like something it is not.

## S — RESOLVED 2026-08-13: the pinned figures, re-verified against the new record

**The sweep completed 2026-08-13 02:00, 502.5 minutes, and wrote the CANONICAL
report.** Every figure §S pinned has been re-checked against it. **Six of the
seven hold unchanged. One moved. None was wrong.**

| Figure | Pinned value | Against the 2026-08-13 record | |
|---|---|---|---|
| Scripts / EXCLUDED / runnable | 86 / 7 / 79 | 86 / 7 / 79 | **HOLDS** |
| Byte-identical | 66 | 66 | **HOLDS** |
| Timestamp-only | 12 | 12 | **HOLDS** |
| DIFFERS | 1, `power_engineering_study.py`, NONDETERMINISTIC | same script, same class | **HOLDS** |
| TIMEOUT / ERROR | 0 | 0 | **HOLDS** |
| Total runtime | 467.8 min / "7.8-hour run" | **502.5 min / 8.4 h** | **MOVED — corrected in README, ENGINEERING, FACTS** |
| "14 published floors would move" | a 2026-08-07 measurement | **neither confirmed nor refuted** | see below |

**The verdict column is identical script-for-script across all 86.** I diffed the
two per-script tables rather than comparing summary totals, because equal totals
can hide two offsetting changes. Nothing offset: no script changed verdict.

**That is a stronger result than re-running and getting the same numbers.** The
harness itself changed between the two runs — Fix D changed where a report may be
written, Fix E changed the environment every script runs in — and the verdicts did
not move. The record survived a change to the logic that produces it.

**On the seventh figure, and this is a limitation not a result.** The claim that
regenerating the DIFFERS artifact would move "14 published floors" is a
2026-08-07 measurement. **This run cannot check it**: the sweep truncates a
DIFFERS detail to three example hunks (`substantive[:3]` in the report writer), so
the record shows three floors moving and says nothing about the other eleven. The
artifact publishes 21 bolded floor values across five tables. The DIFFERS
persisting is *consistent* with the claim and is not evidence for the number.
**Left as a prior measurement, explicitly not re-verified.**

### The runtime, and the two scripts that moved

467.8 → 502.5 min, +7.4%. Two scripts account for +32.2 of the +34.7:
`power_study_seed_audit.py` 68.7 → 89.9 (1.31×) and
`real_universe_detection_curve.py` 78.8 → 89.8 (1.14×). Everything else is within
3%. **Fix E is ruled out as the cause by construction** — no scrubbed name was set
in the launching shell, so every child environment was byte-identical to what it
would have been. The cause is not established and was not investigated.

## T — The check total is computed now, not transcribed

**Added 2026-08-13.** The total lived as a hand-copied number in four documents
and drifted twice in two days:

| | value | why it changed |
|---|---|---|
| through 2026-08-12 morning | 521 | correct |
| 2026-08-12 afternoon | 546 | that day's work added checks |
| 2026-08-12 evening | 545 | two anti-vacuity guards were merged, one being undemonstrable |
| 2026-08-13 | **548** | the check described here added three of its own |

At one point `README.md` said 521, `ENGINEERING.md` and `FACTS.md` said 546, and
the truth was 545. **Three values, none correct in all four places.**

**It survived two passes over the same sentence.** The overclaim review fixed the
*quantifier* beside the number in `WHAT_WENT_WRONG.md:183` ("on every run" → "on
every run I have made of them") without counting it, and the stale-count sweep
that followed listed that exact line by name and then edited three other files.
Two readings, both of which saw 521, neither of which counted it.

**`test_followups.py::test_check_total_is_single_valued` now computes it.** The
three sibling suites are run and their own banners parsed; this suite contributes
its live counter. **No total is stored anywhere in the check** — storing one would
have been the fifth transcription.

Three properties worth stating because each is a limit:

- **It counts its own suite as `PASSED + FAILED + 1`** and that is exact only
  while it is the last check to run, which is why `main()` calls it last. The
  first version put an anti-vacuity check after it and undercounted by exactly
  one, reporting 547. The limitation is real, is documented in the function, and
  is mitigated by placement rather than by cleverness.
- **It scans `writeup/`, `SESSION_HANDOFF.md` and `CLAUDE.md` only.** A total
  stated anywhere else is not seen.
- **It nearly missed its first real target.** The pattern required whitespace
  straight after the digits, so `= **545** checks` in row 15 above — a live,
  wrong claim — slipped through the closing `**`. Widened the same day. A scanner
  for prose has to tolerate the prose's own markup, and mine did not until it was
  pointed at something real.

**Demonstrated failing under three named perturbations** (`TT1`–`TT3`): a document
stating a total the run does not produce; the document scan finding nothing; and a
sibling suite's count becoming unreadable. Each fails exactly one of the three
checks.

## Claims deliberately NOT made

Recorded so that a reader can see the line was drawn on purpose.

| Not claimed | Why |
|---|---|
| "33 strategies" | 33 is a count of `.py` files including grid sweeps and report generators. The strategy counts are 16 / 17 / 7. |
| "Every check is demonstrated failing under a perturbation" | 121 perturbations cover three of four suites. True statement: every check added since the rule was adopted was demonstrated failing before commit. |
| "99 claims were withdrawn" | 99 is a count of withdrawal **markers**; the census structurally verifies **25** and cannot follow 63. |
| A total finding count across all review rounds | One round publishes no headline count, so any total is a floor. |
| Hours of human time | Not recorded anywhere in the repository. |
| That any strategy works, shows promise, or was profitable | Contradicted by the seven-cycle table. |
| That the process caught everything | Two of the six failures in `WHAT_WENT_WRONG.md` were found hours after I published them, and I do not know what a further round would find. Stated in that document. |
| That the detection-curve figures are unqualified | Three caveats travel with them in `FACTS.md` F3b: the rung bracketing the numbers of interest separates at only 2.54σ against a Bonferroni 2.576 and **does not clear it**; the 0% false-positive rate is one gate's property; the ladder's origin is −0.0928, not zero. |

## The weakest claim still standing

**"The protocol reliably detects an edge of about 0.30."**

It is correctly sourced and correctly qualified, and it still rests on a ladder
whose rung between +0.1175 and +0.1421 separates at **2.54σ against a Bonferroni
threshold of 2.576** — a threshold it does not clear. That rung is precisely the
one bracketing the two numbers the curve exists to place. The 0.2998 crossing sits
well above that rung and is not directly affected, but the curve it is read from
has one pair of rungs that are not established as distinct.

The write-up states the crossing with its interval and does not lean on the
adjacent readings. **A reader who pushed on this would be pushing on something
real**, and the honest answer is: the 80% crossing is the most defensible number
on the curve, the detection-rate-at-0.1472 figure is the least, and the seven-cycle
table in §"What I found" does not depend on either.
