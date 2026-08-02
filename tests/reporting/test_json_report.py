"""Tests for JSON report generator."""

import json
from veritas_evalengine.engine.report_types import EvalReport
from veritas_evalengine.reporting.json_report import JSONReportGenerator


def test_json_report_generator():
    report = EvalReport(suite_name="test_suite", total_tasks=1, passed_tasks=1)
    json_str = JSONReportGenerator.generate(report)
    data = json.loads(json_str)
    assert data["suite_name"] == "test_suite"
    assert data["passed_tasks"] == 1
