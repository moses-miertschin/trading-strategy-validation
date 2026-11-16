# TradingBot

A research project that tested whether I could validate a retail trading
strategy. It could not, and establishing that carefully is the result.

**Nothing here trades.** No broker connection, no API keys, no `.env`, no
order-execution code, no paper trading, no live trading. None of these has ever
existed in the repository. `yfinance` was used as a read-only source of
historical prices. No strategy ever advanced past Phase 3, and advancing would
have required me to write an authorization note first.

---

## The question

**Can a retail algorithmic trading strategy, built from free data by one person
in a few weeks, be *validated*?**

That is not "can I find a strategy that makes money". It is a question about
evidence: whether a testing protocol at this scale can tell a real edge apart
from luck.

## What I did

I researched 16 strategies, backtested 17, and put 7 through full walk-forward
validation, each against a decisive control. For the four cross-sectional cycles
that control was chosen to neutralise the thing the strategy changed. The three
long/cash and volatility-targeted cycles were tested against raw buy-and-hold,
which this project later established is the **wrong** control for that strategy
class — the exposure-matched rule came out of discovering that, not before it.

## What I found

**Seven cycles ran. None passed. None produced a result distinguishable from
zero.**

| Strategy | Windows | Beat rate | Excess Sharpe | 95% interval |
|---|---|---|---|---|
| SMA200 regime allocation | 27 | 7.4% | +0.0785 | [−0.19, +0.34] |
| Momentum 12-1 | 27 | 14.8% | +0.0960 | [−0.15, +0.36] |
| Volatility-Targeted SPY | 28 | 25.0% | +0.1224 | [−0.03, +0.27] |
| Sector Rotation | 21 | 47.6% | −0.0667 | [−0.30, +0.13] |
| Inverse-Volatility Sector | 22 | 36.4% | −0.0374 | [−0.13, +0.04] |
| Cross-Asset TSM (7 assets) | 14 | 50.0% | +0.1424 | [−0.20, +0.44] |
| Cross-Asset TSM (8 assets) | 26 | 30.8% | +0.1472 | [−0.17, +0.48] |

The protocol's walk-forward threshold was a beat rate above 60%. **For SMA200 and
Momentum 12-1 that bar is unreachable at any edge size** — their measured ceilings
are 56.3% and 49.6%, because a long/cash strategy *is* the benchmark whenever it
is fully invested and a strict `>` scores that as a loss. So their 7.4% and 14.8%
say much less than the gap to 60% suggests.

Zero sits inside every interval. Two of the seven excesses are negative to begin
with. The best beat rate was a coin flip.

This is measured on the strategies' own real returns against their own controls.
No simulation, no synthetic data, no modelling assumption stands between the
returns and that table.

## Why the answer is "cannot tell", not "they don't work"

I measured what my own testing protocol could actually detect, by injecting
known edges into the real universe and seeing how often the protocol caught them.

**The protocol reliably detects an edge of about 0.30 excess Sharpe** — 0.2998,
95% interval [0.2821, 0.3170], where "reliably" means 80% of the time.

**The largest edge I ever observed was +0.1472**, itself a single realization with
a 95% interval of [−0.19, +0.52]. Read against that curve, an edge of that size
fires the protocol about 29% of the time — 0.2906, interval [0.2213, 0.3611].
**That last figure is the least solid number here**: the two calibration rungs
bracketing it separate at only 2.54σ against a Bonferroni threshold of 2.576, so
it should be read as a region of the curve rather than a point.

So the instrument was roughly twice as coarse as the thing being measured. An
edge the size of the largest one I observed would have been missed about seven
times in ten.

**That is a limitation of breadth and history, not a discovery about markets.**
It says nothing about whether these strategies work — only that 31 years of
monthly data on eight assets cannot answer the question. More history would help
and does not exist. I am not claiming no edge exists anywhere; I am claiming I
could not have seen one this size if it did.

## Why a negative result is the point

I did not set out to find a strategy that worked. I set out to find out whether I
could *tell*. A "yes, it works" from this setup would have been the failure —
because the same setup that produced it could not have distinguished it from
noise, and I would not have known.

Most of the effort here went into making the answer trustworthy rather than into
making it positive:

- **340 + 61 + 143 + 4 = 548 automated checks** across four suites, all passing.
- **121 registered perturbations** that deliberately break the code, to prove that
  the checks in three of the four suites can actually fail. Checks that could not
  be made to fail were deleted. The 340-check regression suite has no perturbation
  set, and that gap is stated rather than papered over.
- **The generated half of the record re-derives from its own scripts**: 86 scripts
  in the three swept directories, 7 excluded for needing network access, 79
  runnable — 66 byte-identical, 12 differing only in a timestamp, 1 with a written
  and classified cause. An 8.4-hour run. Review documents and handoffs are
  hand-written and sit outside the sweep.
- **At least nine rounds of adversarial review** — a separate AI agent instance,
  briefed to refute rather than confirm, whose every finding I then re-verified
  against the artifact myself before accepting it. Findings were rejected. This
  repeatedly overturned conclusions I had written hours earlier the same day.

The interesting artifact here is not a strategy. It is a record built so that
being wrong left evidence — and the evidence says a reader briefed to disagree
caught three of the six failures I have written up, the automated machinery
caught one, and I found two myself by noticing something odd. I do not know what
a further round would find.

## What is worth reading

| | |
|---|---|
| [`ENGINEERING.md`](docs/ENGINEERING.md) | How correctness was enforced, with the specific defect each mechanism caught |
| [`WHAT_WENT_WRONG.md`](docs/WHAT_WENT_WRONG.md) | The failures, including the ones the tooling inflicted on itself |
| [`FACTS.md`](docs/FACTS.md) | Every number above, traced to the artifact it came from |
| [`PROVENANCE.md`](docs/PROVENANCE.md) | Each claim in these documents, checked against its source |
| `trading-research/reports/Closing_Statement_2026-08-05.md` | The full research write-up |

Everything is local. Nothing was ever pushed anywhere.
