# POC 18: Platform scorecard and deprecation brownouts

**Book:** *Platform Engineering at Google* (early release), chapters "Why Developer Experience Matters" (final chapter 18) and "Platform as a Product" (19)

A platform is worth what its adoption is worth. These chapters argue for running the internal platform as a product and measuring it from three views, read in this order.

| View | Question | In `scorecard.py` |
|---|---|---|
| **User** | Do developers use it and like it? | adoption, retention (active against tried-once), median time to first "hello world", first-attempt success, recommendation score |
| **System** | Is it healthy and affordable? | platform SLO attainment, cost of goods sold per active service and its trend, with a flag when cost rises without adoption |
| **Business** | Does it move the organisation? | the five DORA delivery metrics for teams on the platform against teams off it |

`scorecard()["headline"]` enforces the reading order: if adoption or retention is poor, or the first-run experience fails too often, that is the message, whatever the other views say.

`brownout_plan()` supports the last lifecycle phase. Deprecation is a launch in reverse: a plan, communication, migration tooling, and a real off switch. Brownouts (short, deliberate outages of the old service) find the callers nobody knew about.

```bash
python scorecard.py examples/platform.json
python -m pytest -q
```

## On AWS
* **Adoption:** count services created from the golden-path template (a tag or a Service Catalog product), not accounts.
* **Time to first hello world:** repository created to first successful production deploy, from CodePipeline or GitHub events on EventBridge.
* **Delivery metrics:** the same event stream, split by a `platform=on|off` tag.
* **Cost per service:** Cost and Usage Reports with cost allocation tags, divided by active services.
* **Brownouts:** find callers with CloudTrail or ALB/API Gateway access logs; return `410 Gone` with a link to the replacement during the window.

## Templates
`docs/platform/` in this repository has a jobs-to-be-done worksheet, a now-next-later capability roadmap, a deprecation checklist and the shared-fate contract.

## Interview talking points
* "Build it and they will come" fails for three reasons: it ignores existing workflows, costs too much attention, and pays off too late.
* Developer experience has three dimensions: feedback loops, cognitive load, flow.
* A project ends; a product has customers, a value proposition and a lifecycle.
* Validate with an MVP you run by hand for a few teams before writing code.
* "Adoption is voluntary, even when it's mandatory": a mandate without a good product gets malicious compliance.
* Mature platforms need extension points. Avoid tyranny (a rigid path) and chaos (unsupportable customisation).
* Total deployments is a vanity metric.
