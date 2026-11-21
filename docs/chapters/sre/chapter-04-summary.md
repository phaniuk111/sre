# SRE chapter 4: The cultural context of SRE

*Site Reliability Engineering, 2nd Edition. Course lesson: `#ch-4`. Read: full text, two passes.*

## Summary

Culture is the foundation layer: practices fail when the environment punishes the behaviour they need. Two fundamentals, focus on the user and reliability as a core value, are supported by seven elements: a data-driven mindset, collaboration and shared responsibility, continuous learning, blamelessness, psychological safety, trust and empowerment.

- **Learning**: Training builds skill
- **Confidence**: People believe they can do it
- **Behaviour**: They do it, repeatedly
- **Culture**: It becomes how things are done

Being data-driven applies to ops health as well as services: track the share of unactionable pages (noisy monitoring), the share of incidents first noticed by humans (wrong SLIs or gaps in coverage), pages per incident, and on-call hours.

**Avoid heroics.** They hide systemic problems, set unrealistic expectations, burn people out and create knowledge silos. **Blamelessness** moves the focus from people to systems; **blame awareness** goes further and asks why the action made sense at the time.

Neither means zero accountability: a "just culture" separates honest mistakes and at-risk behaviour from reckless or criminal conduct.

## Key ideas

- the two foundations and seven elements of a reliability culture
- blame awareness, just culture and Westrum’s three culture types
- how to change culture through behaviour, in brownfield and greenfield

## What the lesson covers

- The big picture
- Adopting SRE in practice
- Seven elements, two foundations
- Data-driven means measuring the process too
- Blame awareness and just culture
- Trust, safety, empowerment
- DORA and Westrum
- Learning → confidence → behaviour → culture
- Brownfield and greenfield

## Claims and numbers

- DORA found that teams strong in modern operations practices are 1.4× more likely to report better delivery and operational performance and 1.8× more likely to report better business outcomes.
- Teams with good documentation are 3.5× more likely to adopt SRE practices.
- People who went through SRE onboarding scored 15 to 49 percentage points higher on top-box confidence than those who did general onboarding.
- Set two or three realistic SLOs (if you're at 99.5% today, don't promise 99.999%), start blameless postmortems, then publicise the wins.
- For a new service, the SLO is a design input : 99.99% pushes you away from single-homed designs and towards redundancy, idempotent operations for retries, instrumentation built in as a feature, and load and chaos testing.

## Terms

Learning, Confidence, Behaviour, Culture, Avoid heroics, Blamelessness, blame awareness, Brownfield, crucial conversation, Greenfield, just culture, pathological, bureaucratic, generative, grounded scale, the crucial conversation

## On AWS

Culture has no service, but you can make it visible: publish SLO dashboards widely, use Incident Manager's post-incident analysis templates, and track action-item closure. DORA metrics can be computed from CodePipeline/CodeDeploy events.

## Takeaways

- Two foundations: focus on the user, and reliability as a core value. Seven elements sit on top.
- Blameless is not accountability-free. Just culture reserves discipline for reckless or criminal acts.
- Learning builds confidence, confidence changes behaviour, and repeated behaviour becomes culture.
