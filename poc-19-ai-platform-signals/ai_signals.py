"""Platforms for AI: reliability signals a model needs beyond the golden signals.

AI chapter: a model endpoint can return 200 OK quickly with a wrong or harmful
answer (a "silent failure"). So the platform treats three more things as
first-class reliability signals, and gates model releases like any other binary:

  freshness                 how old is the model, against a target for the use case
  data quality / drift      do live inputs still look like the training data?
  probabilistic correctness refuse low-confidence answers: trade a little
                            availability to avoid confident mistakes
  promotion gate            only signed, evaluated, canaried model versions serve

AWS: SageMaker Model Monitor (drift), Model Registry approval status (gate),
Feature Store (one source of feature values, against training-serving skew),
Bedrock Guardrails as an input/output gateway independent of the model.
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta


def psi(expected: list, actual: list, edges: list) -> float:
    """Population stability index between training and live values of one feature.

    Rule of thumb: < 0.1 stable, 0.1-0.25 watch, > 0.25 the model is seeing a different world.
    """
    def shares(values):
        counts = [0] * (len(edges) + 1)
        for v in values:
            counts[sum(v > e for e in edges)] += 1
        return [max(c / len(values), 1e-4) for c in counts]  # floor avoids log(0) for empty buckets

    e, a = shares(expected), shares(actual)
    return round(sum((ai - ei) * math.log(ai / ei) for ei, ai in zip(e, a)), 3)


def drift_status(score: float) -> str:
    return "stable" if score < 0.1 else "watch" if score <= 0.25 else "drifted"


def freshness(trained_at: datetime, now: datetime, max_age: timedelta) -> dict:
    age = now - trained_at
    return {"age_days": age.days, "limit_days": max_age.days, "fresh": age <= max_age}


def confidence_gate(predictions: list, threshold: float) -> dict:
    """predictions: [{"confidence": 0..1, "correct": bool}] from labelled traffic.

    Answers below the threshold are refused (or sent to a fallback or a person).
    Reports what that costs in availability and what it buys in correctness.
    """
    answered = [p for p in predictions if p["confidence"] >= threshold]
    wrong_before = sum(not p["correct"] for p in predictions)
    wrong_after = sum(not p["correct"] for p in answered)
    return {
        "answered_share": round(len(answered) / len(predictions), 3),           # the availability you keep
        "error_rate_ungated": round(wrong_before / len(predictions), 3),
        "error_rate_gated": round(wrong_after / len(answered), 3) if answered else 0.0,
        "wrong_answers_avoided": wrong_before - wrong_after,
    }


def model_slo(health: dict) -> dict:
    """An endpoint is healthy only if the infrastructure AND the model are. health holds booleans."""
    infra = health["available"] and health["latency_ok"]
    model = health["fresh"] and health["drift"] != "drifted" and health["quality_ok"]
    state = "healthy" if infra and model else "silent failure" if infra else "outage"
    return {"state": state, "page": state != "healthy"}


def promotion_gate(version: dict, policy: dict) -> dict:
    """May this model version become the default for serving?"""
    reasons = []
    if not version.get("signed"):
        reasons.append("artifact is not signed by the training pipeline")
    if not version.get("lineage"):
        reasons.append("no lineage: code, data and hyperparameters must all be recorded to reproduce it")
    if version.get("eval_score", 0) < policy["min_eval_score"]:
        reasons.append(f"evaluation {version.get('eval_score', 0)} is below {policy['min_eval_score']}")
    if version.get("eval_score", 0) < version.get("baseline_score", 0) - policy["max_regression"]:
        reasons.append("regresses against the version now serving")
    if not version.get("safety_checks_passed"):
        reasons.append("input/output guardrail tests did not pass")
    canary = version.get("canary")
    if not canary:
        reasons.append("no canary result")
    elif canary["quality_delta"] < -policy["max_regression"]:
        reasons.append("canary quality dropped: roll back")
    return {"promote": not reasons, "reasons": reasons}
