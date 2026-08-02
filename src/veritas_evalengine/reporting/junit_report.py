"""JUnit XML Report Generator for CI integration."""

from __future__ import annotations

from xml.etree import ElementTree as ET
from veritas_evalengine.engine.report_types import EvalReport


class JUnitReportGenerator:
    @staticmethod
    def generate(report: EvalReport) -> str:
        testsuite = ET.Element(
            "testsuite",
            name=report.suite_name,
            tests=str(report.total_tasks),
            failures=str(report.failed_tasks),
            timestamp=report.timestamp.isoformat(),
        )

        for tr in report.task_results:
            testcase = ET.Element(
                "testcase",
                classname=tr.task_type,
                name=tr.task_id,
            )
            if not tr.passed:
                failure = ET.SubElement(testcase, "failure", message="Evaluation task failed")
                failure.text = f"Task {tr.task_id} failed scoring checks."

            testsuite.append(testcase)

        return ET.tostring(testsuite, encoding="unicode", xml_declaration=True)
