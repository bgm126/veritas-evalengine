"""Example RAG Agent Adapter for Veritas EvalEngine."""

from veritas_evalengine.adapters.reference import ReferenceRAGAdapter

# Re-exports reference RAG adapter for demonstration
RAGAgentAdapter = ReferenceRAGAdapter

if __name__ == "__main__":
    from veritas_evalengine.core.config import load_eval_suite
    from veritas_evalengine.engine.runner import EvalRunner
    from veritas_evalengine.scorers.evidence import EvidenceScorer

    suite = load_eval_suite("eval.yaml")
    runner = EvalRunner(adapter=RAGAgentAdapter(), scorers=[EvidenceScorer()])
    report = runner.run_suite(suite)
    print(f"RAG Evaluation complete. Passed: {report.passed_tasks}/{report.total_tasks}")
