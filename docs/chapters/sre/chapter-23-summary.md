# SRE chapter 23: The future of SRE, and the appendices

*Site Reliability Engineering, 2nd Edition. Course lesson: `#ch-23`. Read: full text, two passes.*

## Summary

Two things won't change: reliability matters, and humans stay involved.

- **Trailing**: Availability: tells you after it broke
- **Leading**: Catalogued risk: tells you what could break

What's changing: **shift left becomes shift down** (managed services and opinionated frameworks with best practice built in); **risk becomes a leading indicator** of reliability, so you identify, catalogue and mitigate it before availability suffers, with AI speeding that up; agents bring far more code and far more services, and SREs move from specialists towards generalists. The book ends optimistic, expecting abundance.

**A:** the ROI of training, comparing "sink or swim" with structured onboarding. **B/C:** an SRE team charter template and an example. **D:** example production-meeting minutes. **E:** composing SLOs: in series, success probabilities multiply (0.8 × 0.9 = 0.72); with hedging, failure probabilities multiply (1 − 0.2 × 0.1 = 0.98); both assume independence.

**F:** latency alerting: build cohorts big enough to be meaningful (say 10,000 or more samples with low variance, covering at least 65% of workloads), baseline over 30–60 days, compute z-scores and watch the share above 2. In theory that's 2.28%, around 4% in practice, and a jump means a regression.

## Key ideas

- what the book expects to stay the same
- the three shifts under way: shift down, risk as a leading indicator, agentic operations
- what each appendix is for

## What the lesson covers

- The big picture
- Appendices worth knowing
- More from the chapter
- Appendices

## Claims and numbers

- E: composing SLOs: in series, success probabilities multiply (0.8 × 0.9 = 0.72); with hedging, failure probabilities multiply (1 − 0.2 × 0.1 = 0.98); both assume independence.
- F: latency alerting: build cohorts big enough to be meaningful (say 10,000 or more samples with low variance, covering at least 65% of workloads), baseline over 30–60 days, compute z-scores and watch the share above 2.
- In theory that's 2.28%, around 4% in practice, and a jump means a regression.
- A, training ROI : sink-or-swim takes 550 weeks plus $220k; structured training takes 483 weeks plus $210k.
- C, example charter (gShoe) : success looks like 100% SLO coverage, toil 50% below the 2022 level, launch prep cut from three months to one, at least 60% utilisation while absorbing a 5× spike for an hour.

## Terms

Trailing, Leading, Across the books, Shift down, A, training ROI, B, charter template, C, example charter (gShoe), D, production meeting minutes, G, statistics and ML

## Takeaways

- Reliability matters more each year, and humans stay in the loop for novel problems.
- Shift down: put reliability into platforms so it’s the default.
- Treat risk as the leading indicator, and use AI to find and remove whole classes of it.
