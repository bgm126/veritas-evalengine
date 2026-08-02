"""Tests for JUnit XML report generator."""

from veritas_evalengine.engine.report_types import EvalReport, EvalTaskResult
from veritas_evalengine.reporting.junit_report import JUnitReportGenerator


def test_junit_report_generator():
    report = EvalReport(
        suite_name="test_suite",
        total_tasks=1,
        passed_tasks=1,
        task_results=[EvalTaskResult(task_id="t1", task_type="rag", passed=True)],
    )
    xml_str = JUnitReportGenerator.generate(report)
    assert "<testsuite" in xml_str
    assert 'name="t1"' in xml_str
