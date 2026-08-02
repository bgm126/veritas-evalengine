"""Tests for HTML report generator."""

from veritas_evalengine.engine.report_types import EvalReport
from veritas_evalengine.reporting.html_report import HTMLReportGenerator


def test_html_report_generator():
    report = EvalReport(suite_name="test_suite", total_tasks=3, passed_tasks=3)
    html_str = HTMLReportGenerator.generate(report)
    assert "<!DOCTYPE html>" in html_str
    assert "Veritas EvalEngine Report" in html_str
    assert "test_suite" in html_str
