"""Tests for Markdown report generator."""

from veritas_evalengine.engine.report_types import EvalReport
from veritas_evalengine.reporting.markdown_report import MarkdownReportGenerator


def test_markdown_report_generator():
    report = EvalReport(suite_name="test_suite", total_tasks=2, passed_tasks=2)
    md_str = MarkdownReportGenerator.generate(report)
    assert "# Evaluation Report: `test_suite`" in md_str
    assert "**Total Tasks:** 2" in md_str
