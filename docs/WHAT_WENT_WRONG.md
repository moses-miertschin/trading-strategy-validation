# What went wrong

Six failures, in the order they hurt. They are here because a verification system
that never catches anything is indistinguishable from one that does not run — and
because the pattern in *who* found them, in §7, is not the one I expected and not
the one that flatters the tooling.

Each entry says **who found it** — a check, a review, or a person noticing. That
distinction turned out to matter more than I expected, and §7 is about what it
shows.

---

## 1. The tool that audits the code damaged the repository three times

`tools/mutate.py` is the mutation-testing driver: it perturbs a file, runs a
suite, and restores the file. It is the thing that demonstrates the other checks
can fail — which is weaker than "work", and is the strongest claim available.

**It broke the repository three separate times, and its own file now opens by
saying so:**

> *"This driver has damaged this repository three times, and every time it was
> `git status` that noticed, not the driver."*

1. **A perturbation leaked a fixture file.** On the next run the baseline digest
   already contained it, so the check that perturbation was meant to break
   **passed instead** — a false green produced by the tool whose job is producing
   true reds.
2. **Stale bytecode.** Python caches compiled files on `(mtime, size)`. The driver
   rewrote files sub-second, so one perturbation ran against another's cached
   bytecode and **reported that perturbation's failure as its own.**
3. **A text-mode restore, inside the tagged tree.** Reading a file in text mode
   converts `\r\n` to `\n`. The driver read that way and wrote back, so on a
   Windows-line-ending file the restore was **not byte-exact** — and it reported
   `restored=True`, because it compared the text it had read to the text it had
   written. It silently rewrote `reproducibility_sweep.py`, the sweep harness
   itself, inside the tree a release tag pointed at.

**And in that same session a perturbation containing a live `git commit`
executed**, committing the perturbed source along with every other modified file.

**Found by:** `git status`. Not by the driver, not by a review, not by a suite —
by a human noticing that the working tree was dirty when it should not have been.

**What changed.** The driver moved out of a scratch directory into the repository
and gained four guards, each demonstrated firing by its own self-test: restore is
byte-exact and verified afterwards; a perturbation containing a mutating git verb
is refused before anything is written; the whole repository state — worktree,
HEAD and every ref — is compared before and after and any difference aborts the
run; and bytecode is cleared between runs. The ref comparison exists because an
earlier version watched only the worktree, so a perturbation that deleted a **tag**
left it looking clean.

## 2. A guard that could never fail, while three documents said it protected us

The record has a baseline commit. Re-pointing that baseline at the current commit
would make any drift disappear — so a check existed to forbid it.

**The check compared a 7-character abbreviated hash against a 40-character
`git rev-parse HEAD`.** Those strings can never be equal, so the check could never
match and therefore could never fail. Setting the baseline to `HEAD` verbatim
**left the suite green at 100 of 100.**

The protection had never existed. Meanwhile the claim that it did was standing in
at least three places, including this project's own handoff and the previous day's
verdict. All are now struck in place rather than deleted:

> *"**Every prior statement that the suite blocks re-anchoring was false**,
> including one in this project's own handoff and one in yesterday's verdict."*

**Found by:** a check — but only obliquely, and this is the part worth noting. It
was found **while demonstrating a different change** under the rule that every new
check must be shown failing. Nobody set out to audit it. The rule that forces you
to prove a check can fail is what exposed a check that could not.

## 3. A fix that reintroduced the defect it was written to close, through one word

A function had to answer: *which commit carries this record file?* It used

```
git log -1 -- <path>
```

which returns the commit that most recently **touched** the path — **including a
commit that deleted it.** Verified in a throwaway clone: delete the record, commit
that deletion, and the guard printed

```
anchor VERIFIED: b9efd35 carries the record, and its 96 hashes are that commit's own
```

about a commit where the record **does not exist**, while *rejecting* the honest
one.

This function had been written specifically to close that class of defect. The
review's own summary of it is the cleanest description of the failure mode I have:
**the word "touched" stood in for "carries"** — two sides of a comparison that name
different things, inside the fix for exactly that error.

**Found by:** adversarial review, and it was reproduced in a clone before being
accepted.

## 4. A regression check written in the morning, scheduled to fail that afternoon

On 2026-08-12 I found that a data feed had stopped returning certain historical
bars. I checked the four instruments already known to be affected, found the same
bars missing, and wrote a regression check pinned to that set of seven so any new
one would fail the suite.

**I had checked four of eight instruments.** Checking all eight found **ten missing
bars across six instruments** — two instruments were newly affected and I had not
looked at them, because I had gone looking for confirmation rather than for the
answer.

The consequence was mechanical: the pinned set was a subset of reality, the
scheduled data capture that afternoon would have brought the extra cases onto the
record, and **the check I wrote that morning would have failed the same day.**

**Found by:** adversarial review, hours later, on the same day I wrote it.

## 5. An irreversible action triggered by the documentation's own first instruction

The project runs an unattended job that captures a daily snapshot of market data.
Snapshots are write-once by design: the first write for a date wins, permanently.
Capturing before the market closes therefore freezes a partial view of that day
forever.

