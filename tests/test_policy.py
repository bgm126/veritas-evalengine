"""Tests for release policy engine."""

from veritas_evalengine.core.policy import PolicyEngine, PolicyRule, ReleasePolicy


def test_policy_rule_evaluation():
    rule1 = PolicyRule(expression="deterministic_failure_count > 0")
    violated1, _ = rule1.evaluate({"deterministic_failure_count": 2})
    assert violated1 is True

    violated1_passed, _ = rule1.evaluate({"deterministic_failure_count": 0})
    assert violated1_passed is False

    rule2 = PolicyRule(expression="pass_rate < 0.8")
    violated2, _ = rule2.evaluate({"pass_rate": 0.95})
    assert violated2 is False

    violated2_fail, _ = rule2.evaluate({"pass_rate": 0.50})
    assert violated2_fail is True


def test_policy_engine():
    policy = ReleasePolicy(
        name="test_pol",
        fail_if=["deterministic_failure_count > 0", "pass_rate < 0.90"],
    )
    engine = PolicyEngine(policy)

    verdict_pass = engine.evaluate({"deterministic_failure_count": 0, "pass_rate": 0.95})
    assert verdict_pass.passed is True
    assert len(verdict_pass.violations) == 0

    verdict_fail = engine.evaluate({"deterministic_failure_count": 1, "pass_rate": 0.95})
    assert verdict_fail.passed is False
    assert len(verdict_fail.violations) == 1
