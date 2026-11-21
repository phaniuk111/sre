# Claims and numbers

## Numbers to know cold

*Curated from both books. The full mechanical extraction follows.*

| Figure | What it is | Chapter |
|---|---|---|
| **99.9% over 30 days** | 43.2 minutes of error budget | S8 |
| **14.4× burn rate** | 2% of a 30-day budget in one hour: page, confirmed by a 5-minute window | S8 |
| **6× burn rate** | 5% of the budget in six hours: page, confirmed by a 30-minute window | S8 |
| **1× burn rate** | 10% of the budget in three days: ticket | S8 |
| **99% / 99.9% / 99.99% / 99.999% a year** | 87.6 hours / 8.77 hours / 52.6 minutes / 5.26 minutes of downtime | P16 |
| **At least 50%** | of an SRE team’s time on engineering; the toil ceiling is a limit, not a target | S1, S6, S13 |
| **At most 25%** | of time on-call | S6 |
| **6 per site across two sites, or 8 at one** | minimum engineers for a sustainable rotation | S6 |
| **About 2** | incidents per on-call shift at most | S10 |
| **100 to 1,000 engineer-hours** | the cost of one hour of major downtime | S2 |
| **53%** | of visitors abandon a task when a page takes more than three seconds | S2 |
| **1.4× and 1.8×** | more likely to report better delivery and better business outcomes with strong operations practice | S4 |
| **3.5×** | more likely to adopt SRE practices with good documentation | S4 |
| **About 40 days** | from application to offer, after which candidates drop out sharply | S5 |
| **Nearly a fifth** | of SRE alerts at Google are universal alerts every service inherits | S9 |
| **34 against 7** | recommendations from STPA against the original postmortem in the Maps example | S12 |
| **22 against 8** | recommendations from CAST against the postmortem for the misnamed cities | S12 |
| **0.1%, then about ten-fold a day** | a rule of thumb for progressive rollout | S14 |
| **100 to 1 and 2 to 1** | cost of fixing severe and minor defects in production against earlier | S14 |
| **99% of data sources within RPO, 99% of the time** | an example fleet-level backup objective | S16 |
| **About 6 months** | the build horizon: older binaries may not run | S18 |
| **L0 to L4** | autonomy levels for AI operators, from manual to full | S21 |
| **15×** | growth in accelerator use at Google in 24 months | S3 |
| **About 8%** | of Google’s fleet usage was the memory allocator in 2015 | P14 |
| **Doubled in a year** | the share of the fleet using profile-guided optimisation once it became automatic | P14 |
| **Several hundred to one** | developers to security experts, at Google and at small companies alike | P15 |
| **60 to 70%** | of high-severity vulnerabilities in large C and C++ codebases are memory-safety bugs | P15 |
| **Over 70% to 24% in six years** | Android’s memory-safety share after writing new code in safe languages | P15 |
| **Zero in more than a decade** | reported SQL injection in applications protected by safe query APIs | P12, P15 |
| **About 20** | web security controls enabled by default in Google’s frameworks | P15 |
| **L0 to L3** | SLSA build levels | P15 |
| **Four engineers for several months** | to build automated canary analysis; pays back within a year | P16 |
| **8 billion screenshots** | served by an internal tool run by about one part-time person, on shared infrastructure | P10 |
| **More than 15 hours a week** | developers spend on tasks other than writing application code | P18 |
| **About 80%** | of cases a golden path’s defaults should cover | P18, P19 |
| **Under 18 months** | of full-time work equals the hours in a computing degree | P24 |
| **About fivefold in 15 years** | growth in US computing enrolment, without matching teaching staff | P24 |

## Extracted from each chapter

Statements that carry a figure, extracted mechanically from the chapter lessons (`tools/build_reading_docs.py`) and grouped by chapter. They are in my own words; check the book before quoting a number in writing. Platform chapters use the final book's numbering.


### SRE chapter 2

- Not 100%, though: that is always the wrong target.
- Customers get reliability as the feature everything else depends on (but not 100%, which is always the wrong target).
- The chapter’s most quotable table argues that a major outage costs 100 to 1,000 times its length in engineering time.
- The same chapter has a simple worked example for an internal system: a finance outage that idles 400 people for two days at $325 a day is $260,000 before anyone counts the knock-on effects.
- A number worth remembering Google’s research found that 53% of visitors give up on a task when a page takes more than three seconds to load.
- A sidebar describes a SaaS company growing revenue 200% a year while putting off basic production hygiene.
- Uptime went from 99.84% to 99.999%, which is the difference between about an hour of downtime a month and a few seconds.

### SRE chapter 3