The handoff document's list of "what a returning reader checks first" opened with:

```
python ops/daily.py                  # any missed captures?
```

phrased as a question. **`daily.py` parses no arguments at all.** It never reads
`sys.argv`; it calls the capture function unconditionally. I ran
`python ops/daily.py --help`, expecting usage text, at 09:55 — five hours before
the market close.

It wrote eight pre-close files under that day's date. Recovered only because the
output said what it had done, and the directory could be moved to a non-record
location before the 16:30 scheduled run — **which then wrote the day's settled
snapshot on time, on 2026-08-12, and it is committed as one of the six canonical
capture dates.** Nothing was deleted.

> **CORRECTED 2026-08-13.** This read ~~"which **will** write the day's settled
> snapshot at its normal time"~~ — future tense, written at 14:41 on 2026-08-12
> when the 16:30 run had not yet happened. It has. Left in the future tense it
> would have been the same defect in the opposite direction: a document asserting
> as pending something already done.

**The same file carried a warning — "Do not run a capture before 16:30" — two
sections below the instruction that does exactly that.**

**Found by:** a person, immediately, by reading the command's output. No check
existed for it. The check I then wrote turned out to be inert for that very date
(§6).

## 6. The check written to catch §5 was inert for the case that caused it

To make the failure in §5 detectable, I added a check comparing the audit log
against the snapshot directories: every capture on disk must have a corresponding
"run finished" record in the log.

The accidental capture had already written a "run finished" record before its
output was reclassified. So the date that went wrong was **pre-vouched for by the
run that went wrong**, and the check could not have detected a repeat on that date.

**Found by:** adversarial review, the same day, roughly two hours after I wrote the
check.

---

## 7. Who found what, and what that says

| # | Failure | Found by |
|---|---|---|
| 1 | Driver damaged the repository ×3 | **a person**, via `git status` |
| 2 | Guard comparing 7 chars to 40 | **a check** — indirectly, while demonstrating a different one |
| 3 | "touched" standing in for "carries" | **review** |
| 4 | Morning check, afternoon failure | **review** |
| 5 | Irreversible capture from a `--help` | **a person**, reading output |
| 6 | Check inert for its own motivating case | **review** |

**Three of six were found by adversarial review. Two by a person noticing
something. Only one by the automated machinery**, and that one only as a side
effect of a rule about proving checks can fail.

That ratio is the honest headline of this document, and it cuts against the
obvious story. The suites are worth having — 548 checks pass on every run I have
made of them, and they pin real numbers — but **they overwhelmingly catch
regressions in things already understood.**

> **CORRECTED 2026-08-13.** This said ~~521~~. The true total is **548**
> (340 + 61 + 143 + 4) — 545 for a few minutes, until the check described at the
> end of this note added three of its own and moved the number it exists to
> protect. 521 was correct on 2026-08-12 before that day's work
> added checks, and it survived two passes over this very sentence: an overclaim
> review fixed the *quantifier* beside it ("on every run" → "on every run I have
> made of them") and a stale-count sweep listed this line by name and then edited
> three other files. Two readings, both of which saw the number and neither of
> which counted it. A check now computes the total at runtime and fails if any
> document disagrees — see `test_followups.py`. The defects above were all cases where the code did exactly what I
told it to and what I told it was wrong: a comparison between two things that were
never comparable, a word that meant something adjacent to what I needed, a sample
I chose because it would agree with me.

**No test finds those. A reader briefed to disagree finds those.**

There is a second pattern, and it is the less comfortable one. **The failures
cluster in the verification apparatus itself, not in the research.** The mutation
driver, the anchor guard, the fix for the anchor guard, a regression check, and the
check written to cover an incident — five of the six are tooling. Across the last
five review rounds, findings concerning work done *that same session* ran 3 of 7
(2026-08-06), 4 of 8 (2026-08-07), then three rounds in one day on 2026-08-12:
**12 of 16**, **17 of 17**, and **15 of 15**.

> **CORRECTED 2026-08-13.** This said ~~"the last three review rounds… 3 of 7,
> then 4 of 8, then 12 of 16"~~ and stopped two rounds short. The fourth is the
> overclaim review of the write-up itself — 17 findings, all 17 concerning
> documents written hours earlier the same session (`PROVENANCE.md` §Q, commit
> `d389c40`). The fifth is the sweep-fix review, 15 of 15
> (`REVIEW_2026-08-12_sweepfix.md`). **All three fell on 2026-08-12**, not across
> separate days.

The tools built to audit the record had become the largest single source of
defects in the record. That is written into the handoff as a stopping condition
rather than treated as a reason to build more tooling, because the measured trend
says more tooling makes it worse.

**What I would not claim.** That the process caught everything — §4 and §6 were
mine, found hours after I published them, and I do not know what a tenth review
round would find. What I will claim is narrower: the system was
built so that being wrong left evidence, and each failure above was corrected **in
the document that published it** rather than quietly in a new one — the false
re-anchoring claim struck in place across three documents, and the handoff
instruction that caused the capture replaced by a banner naming itself as the
cause.
