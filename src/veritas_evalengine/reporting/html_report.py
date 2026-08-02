"""HTML Report Generator using Jinja2 templates."""

from __future__ import annotations

from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from veritas_evalengine.engine.report_types import EvalReport


class HTMLReportGenerator:
    @staticmethod
    def generate(report: EvalReport) -> str:
        template_dir = Path(__file__).parent / "templates"
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("report.html.j2")

        css_path = template_dir / "styles.css"
        css_styles = css_path.read_text(encoding="utf-8") if css_path.exists() else ""

        policy_passed = report.policy_verdict.passed if report.policy_verdict else True
        policy_violations = report.policy_verdict.violations if report.policy_verdict else []

        return template.render(
            suite_name=report.suite_name,
            timestamp=report.timestamp.isoformat(),
            total_tasks=report.total_tasks,
            passed_tasks=report.passed_tasks,
            failed_tasks=report.failed_tasks,
            policy_passed=policy_passed,
            policy_violations=policy_violations,
            task_results=[tr.model_dump() for tr in report.task_results],
            css_styles=css_styles,
        )
