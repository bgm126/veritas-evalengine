"""End-to-End Integration Tests for Veritas EvalEngine."""

import json
from pathlib import Path
from click.testing import CliRunner

from veritas_evalengine.adapters.reference import (
    ReferenceCodingAdapter,
    ReferenceMultiAgentAdapter,
    ReferenceRAGAdapter,
    ReferenceToolAdapter,
)
from veritas_evalengine.cli.main import cli
from veritas_evalengine.core.config import load_eval_suite
from veritas_evalengine.core.policy import ReleasePolicy
from veritas_evalengine.engine.runner import EvalRunner
from veritas_evalengine.reporting.html_report import HTMLReportGenerator
from veritas_evalengine.reporting.json_report import JSONReportGenerator
from veritas_evalengine.reporting.junit_report import JUnitReportGenerator
from veritas_evalengine.reporting.markdown_report import MarkdownReportGenerator
from veritas_evalengine.scorers.evidence import EvidenceScorer
from veritas_evalengine.scorers.fidelity import PolicyAdherenceScorer
from veritas_evalengine.scorers.tool_replay import ToolReplayScorer
from veritas_evalengine.scorers.trace import MultiAgentTraceScorer


def test_e2e_full_flow(tmp_path: Path):
    runner = CliRunner()

    # 1. CLI init
    init_res = runner.invoke(cli, ["init", "-o", str(tmp_path / "evals")])
    assert init_res.exit_code == 0

    suite_path = tmp_path / "evals" / "rag.yaml"
    policy_path = tmp_path / "evals" / "policies" / "default.yaml"
    report_output = tmp_path / "report.json"

    # 2. CLI run
    run_res = runner.invoke(cli, ["run", "-c", str(suite_path), "-p", str(policy_path), "-o", str(report_output)])
    assert run_res.exit_code == 0
    assert report_output.exists()

    # 3. CLI promote
    baseline_path = tmp_path / "baselines" / "baseline.json"
    promote_res = runner.invoke(cli, ["promote", "-r", str(report_output), "-t", str(baseline_path), "--reason", "Initial baseline"])
    assert promote_res.exit_code == 0
    assert baseline_path.exists()

    # 4. CLI compare
    compare_res = runner.invoke(cli, ["compare", "-c", str(report_output), "-b", str(baseline_path)])
    assert compare_res.exit_code == 0

    # 5. CLI report formats
    for fmt in ["json", "markdown", "html", "junit"]:
        rep_res = runner.invoke(cli, ["report", "-r", str(report_output), "-f", fmt])
        assert rep_res.exit_code == 0


def test_e2e_all_agent_types():
    rag_suite = load_eval_suite("evals/rag.yaml")
    tool_suite = load_eval_suite("evals/tool.yaml")
    code_suite = load_eval_suite("evals/coding.yaml")
    multi_suite = load_eval_suite("evals/multi_agent.yaml")

    pol = ReleasePolicy(fail_if=["deterministic_failure_count > 0"])

    # RAG
    rag_runner = EvalRunner(adapter=ReferenceRAGAdapter(), scorers=[EvidenceScorer()], policy=pol)
    rag_report = rag_runner.run_suite(rag_suite)
    assert rag_report.passed_tasks == 2

    # Tool
    tool_runner = EvalRunner(adapter=ReferenceToolAdapter(), scorers=[ToolReplayScorer()], policy=pol)
    tool_report = tool_runner.run_suite(tool_suite)
    assert tool_report.passed_tasks == 1

    # Coding
    code_runner = EvalRunner(adapter=ReferenceCodingAdapter(), scorers=[PolicyAdherenceScorer()], policy=pol)
    code_report = code_runner.run_suite(code_suite)
    assert code_report.passed_tasks == 1

    # Multi-Agent
    multi_runner = EvalRunner(adapter=ReferenceMultiAgentAdapter(), scorers=[MultiAgentTraceScorer()], policy=pol)
    multi_report = multi_runner.run_suite(multi_suite)
    assert multi_report.passed_tasks == 1

    # All reports generate cleanly
    json_out = JSONReportGenerator.generate(rag_report)
    junit_out = JUnitReportGenerator.generate(tool_report)
    md_out = MarkdownReportGenerator.generate(code_report)
    html_out = HTMLReportGenerator.generate(multi_report)

    assert len(json_out) > 0
    assert len(junit_out) > 0
    assert len(md_out) > 0
    assert len(html_out) > 0
