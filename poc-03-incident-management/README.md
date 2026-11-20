# POC 03: Incident management, learning from incidents, STPA/CAST on AWS

**Book chapters:** 10 (Incident Management & On-Call), 11 (Learning from Incidents), 12 (STPA & CAST)

| Path | What it shows |
|---|---|
| `terraform/` | **AWS Systems Manager Incident Manager**: multi-region replication set, contacts, 2-stage escalation plan (5-min response), a response plan that runs an SSM Automation diagnosis runbook. Point POC 01's page-severity composite alarms at `response_plan_arn`. |
| `playbooks/slo-burn.md` | IMAG roles (IC / Comms / Ops), triage questions, the **generic mitigations** (rollback, drain, upsize, degrade, block) mapped to AWS commands, multiple-hypotheses investigation, resolution criteria |
| `templates/postmortem-cast.md` | Blameless postmortem built on **CAST**: losses, hazards, control structure, per-controller analysis without hindsight words, systemic factors, traceable actions |
| `templates/stpa-worksheet.md` | Worked **STPA** example on a CodeDeploy → Lambda pipeline: hazards → control structure → unsafe control actions → causal scenarios |
| `incident_metrics.py` | TTD/TTM/TTR **plus** cost of coordination (people, teams, pages, handoffs), % manually detected, % without an IC |

```bash
python incident_metrics.py examples/incidents.json
python -m pytest -q
```

## Interview talking points
* Anyone can declare an incident; label false positives later. Don't let politics decide what counts as an outage.
* Move the decision to the information: the people with the most context make the calls; the IC coordinates.
* MTTR on its own is a weak metric. Look at how many people and teams were involved, how many handoffs there were, and whether the alert or a customer noticed first.
* Root cause analysis assumes a linear chain. CAST/STAMP treat an incident as a **control problem**: why didn't the system's design constrain unsafe behaviour? Human error is a symptom.
* STPA is the forward-looking twin: run it on a design doc. In the Maps example it produced 34 recommendations against the postmortem's 7.