- They can't express gray failures like "30% slower for 10% of users", and they only start counting after a disaster.
- On-premises, you bought for the peak and the hardware sat idle 51 weeks a year.
- They can’t describe a gray failure such as “30% slower for 10% of users”.
- More than 3.2 quadrillion tokens a month by mid-2026, accelerator use up fifteen-fold in two years, and machine learning used to predict hardware failures and tune cooling.

### SRE chapter 4

- Reaching 99.999% depends on culture as much as on technology.
- DORA found that teams strong in modern operations practices are 1.4× more likely to report better delivery and operational performance and 1.8× more likely to report better business outcomes.
- Teams with good documentation are 3.5× more likely to adopt SRE practices.
- People who went through SRE onboarding scored 15 to 49 percentage points higher on top-box confidence than those who did general onboarding.
- Set two or three realistic SLOs (if you're at 99.5% today, don't promise 99.999%), start blameless postmortems, then publicise the wins.
- For a new service, the SLO is a design input : 99.99% pushes you away from single-homed designs and towards redundancy, idempotent operations for retries, instrumentation built in as a feature, and load and chaos testing.

### SRE chapter 5

- Process lessons: dropout rises sharply once time from application to offer passes about 40 calendar days, so optimise latency for each candidate rather than throughput; avoid brainteasers; and let a committee, not the hiring manager, decide.
- Informal methods include N+1 mentoring (a mentor from another team), shadowing and reverse shadowing , the Wheel of Misfortune, reverse-engineering systems and reading postmortems.
- To teach production safety to tens of thousands of developers (more than ten times orientation's capacity of about 1,000 a year), the team built a self-paced course with automated reminders that escalate up the management chain.
- They canaried it to 1% of the audience, then rolled it out progressively.
- Net Promoter Score rose 30 points for what was essentially a compliance module, and over 95% completed it.
- Teams are typically 7–10 people per site across two sites.
- Onboarding to on-call can take up to a year, which makes attrition expensive, so managers keep N+1 coverage for on-call and for expertise.

### SRE chapter 6

- Limits: at least 50% engineering time, at most 50% operational work, at most 25% on-call.
- Two sites 6–9 hours apart allow follow-the-sun, with at least six engineers per site (two to three on-call weeks a quarter each).
- Ideally the current on-caller absorbs all the ops work, about 15% of team capacity.
- If SRE alone is primary, developers keep a 24×7 secondary rotation.

### SRE chapter 7

- An SLO of 99.99% under 10 ms needs a very different design from 99% under 250 ms.

### SRE chapter 8

- The sum for 99.9% is 0.001 × 30 days × 1,440 minutes a day = 43.2 minutes.
- 99% is relaxed, 99.9% is the common choice and 99.99% is demanding.
- Where 14.4 comes from: 2% of a 30-day budget in one hour is 0.02 × 720 hours ÷ 1 hour = 14.4 times the sustainable rate.
- At that pace the whole budget is gone in about 50 hours.
- Low traffic needs statistics With 200 requests in an hour, a handful of errors proves nothing.
- For a 14.4% threshold at 99% confidence, that takes 173 failures in 1,000 requests, 42 in 200, or 24 in 100.
- In one case a single 99.99% probe stayed green while small combinations of protocol and destination were completely broken.
- An aggregate burn of 10× could be one customer at 100× and nine at zero.
- Use bad minutes : a minute is bad if its error rate is above, say, 6% when the noise is 5%.

### SRE chapter 9

- Google keeps minute-level data in memory for hours, on disk for weeks, and as 30-minute rollups for years.
- Composing dependencies: in series, success multiplies (80% × 90% = 72%).
- With hedging, failure multiplies (1 − 0.2 × 0.1 = 98%).
- One error in twenty requests is a 5% error rate, and it is almost certainly noise.
- The observed rate can cross the line many times without the alert firing (Figure 9-7 shows exactly this).
- For latency, compare against the service’s own past: group requests into cohorts by method, customer and workload shape, keep a 30-day mean and standard deviation, and alert on z-scores.

### SRE chapter 10

- Coverage that matches users: business hours is “on duty”, daylight across two sites gives about 21 hours, and follow-the-sun gives 24×7.
- Response time: three minutes or less needs two people; 30 minutes allows normal life.
- Schedule options include business hours, daytime (6am–8pm), a daylight span across sites of about 21 hours, and 24-hour coverage via follow-the-sun or compensatory time.
- Humans are poor at passive monitoring beyond about 30 minutes.

### SRE chapter 11

- A cooling-pipe water leak in europe-west9 led to a battery-room fire, and the fire brigade ordered power off for one of the region's three buildings.
- 16:46 A cooling pipe starts leaking above one zone.
- 19:00 Next day: control plane restored across the region.
- Customers' complaints were nearly 12 hours of recovery after power returned, and slow, vague updates; one awkward phrase in an update became a media joke.
- In March 2025, a power loss in us-east5-c stayed local and took about 6 hours instead of more than 11.

### SRE chapter 12

- That is how the same incident produced 22 recommendations where the postmortem had 8.
- Google's diagrams usually have 5–10 boxes, roughly a tenth the size of a dataflow diagram, and drawing one together gives teams a shared language.
- The STPA took 2 engineers part-time for 5 weeks and covered more than 30 subsystems and over a dozen teams.
- It made 34 recommendations against the postmortem's 7.
- CAST took 5 people and 81 hours and produced 22 recommendations; the postmortem took 3 people and 16 hours and produced 8.

### SRE chapter 13

- Build up incrementally (the automation snowball of quick wins first earns trust), add extra safety to early versions, and don't stop at 90%.
- For the pure time-saving case, the chapter points to the well-known xkcd chart (number 1205) that tells you how long you can spend automating a task before you lose more time than you save, counted over five years.
- The sum behind it is simple enough to do in an interview: time saved per run × runs per day × 1,825 days.
- The other traps are dangerous automation without rate limits, scope limits, do-no-harm checks and circuit breakers; deskilling (the 99% case); automation surprise; automating over a broken foundation; automating a moving target; and automating ambiguity.
- Don't stop at 90%, because half-automated processes confuse people and add cognitive load; give the automation readable logs and dashboards with linkable events.
- After an 18-month joint stabilisation effort with the platform team, the service moved to multi-tenancy.
- Keep engineering above 50% (for example, reduce toil from 50% to 30%).

### SRE chapter 14

- From a footnote in the chapter: begin at 0.1% of traffic and grow roughly ten-fold every 24 hours, moving across server locations as you go.
- At 0.1% a bad release hurts almost nobody, so move quickly.
- At 50% a bad release is a major outage, so bake longer.
- One more honest detail: the old claim that a bug costs 100 times more to fix in production is more nuanced than the slogan.
- Watch for performance creep: a run of small regressions took one service from 50 to 250 ms in a year.

### SRE chapter 15

- Case: Google Meet in 2020 saw regional growth of up to 400×, handled with adaptive long-running incident response, separate workstreams, pooled resources, control knobs (load shedding, lower video quality) and attention to burnout.
- Across both books Ideas in this lesson that the platform engineering book also covers, from the knowledge map:Failure domains and N+1 : Survive the loss of a zone or region; say which domain you mean.
- Provisioning for every edge case is like aiming for 100% availability.
- Simple autoscaling rules (add two instances above 70% CPU for five minutes, remove one below 40% with a floor of five) cover most services.
- Typical cloud SLAs are 99.5% for a zone and 99.99% for multi-region services.
- Google's Flex pools quota and saves about 5–20%.
- Then it grew up to 30× (and up to 400× in some regions by mid-May 2020), with first pages on 17 February in Asia.
- Dependency mapping : a 10× target against the pre-COVID peak, tracked in one sheet.

### SRE chapter 16

- Silent corruption found after 40 days with 30 days of backups is unrecoverable.
- On 9/11, Aon's planning had it operating again within hours with no data lost.
- The chapter's authors run Bigtable: 10 exabytes and 7 billion queries per second.
- GDPR fines reach €20M or 4% of global revenue.
- Efficiency : cross-region "RAID" (half the data in A, half in B, parity in C) has 50% overhead instead of 100%, cutting cost by 25%.
- Storage-system bugs : RocksDB research found roughly one corruption per 3 months per 100 PB, with 40% already copied to replicas.
- RWO example: daily backups kept for two days can't recover corruption from three days ago, and with 14 days you can still lose up to 24 hours if the corruption landed at 23:50.
- Build a catalogue with labels and group it into buckets, then give each bucket objectives (24 h RPO with 12 h RTO works manually; 5 min RPO with 3 min RTO must be software-driven).
- On AWS AWS Backup plans selected by tag, Vault Lock in compliance mode, cross-Region and cross-account copies, restore testing, DynamoDB PITR and deletion protection, S3 versioning and Object Lock, Aurora backtrack.

### SRE chapter 17

- Failure domains and N+1 : Survive the loss of a zone or region; say which domain you mean.
- Alignment matters: two regions with two zones each lose 25% of capacity per zone, while one zone per region without anti-affinity loses 50%.
- Degrade to roughly 80% quality for 20% of the compute.
- On AWS Multi-AZ and cells; Route 53 ARC zonal shift and zonal autoshift; static stability; SDK adaptive retries; API Gateway and WAF throttles; SQS buffering; AppConfig flags; Incident Manager replicated across Regions; break-glass IAM roles.

### SRE chapter 18

- “Shift down” means moving a practice from type 2, where every feature team has to know and do it, to type 3 or 4, where the platform does it.
- A platform moves accidental complexity towards clear, making the routine 90% easy so experts can focus on the hard 10%.

### SRE chapter 20

- Going from 30% to 35% costs far more power than going from 75% to 80%.So a half-idle fleet wastes the hardware and still pays most of the power bill.
- Monitor 7-day 95th-percentile occupancy against targets .
- The loop is the ordinary capacity loop from chapter 15; what changes is that supply takes months to arrive and can’t be bought on demand.
- Google's first ML SRE team started in 2009 for ad click prediction.
- Utilisation is measured as duty cycle (for example, P95 occupancy over seven days).
- Starting from 100%, six losses explain the gap:.
- Max utilisation : real-time serving may queue at around 50%, batch at around 90%.
- An ML machine draws roughly 3× a CPU machine, and a 1,000-machine job needs one grid, so its smallest useful footprint is about 3,000× larger.
- On AWS Bedrock (provisioned throughput, guardrails, model evaluation, cross-Region inference), SageMaker endpoints and inference components, EC2 Capacity Blocks for ML, CloudWatch metrics for TTFT and tokens per second.

### SRE chapter 21

- Probabilistic tools at production scale bring probabilistic failure at scale: a 1% error rate spread across all of production is a catastrophe.
- Give agents SLOs too: proposal latency, a helpfulness SLO (say 95% of suggestions accepted) and a safety budget that pauses autonomy when spent.
- At a 0.1% error rate, a customer making 1,000 calls per operation sees nearly every operation fail, and a 0.1% average might really be 1% of customers failing 10% of the time.
- It became core infrastructure in early 2026 and saved thousands of hours of customer impact.
- Toil reduction has a ceiling: with toil at 25%, even processing it 5× faster barely moves overall productivity.

### SRE chapter 22

- A solo SRE focuses on keeping the service running and making developers self-sufficient, and may start at around 80% toil.
- You're the firefighter, the builder and the evangelist, often starting at 80% toil.
- P1, visibility : business and system metrics, symptom alerts switched on at the start of the day (never at home time), and structured JSON logs.
- Six months later, downtime across critical journeys was down about 60% and a major feature shipped 60 days early.
- It now has about a 7:1 developer-to-SRE ratio, and developers spend about 5% of their time on ops, down from nearly half.
- A central team offered issue-flow advice, 90-day engagements, one to three designated SREs at 50–75% for critical services, and a training rotation, then ran an eight-week enablement programme.

### SRE chapter 23

- E: composing SLOs: in series, success probabilities multiply (0.8 × 0.9 = 0.72); with hedging, failure probabilities multiply (1 − 0.2 × 0.1 = 0.98); both assume independence.
- F: latency alerting: build cohorts big enough to be meaningful (say 10,000 or more samples with low variance, covering at least 65% of workloads), baseline over 30–60 days, compute z-scores and watch the share above 2.
- In theory that's 2.28%, around 4% in practice, and a jump means a regression.
- A, training ROI : sink-or-swim takes 550 weeks plus $220k; structured training takes 483 weeks plus $210k.
- C, example charter (gShoe) : success looks like 100% SLO coverage, toil 50% below the 2022 level, launch prep cut from three months to one, at least 60% utilisation while absorbing a 5× spike for an hour.

### Platform chapter 9

- When many people left Twitter in 2022, they overwhelmed Mastodon’s servers.

### Platform chapter 10

- Prototype Started in 2009 as a 20% project.
- Product For more than 15 years a tiny team, often one person part-time, kept it running.
- Infrastructure It reached 8 billion screenshots with no major rework, because it ran on App Engine.

### Platform chapter 14

- In 2015 the memory allocator accounted for about 8% of fleet usage, more than any single application.
- The problem: a service’s CPU use went up 20%.

### Platform chapter 15

- Existing code is the expensive part, and the Android numbers show a way through: writing new code in memory-safe languages took memory-safety bugs from over 70% of the total to 24% in six years, without rewriting the old code.
- Between 60% and 70% of high-severity vulnerabilities in large C and C++ codebases are memory-safety bugs.

### Platform chapter 16

- Failure domains and N+1 : Survive the loss of a zone or region; say which domain you mean.

### Platform chapter 18

- One survey cited in the chapter found developers spend more than 15 hours a week on tasks other than writing application code.

### Platform chapter 19

- The platform team provides the paving, lighting and plumbing, meaning reliability, security and core APIs, and keeps the main roads that take 80% of people where they need to go.

### Platform chapter 24

- An old model from the 1970s, the “surgical team”, gives the critical work to the best engineer and has everyone else support them.
- All the lectures, labs and homework in a computing degree add up to less than 18 months of full-time work, and less than a third of the popular “10,000 hours to mastery” figure.
- Enrolment in the US grew about fivefold in 15 years and teaching staff didn’t, so early courses are graded automatically on whether the output is right.
- Being the person 10,000 Java engineers bring their questions to is another.
