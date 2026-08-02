"""Markdown Report Generator."""

from __future__ import annotations

from veritas_evalengine.engine.report_types import EvalReport


class MarkdownReportGenerator:
    @staticmethod
    def generate(report: EvalReport) -> str:
        lines = [
            f"# Evaluation Report: `{report.suite_name}`",
            "",
            f"**Timestamp:** {report.timestamp.isoformat()}",
            f"**Total Tasks:** {report.total_tasks}",
            f"**Passed Tasks:** {report.passed_tasks}",
            f"**Failed Tasks:** {report.failed_tasks}",
            "",
        ]

        if report.policy_verdict:
            verdict_str = "✅ PASSED" if report.policy_verdict.passed else "❌ FAILED"
            lines.append(f"## Release Policy Verdict: {verdict_str}")
            if not report.policy_verdict.passed:
                lines.append("\n### Violations:")
                for v in report.policy_verdict.violations:
                    lines.append(f"- `{v}`")
            lines.append("")

        lines.extend(
            [
                "## Task Results Summary",
                "",
                "| Task ID | Task Type | Passed | Metrics |",
                "|---|---|---|---|",
            ]
        )

        for tr in report.task_results:
            status = "✅ Pass" if tr.passed else "❌ Fail"
            metrics_summary = ", ".join([f"{k}={v:.2f}" for k, v in tr.metrics.items()]) or "-"
            lines.append(f"| `{tr.task_id}` | `{tr.task_type}` | {status} | {metrics_summary} |")

        return "\n".join(lines)
