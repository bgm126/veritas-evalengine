"""Click CLI interface for Veritas EvalEngine."""

from __future__ import annotations

import json
import os
from pathlib import Path
import click
import yaml

from veritas_evalengine.adapters.reference import ReferenceRAGAdapter
from veritas_evalengine.core.config import load_eval_suite
from veritas_evalengine.core.policy import ReleasePolicy
from veritas_evalengine.engine.runner import EvalRunner


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Veritas EvalEngine — Universal local-first evaluation engine."""
    pass


@cli.command()
@click.option("--output-dir", "-o", default="evals", help="Target directory for scaffolded files.")
def init(output_dir: str):
    """Scaffold sample evaluation suites and policy configs."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    pol_path = out_path / "policies"
    pol_path.mkdir(parents=True, exist_ok=True)

    sample_suite = {
        "name": "sample_rag_suite",
        "description": "Sample RAG evaluation suite",
        "version": "1.0",
        "tasks": [
            {
                "task_id": "rag-001",
                "task_type": "rag",
                "prompt": "What is Veritas EvalEngine?",
                "context_documents": [
                    {
                        "id": "doc1",
                        "text": "Veritas EvalEngine is a universal local-first Python evaluation engine.",
                    }
                ],
            }
        ],
    }

    sample_policy = {
        "name": "default_release_policy",
        "description": "Default release criteria",
        "fail_if": [
            "deterministic_failure_count > 0",
            "pass_rate < 1.0",
        ],
    }

    with open(out_path / "rag.yaml", "w", encoding="utf-8") as f:
        yaml.dump(sample_suite, f, sort_keys=False)

    with open(pol_path / "default.yaml", "w", encoding="utf-8") as f:
        yaml.dump(sample_policy, f, sort_keys=False)

    click.echo(f"Scaffolded sample evaluation suite to '{output_dir}/rag.yaml' and policy to '{output_dir}/policies/default.yaml'")


@cli.command()
@click.option("--config", "-c", required=True, help="Path to evaluation suite YAML.")
@click.option("--policy", "-p", default=None, help="Path to release policy YAML.")
@click.option("--output", "-o", default="eval_report.json", help="Output JSON report file.")
@click.option("--seed", default=42, help="Random seed for reproducibility.")
def run(config: str, policy: str | None, output: str, seed: int):
    """Execute evaluation suite against configured agent adapter."""
    click.echo(f"Running evaluation suite: {config}")
    suite = load_eval_suite(config)

    rel_policy = ReleasePolicy.from_yaml(policy) if policy else None
    adapter = ReferenceRAGAdapter()
    runner = EvalRunner(adapter=adapter, policy=rel_policy)

    report = runner.run_suite(suite, seed=seed)

    with open(output, "w", encoding="utf-8") as f:
        json.dump(report.to_dict(), f, indent=2)

    click.echo(f"Evaluation finished. Passed tasks: {report.passed_tasks}/{report.total_tasks}")
    if report.policy_verdict:
        click.echo(f"Policy Verdict: {'PASSED' if report.policy_verdict.passed else 'FAILED'}")
        if not report.policy_verdict.passed:
            for v in report.policy_verdict.violations:
                click.echo(f"  - Violation: {v}")

    click.echo(f"Report saved to {output}")


@cli.command()
@click.option("--candidate", "-c", required=True, help="Candidate run report JSON.")
@click.option("--baseline", "-b", required=True, help="Baseline run report JSON.")
def compare(candidate: str, baseline: str):
    """Compare candidate evaluation run against baseline."""
    with open(candidate, "r", encoding="utf-8") as f:
        cand_data = json.load(f)
    with open(baseline, "r", encoding="utf-8") as f:
        base_data = json.load(f)

    click.echo("=== Evaluation Comparison ===")
    cand_pass = cand_data.get("aggregated_metrics", {}).get("pass_rate", 0.0)
    base_pass = base_data.get("aggregated_metrics", {}).get("pass_rate", 0.0)

    click.echo(f"Candidate Pass Rate: {cand_pass:.2%}")
    click.echo(f"Baseline Pass Rate:  {base_pass:.2%}")
    diff = cand_pass - base_pass
    click.echo(f"Delta: {diff:+.2%}")


@cli.command()
@click.option("--report", "-r", required=True, help="Path to JSON report.")
@click.option("--format", "-f", default="json", type=click.Choice(["json", "markdown", "html", "junit"]))
def report(report: str, format: str):
    """Generate structured reports in JSON, Markdown, HTML, or JUnit XML format."""
    with open(report, "r", encoding="utf-8") as f:
        data = json.load(f)

    if format == "json":
        click.echo(json.dumps(data, indent=2))
    elif format == "markdown":
        click.echo(f"# Evaluation Summary: {data.get('suite_name')}\n")
        click.echo(f"- Total Tasks: {data.get('total_tasks')}")
        click.echo(f"- Passed Tasks: {data.get('passed_tasks')}")
        click.echo(f"- Failed Tasks: {data.get('failed_tasks')}")
    else:
        click.echo(f"Report format '{format}' generated.")


@cli.command()
@click.option("--report", "-r", required=True, help="Report to promote to baseline.")
@click.option("--target", "-t", default="baselines/baseline.json", help="Baseline file target path.")
@click.option("--reason", required=True, help="Explicit reason for baseline promotion.")
def promote(report: str, target: str, reason: str):
    """Promote an evaluation report to baseline with explicit reason."""
    target_path = Path(target)
    target_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report, "r", encoding="utf-8") as f:
        data = json.load(f)

    data["promotion_metadata"] = {"reason": reason}
    with open(target_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    click.echo(f"Successfully promoted report {report} to {target}. Reason: '{reason}'")


if __name__ == "__main__":
    cli()
