"""Guardrails for AI agents acting in production (book ch. 10 'Autonomy in
Production', ch. 21 'Safety and Reliability of AI Solutions', 'Path to Autonomy').

Principles implemented here:
  * Least privilege + DRY RUN first        -> every action supports dry_run()
  * REVERSIBLE OPERATIONS                  -> an action without undo() is refused
  * Atomic transaction                     -> action + validation + auto-rollback,
                                              recorded as ONE auditable entry
  * PROGRESSIVE AUTHORIZATION              -> autonomy level per scenario is earned
                                              from an evaluated track record
  * Absolute human control                 -> global kill switch
  * Transparency                           -> agent must give a rationale + evidence

Autonomy levels (Monitor / Investigate / Approve / Actuate / Self-direct):
  L0 manual   : only monitoring is automated
  L1 assisted : agent monitors + investigates, humans do the rest
  L2 partial  : agent actuates, but a HUMAN APPROVES each action
  L3 high     : agent approves + actuates for well-defined scenarios
  L4 full     : agent plans multi-step responses itself
Not every scenario should reach L4.

The LLM part (e.g. Amazon Bedrock generating a hypothesis and proposing a
mitigation) is pluggable: `propose` is any callable returning a Proposal.
"""
from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from enum import IntEnum
from typing import Callable, Dict, List, Optional, Protocol


class Level(IntEnum):
    L0_MANUAL = 0
    L1_ASSISTED = 1
    L2_PARTIAL = 2
    L3_HIGH = 3
    L4_FULL = 4


class Action(Protocol):
    name: str

    def dry_run(self) -> str: ...
    def apply(self) -> None: ...
    def undo(self) -> None: ...


@dataclass
class Proposal:
    scenario: str          # e.g. "bad-deploy", "az-impairment"
    action: Action
    rationale: str
    evidence: List[str]
    confidence: float


@dataclass
class TrackRecord:
    """Evaluated outcomes per scenario, e.g. from replaying past incidents (evals)."""
    successes: int = 0
    failures: int = 0

    @property
    def total(self) -> int:
        return self.successes + self.failures

    @property
    def success_rate(self) -> float:
        return self.successes / self.total if self.total else 0.0


# Promotion gates: (min evaluated cases, min success rate) required for each level
GATES = {
    Level.L1_ASSISTED: (0, 0.0),
    Level.L2_PARTIAL: (20, 0.90),
    Level.L3_HIGH: (100, 0.99),
    Level.L4_FULL: (1000, 0.999),
}


def earned_level(record: TrackRecord, ceiling: Level) -> Level:
    level = Level.L1_ASSISTED
    for lvl in (Level.L2_PARTIAL, Level.L3_HIGH, Level.L4_FULL):
        n, rate = GATES[lvl]
        if record.total >= n and record.success_rate >= rate:
            level = lvl
    return min(level, ceiling)


@dataclass
class AuditEntry:
    ts: float
    scenario: str
    action: str
    level: str
    decision: str
    rationale: str
    evidence: List[str]
    dry_run: str
    outcome: str = ""


@dataclass
class Guardrails:
    records: Dict[str, TrackRecord] = field(default_factory=dict)
    ceilings: Dict[str, Level] = field(default_factory=dict)  # policy: max level per scenario
    kill_switch: bool = False
    audit: List[AuditEntry] = field(default_factory=list)
    min_confidence: float = 0.7

    def execute(self, p: Proposal, validate: Callable[[], bool], human_approves: Optional[Callable[[Proposal, str], bool]] = None) -> str:
        level = earned_level(self.records.get(p.scenario, TrackRecord()), self.ceilings.get(p.scenario, Level.L3_HIGH))
        plan = p.action.dry_run()
        entry = AuditEntry(time.time(), p.scenario, p.action.name, level.name, "", p.rationale, p.evidence, plan)
        self.audit.append(entry)

        if self.kill_switch:
            entry.decision = "refused: kill switch engaged"
            return entry.decision
        if not callable(getattr(p.action, "undo", None)):
            entry.decision = "refused: action is not reversible"
            return entry.decision
        if not p.rationale or not p.evidence:
            entry.decision = "refused: no rationale/evidence (transparency)"
            return entry.decision
        if level <= Level.L1_ASSISTED:
            entry.decision = "suggest-only: posted to incident channel"
            return entry.decision
        if level == Level.L2_PARTIAL or p.confidence < self.min_confidence:
            if not human_approves or not human_approves(p, plan):
                entry.decision = "awaiting/denied human approval"
                return entry.decision
            entry.decision = "approved by human"
        else:
            entry.decision = "auto-approved"

        # Atomic: apply -> validate -> rollback on failure, one audit record.
        try:
            p.action.apply()
            ok = validate()
        except Exception as exc:  # noqa: BLE001
            ok = False
            entry.outcome = f"apply raised {exc!r}; "
        if ok:
            entry.outcome += "applied and validated"
        else:
            p.action.undo()
            entry.outcome += "validation failed -> rolled back"
        self.records.setdefault(p.scenario, TrackRecord())
        return entry.decision + " / " + entry.outcome

    def audit_json(self) -> str:
        return json.dumps([asdict(a) for a in self.audit], indent=2, default=str)


# ---- Example reversible actions on AWS (boto3 calls left as comments) ----
@dataclass
class ZonalShift:
    """Drain an AZ behind an ALB with Route 53 ARC. Reversible + auto-expiring."""
    resource_arn: str
    away_from_az_id: str
    applied: bool = False
    name: str = "arc-zonal-shift"

    def dry_run(self) -> str:
        return f"StartZonalShift(resource={self.resource_arn}, awayFrom={self.away_from_az_id}, expiresIn=1h)"

    def apply(self) -> None:
        # boto3.client("arc-zonal-shift").start_zonal_shift(resourceIdentifier=..., awayFrom=..., expiresIn="1h", comment="agent")
        self.applied = True

    def undo(self) -> None:
        # boto3.client("arc-zonal-shift").cancel_zonal_shift(zonalShiftId=...)
        self.applied = False


@dataclass
class RollbackLambdaAlias:
    function: str
    alias: str
    previous_version: str
    current_version: str
    active_version: str = ""
    name: str = "lambda-alias-rollback"

    def dry_run(self) -> str:
        return f"UpdateAlias({self.function}:{self.alias} {self.current_version} -> {self.previous_version})"

    def apply(self) -> None:
        self.active_version = self.previous_version

    def undo(self) -> None:
        self.active_version = self.current_version


class IrreversibleDelete:
    name = "delete-table"

    def dry_run(self) -> str:
        return "DeleteTable(orders)"

    def apply(self) -> None:
        raise RuntimeError("never")

    undo = None  # no undo -> guardrails must refuse
