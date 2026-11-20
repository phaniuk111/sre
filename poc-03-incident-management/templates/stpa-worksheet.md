# STPA worksheet: worked example on an AWS deployment pipeline

STPA (System-Theoretic Process Analysis) looks forward: you can run it on a **design doc**, before anything breaks. Four steps.

## Step 1: Losses, hazards and scope
| ID | Loss (unacceptable outcome) |
|---|---|
| L-1 | Customers can't complete checkout |
| L-2 | Orders are lost or double-charged |

| ID | Hazard (detectable system state that leads to a loss in the worst case) | Losses |
|---|---|---|
| H-1 | Checkout serves errors above SLO while a change is still rolling out | L-1 |
| H-2 | Order writes accepted but not durably stored | L-2 |

## Step 2: Control structure
```
            [Engineering manager]  -- launch schedule -->  [Engineer]
                                                             |  deploy / rollback (control actions)
                                                             v
  [CloudWatch alarms] -- feedback -->  [CodeDeploy canary 10% / 5 min]  --> [Lambda alias: checkout]
         ^                                                                   |
         +------------------------- metrics, logs, traces ------------------+
```
For each controller, note its **responsibility**, its **process model** (what it believes about the system) and its **feedback**.

## Step 3: Unsafe control actions (UCAs)
For each control action, consider four ways it can be unsafe:

| Control action | Not provided when needed | Provided when unsafe | Too early / too late / wrong order | Stopped too soon / applied too long |
|---|---|---|---|---|
| Engineer: **roll back** | UCA-1: no rollback while errors exceed SLO (H-1) | UCA-2: rollback to a version that can't read the new data format (H-2) | UCA-3: rollback 40 min after impact starts (H-1) | n/a |
| CodeDeploy: **shift traffic to 100%** | n/a | UCA-4: shifts while the alarm is in INSUFFICIENT_DATA (H-1) | UCA-5: shifts before the bake time covers peak traffic | n/a |

## Step 4: Causal scenarios (why would a UCA happen?)
| UCA | Scenario | Design fix |
|---|---|---|
| UCA-1 | Engineer starts debugging instead of rolling back first | Playbook says "mitigate first"; auto-rollback on alarm |
| UCA-1 | Engineer lacks IAM permission for `codedeploy:StopDeployment` at 3am | on-call role has a pre-approved break-glass path |
| UCA-1 | New pipeline tool launched last week; engineer doesn't know the rollback command | rollback drill in Wheel of Misfortune |
| UCA-2 | Schema change shipped in the same release as code | expand/contract migrations; one change at a time |
| UCA-4 | Alarm `treat_missing_data = notBreaching` hides a silent canary | canary traffic floor; missing data = breaching for probes |

**Output:** prioritised scenarios → design requirements, written *before* launch.
