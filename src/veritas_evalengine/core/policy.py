"""Release policy engine.

Evaluates YAML-defined pass/fail rules against an evidence vector
of scorer metrics. No weighted overall score — each dimension
remains independent.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List, Tuple
import yaml
from pydantic import BaseModel, Field


class PolicyRule(BaseModel):
    expression: str
    description: str = ""

    def evaluate(self, evidence: Dict[str, Any]) -> Tuple[bool, str]:
        """Evaluates the condition expression against evidence vector.

        Returns (violated, reason).
        If rule evaluates to True, it means 'fail condition met' (violation!).
        """
        expr = self.expression.strip()
        match = re.match(
            r"^([a-zA-Z0-9_\.-]+)\s*(==|!=|<=|>=|<|>)\s*([0-9\.-]+)$", expr
        )
        if not match:
            if expr in evidence:
                val = float(evidence[expr])
                return val > 0, f"Rule '{expr}' triggered with value {val}"
            return False, f"Rule '{expr}' could not be parsed or evaluated"

        metric, op, raw_val = match.groups()
        target_val = float(raw_val)

        if metric not in evidence:
            return False, f"Metric '{metric}' not found in evidence"

        actual_val = float(evidence[metric])

        violated = False
        if op == "==":
            violated = actual_val == target_val
        elif op == "!=":
            violated = actual_val != target_val
        elif op == "<":
            violated = actual_val < target_val
        elif op == "<=":
            violated = actual_val <= target_val
        elif op == ">":
            violated = actual_val > target_val
        elif op == ">=":
            violated = actual_val >= target_val

        msg = (
            f"Violation: {metric} ({actual_val}) {op} {target_val}"
            if violated
            else f"Passed: {metric} ({actual_val}) not {op} {target_val}"
        )
        return violated, msg


class ReleasePolicy(BaseModel):
    name: str = "default_policy"
    description: str = ""
    fail_if: List[str] = Field(default_factory=list)

    @classmethod
    def from_yaml(cls, path: str | Path) -> ReleasePolicy:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return cls(
            name=data.get("name", "policy"),
            description=data.get("description", ""),
            fail_if=data.get("fail_if", []),
        )


class PolicyVerdict(BaseModel):
    passed: bool
    violations: List[str] = Field(default_factory=list)
    passed_rules: List[str] = Field(default_factory=list)
    evidence: Dict[str, Any] = Field(default_factory=dict)


class PolicyEngine:
    """Evaluates release policies against run evidence."""

    def __init__(self, policy: ReleasePolicy):
        self.policy = policy

    def evaluate(self, evidence: Dict[str, Any]) -> PolicyVerdict:
        violations: List[str] = []
        passed_rules: List[str] = []

        for expr in self.policy.fail_if:
            rule = PolicyRule(expression=expr)
            violated, msg = rule.evaluate(evidence)
            if violated:
                violations.append(f"{expr} -> {msg}")
            else:
                passed_rules.append(expr)

        return PolicyVerdict(
            passed=len(violations) == 0,
            violations=violations,
            passed_rules=passed_rules,
            evidence=evidence,
        )
