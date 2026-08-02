<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.11+"/>
  <img src="https://img.shields.io/badge/License-Apache%202.0-D22128?style=for-the-badge&logo=apache&logoColor=white" alt="License"/>
  <img src="https://img.shields.io/badge/Pydantic-v2-E92063?style=for-the-badge&logo=pydantic&logoColor=white" alt="Pydantic v2"/>
  <img src="https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white" alt="CI"/>
  <img src="https://img.shields.io/badge/Type%20Checked-mypy-1674B1?style=for-the-badge" alt="mypy"/>
  <img src="https://img.shields.io/badge/Linted-Ruff-FCC21B?style=for-the-badge&logo=ruff&logoColor=black" alt="Ruff"/>
</p>

<h1 align="center">
  ⚖️ Veritas EvalEngine
</h1>

<p align="center">
  <strong>The universal, local-first evaluation engine for AI agent systems.</strong>
  <br/>
  <em>Evidence-backed. Statistically rigorous. Framework-agnostic. Production-grade.</em>
</p>

<p align="center">
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-why-veritas">Why Veritas</a> •
  <a href="#-capabilities">Capabilities</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-cli-reference">CLI</a> •
  <a href="#-extending-veritas">Extend</a> •
  <a href="#-benchmarks">Benchmarks</a> •
  <a href="#-mathematical-foundations">Math</a>
</p>

---

## The Problem

You built an AI agent — a RAG pipeline, a tool-using assistant, a coding copilot, a multi-agent research system. Now answer these questions with statistical confidence:

> *"Does my agent hallucinate? How often? With what confidence?"*
>
> *"Did that prompt injection actually bypass my guardrails?"*
>
> *"Is this new model version better than the last — or is the difference just noise?"*
>
> *"When my multi-agent system fails, which agent caused it?"*

Most evaluation tools give you a single number. Veritas gives you **evidence**, **confidence intervals**, and **reproducible proof**.

---

## ⚡ Quick Start

```bash
# Install
pip install veritas-evalengine

# Scaffold a sample evaluation suite
veritas-eval init -o evals

# Run the evaluation
veritas-eval run -c evals/rag.yaml -p evals/policies/default.yaml -o report.json

# Generate a human-readable report
veritas-eval report -r report.json -f markdown

# Compare against a known baseline
veritas-eval compare -c report.json -b baselines/baseline.json
```

**That's it.** Five commands from zero to a statistically rigorous evaluation of your agent.

---

## 🎯 Why Veritas

<table>
  <tr>
    <td width="50%">

### What Existing Tools Do
- ❌ Single aggregate scores with no confidence bounds
- ❌ Tied to specific LLM providers or agent frameworks
- ❌ "Vibe-check" LLM-as-judge with unknown reliability
- ❌ No reproducibility guarantees across runs
- ❌ No drift detection between versions
- ❌ No adversarial stress testing built in
- ❌ No root-cause attribution in multi-agent systems

</td>
<td width="50%">

### What Veritas Does
- ✅ Wilson confidence intervals on every metric
- ✅ Framework-agnostic via the `AgentAdapter` protocol
- ✅ Judge reliability lab with bias quantification
- ✅ Deterministic seeds, content hashes, dataset pinning
- ✅ PSI / EWMA / CUSUM drift detection with alerting
- ✅ 8 adversarial attack families + Garak/PyRIT integration
- ✅ Topological trace analysis with impact attribution

</td>
  </tr>
</table>

### Design Principles

| Principle | Implementation |
|:--|:--|
| **Evidence over opinions** | Every claim is decomposed, traced to source evidence, and scored via NLI entailment — not pattern matching |
| **Confidence over point estimates** | Wilson score intervals, bootstrap CIs, and paired significance tests on all metrics |
| **Determinism over randomness** | Seeded runs, content hashes, pinned dataset revisions, Git-trackable baselines |
| **Independence over aggregation** | No weighted overall score — each evaluation dimension remains independent and auditable |
| **Local-first over cloud-dependent** | Core engine runs fully offline; LLM judges and cloud models are optional fallbacks |

---

## 🔬 Capabilities

Veritas is organized into **7 evaluation capabilities**, each backed by dedicated scorers, statistical tests, and reporting:

### Capability 1 — Evidence-Backed Hallucination Detection

Decomposes agent answers into **atomic claims**, locates **evidence spans** in source documents, and classifies entailment:

```
Agent Answer: "The contract was signed on March 15 and expires after 2 years."
                    ↓ Claim Decomposition
┌──────────────────────────────────────────────────────────────┐
│ Claim 1: "The contract was signed on March 15"               │
│   → Evidence: doc-3, chars 142–189        → SUPPORTED       │
│ Claim 2: "The contract expires after 2 years"                │
│   → Evidence: doc-3, chars 201–245        → CONTRADICTED    │
│   → Source says "3 years"                                    │
└──────────────────────────────────────────────────────────────┘
Grounding Rate: 50.0%   Wilson 95% LCB: 9.5%   Contradiction Rate: 50.0%
```

**Entailment backends:**
- `DeBERTaEntailmentScorer` — Local DeBERTa-v3-large-MNLI (via `[transformers]` extra). No API keys. No data leaves your machine.
- `LLMJudgeEntailmentScorer` — Provider-neutral fallback via LiteLLM. Works with OpenAI, Anthropic, Google, Cohere, or any OpenAI-compatible endpoint.

### Capability 2 — Semantic Entropy & Uncertainty Quantification

Detects hallucination through **information-theoretic uncertainty measurement**:

```
Prompt → Sample N completions at temperature T
         ↓
     Bidirectional entailment clustering
         ↓
     Semantic equivalence classes {C₁, C₂, ..., Cₖ}
         ↓
     H(X) = −Σ p(cᵢ) log p(cᵢ)
         ↓
     High entropy → High uncertainty → Likely hallucination
```

**Includes Semantic Entropy Probes (SEP)** — train a lightweight linear probe on hidden-state representations to predict semantic entropy from a single forward pass, achieving up to **300× speedup** over full N-sample generation.

### Capability 3 — Deterministic Tool Replay

Records and replays an agent's tool-call trace against typed tool specifications:

```yaml
# Tool specification
- name: check_inventory
  input_schema: { product_id: str, warehouse: str }
  output_schema: { available: bool, quantity: int }
  side_effects: [inventory_read]
  forbidden_transitions: [order_cancelled → order_shipped]
```

**Validates:** call ordering, argument type conformance, output handling, terminal state, forbidden side effects, and idempotent replay.

### Capability 4 — Judge Reliability Lab

LLM-as-judge is only useful if you can **quantify how reliable the judge is**:

| Metric | What It Measures | Method |
|:--|:--|:--|
| Inter-rater agreement | Judge consistency | Cohen's κ (weighted) |
| Rank correlation | Ordering accuracy | Spearman ρ |
| Position bias | Order sensitivity | Swap-test flip rate |
| Self-consistency | Re-judge stability | Repeated scoring variance |
| Calibration error | Confidence accuracy | Expected Calibration Error (ECE) |
| Global ranking | Aggregate ordering | Bradley-Terry via MM algorithm |

**Judge modes:** Absolute rubric (1–5), pairwise comparison (with position-bias mitigation), and G-Eval structured scoring.

> **Non-gating by default.** Judge scores are informational until reliability metrics meet configured calibration thresholds.

### Capability 5 — Drift & Instruction-Adherence Monitor

Tracks metric distributions across agent versions and deployment windows:

```
Version 1.2 ──────────── Version 1.3 ──────────── Version 1.4
     │                        │                        │
     │   PSI = 0.03 ✓        │   PSI = 0.28 ⚠️        │
     │   EWMA: stable        │   EWMA: ↘ trend        │
     │   CUSUM: no alarm     │   CUSUM: ALARM at t=47 │
     └────────────────────────┴────────────────────────┘
```

**Detectors:** Population Stability Index (PSI), Exponentially Weighted Moving Average (EWMA), Cumulative Sum (CUSUM) with bilateral change-point detection, and optional embedding cosine distance.

Run history is stored as **append-only JSONL** — Git-trackable and auditable.

### Capability 6 — Instruction-Fidelity Firewall & Adversarial Stress Lab

**8 built-in adversarial attack families**, each with deterministic generators:

| Attack Family | What It Tests | Expected Agent Behavior |
|:--|:--|:--|
| Missing Information | Incomplete context | Abstain / "I don't know" |
| Contradictory Sources | Conflicting documents | Flag conflict, cite both |
| Poisoned Documents | Injected false evidence | Reject unverifiable claims |
| Poisoned Tool Outputs | Manipulated tool returns | Validate against schema |
| Instruction Conflicts | Contradictory directives | Request clarification |
| Prompt Injection | Direct injection attempts | Reject / maintain boundaries |
| Multi-Turn Jailbreak | Escalating manipulation | Maintain guardrails |
| Forbidden Actions | Prohibited tool/data access | Refuse with explanation |

**Scoring:** Attack success rate with Wilson confidence intervals per family and per agent version. Paired bootstrap tests for cross-version comparison.

**Optional integrations:** [Garak](https://github.com/NVIDIA/garak) probe corpora and [PyRIT](https://github.com/Azure/PyRIT) adaptive multi-turn attacks — both adapter-based, zero required dependencies.

### Capability 7 — Multi-Agent Failure Attribution

When a multi-agent system produces a wrong answer, Veritas builds a **directed trace graph** and identifies the root cause:

```
Orchestrator
    ├── Researcher Agent
    │       ├── [tool_call] web_search("quantum computing")     ✓
    │       └── [claim] "QC achieves 1000 qubit stability"      ✗ ← ROOT CAUSE
    │                     ↓ propagates to
    ├── Writer Agent
    │       └── [claim] "Stable 1000-qubit systems exist"       ✗ ← DOWNSTREAM
    │                     ↓ propagates to
    └── Final Answer: "1000-qubit quantum computers are stable" ✗ ← OBSERVED FAILURE
```

**Analysis pipeline:** Topological sort → earliest invalid event → downstream impact attribution → minimal root-cause path.

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         veritas-eval CLI                            │
│   init  ·  run  ·  compare  ·  report  ·  promote                  │
└────────────────────────────┬────────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────────┐
│                        EvalRunner                                   │
│  Loads EvalSuite → Runs AgentAdapter → Routes to Scorers →         │
│  Evaluates Release Policy → Produces EvalReport                    │
└──┬──────────────┬──────────────┬──────────────┬────────────────────┘
   │              │              │              │
   ▼              ▼              ▼              ▼
┌──────┐   ┌──────────┐   ┌──────────┐   ┌────────────┐
│Adapt-│   │ Scorers  │   │ Entropy  │   │  Stress    │
│ ers  │   │          │   │          │   │  Lab       │
│      │   │ evidence │   │ sampling │   │            │
│generi│   │ tool_rep │   │ cluster  │   │ generators │
│otel  │   │ drift    │   │ probe    │   │ runner     │
│refer-│   │ fidelity │   │          │   │ adapters   │
│ence  │   │ judge    │   │          │   │ (garak,    │
│      │   │ trace    │   │          │   │  pyrit)    │
└──┬───┘   └────┬─────┘   └────┬─────┘   └─────┬──────┘
   │            │              │                │
   └────────────┴──────┬───────┴────────────────┘
                       │
   ┌───────────────────▼───────────────────────────────────────┐
   │                    Core Contract                           │
   │                                                            │
   │  AgentRun  ·  EvalTask  ·  EvalSuite  ·  ScorerResult     │
   │  Claim  ·  ToolCall  ·  TraceEvent  ·  StateTransition    │
   │                                                            │
   │  AgentAdapter Protocol  ·  Scorer Protocol                 │
   └───────────────────┬───────────────────────────────────────┘
                       │
   ┌───────────┬───────┴───────┬──────────────┐
   ▼           ▼               ▼              ▼
┌──────┐  ┌─────────┐  ┌───────────┐  ┌──────────┐
│Stats │  │Benchmark│  │ Reporting │  │  Policy  │
│      │  │Adapters │  │           │  │  Engine  │
│wilson│  │         │  │ json      │  │          │
│boots-│  │truthful │  │ junit     │  │ fail_if  │
│trap  │  │halueval │  │ markdown  │  │ rules    │
│mcnem-│  │fever    │  │ html      │  │          │
│ar    │  │simpleqa │  │ (jinja2)  │  │          │
│BT    │  │         │  │           │  │          │
│psi   │  │         │  │           │  │          │
│cusum │  │         │  │           │  │          │
└──────┘  └─────────┘  └───────────┘  └──────────┘
```

### The Contract Boundary

Everything in Veritas flows through **two types**:

```python
# Your agent implements this:
class AgentAdapter(Protocol):
    def run(self, task: EvalTask) -> AgentRun: ...

# Every scorer implements this:
class Scorer(Protocol):
    name: str
    def score(self, task: EvalTask, run: AgentRun) -> ScorerResult: ...
```

`AgentRun` is the **universal normalized output** — it captures the final answer, decomposed claims with evidence spans, tool-call traces, state transitions, multi-agent trace events, model metadata, cost tracking, and content hashes. Every scorer, every statistical test, every reporter works exclusively from `AgentRun` instances. No raw dicts. No framework-specific types.

---

## 📦 Installation

### Minimal (core engine, no ML models)

```bash
pip install veritas-evalengine
```

### With local entailment model (DeBERTa-v3-large-MNLI)

```bash
pip install "veritas-evalengine[transformers]"
```

### With LLM-judge support (provider-neutral via LiteLLM)

```bash
pip install "veritas-evalengine[llm]"
```

### With benchmark datasets (TruthfulQA, HaluEval, FEVER, SimpleQA)

```bash
pip install "veritas-evalengine[benchmarks]"
```

### With OpenTelemetry trace ingestion

```bash
pip install "veritas-evalengine[otel]"
```

### Everything

```bash
pip install "veritas-evalengine[all]"
```

### Development

```bash
git clone https://github.com/your-org/veritas-evalengine.git
cd veritas-evalengine
pip install -e ".[all,dev]"
pytest tests/ -m "not provider and not benchmark"
```

---

## 🖥 CLI Reference

### `veritas-eval init`

Scaffold a ready-to-run evaluation project:

```bash
veritas-eval init -o my_evals
```

Creates:
```
my_evals/
├── rag.yaml              # Sample RAG evaluation suite
└── policies/
    └── default.yaml      # Sample release policy
```

### `veritas-eval run`

Execute an evaluation suite against your agent:

```bash
veritas-eval run \
  -c evals/rag.yaml \
  -p evals/policies/default.yaml \
  -o report.json \
  --seed 42
```

**Flags:**
| Flag | Description | Default |
|:--|:--|:--|
| `-c, --config` | Path to evaluation suite YAML | Required |
| `-p, --policy` | Path to release policy YAML | None (no policy gating) |
| `-o, --output` | Output JSON report path | `eval_report.json` |
| `--seed` | Random seed for reproducibility | `42` |

### `veritas-eval compare`

Statistically compare a candidate run against a baseline:

```bash
veritas-eval compare -c candidate.json -b baselines/baseline.json
```

Reports per-metric deltas with significance indicators.

### `veritas-eval report`

Generate human-readable reports in multiple formats:

```bash
# Markdown (great for PR comments)
veritas-eval report -r report.json -f markdown

# Static HTML (interactive dashboard with charts)
veritas-eval report -r report.json -f html

# JUnit XML (CI integration — each task = test case)
veritas-eval report -r report.json -f junit

# Structured JSON (machine-readable)
veritas-eval report -r report.json -f json
```

### `veritas-eval promote`

Promote a passing evaluation to the tracked baseline:

```bash
veritas-eval promote \
  -r report.json \
  -t baselines/baseline.json \
  --reason "v1.3 release candidate — all evidence scorers pass, drift within bounds"
```

> **Explicit reason required.** No silent baseline updates. Every promotion is auditable.

---

## 📝 Writing Evaluation Suites

Evaluation suites are YAML files containing tasks, context, and expected outcomes:

```yaml
name: customer_support_rag
description: "Evaluate RAG accuracy on customer support knowledge base"
version: "1.0"
tasks:
  - task_id: cs-001
    task_type: rag
    prompt: "What is the return policy for electronics?"
    reference_answer: "Electronics can be returned within 30 days with receipt."
    context_documents:
      - id: policy-doc-7
        text: >
          Return Policy: Electronics purchased in-store or online may be
          returned within 30 days of purchase. Original receipt required.
          Items must be in original packaging.
    tags: [returns, electronics, policy]

  - task_id: cs-002
    task_type: rag
    prompt: "Can I return a laptop after 60 days?"
    reference_answer: null  # Agent should abstain — no 60-day policy exists
    context_documents:
      - id: policy-doc-7
        text: "Return Policy: Items may be returned within 30 days."
    forbidden_actions: [fabricate_policy]
    tags: [returns, abstention]
```

### Release Policies

Define pass/fail criteria as independent rules — no opaque weighted scores:

```yaml
name: production_release_policy
description: "Minimum quality bar for production deployment"
fail_if:
  - deterministic_failure_count > 0
  - pass_rate < 0.95
  - grounding.wilson_lcb < 0.80
  - contradiction_rate > 0.05
```

Each rule is evaluated independently against the evidence vector. **If any rule fails, the release is blocked.**

---

## 🔌 Extending Veritas

### Custom Agent Adapter

Wrap your agent in the `AgentAdapter` protocol:

```python
from veritas_evalengine.core.protocols import AgentAdapter
from veritas_evalengine.core.schemas import AgentRun, EvalTask

class MyRAGAgent(AgentAdapter):
    def __init__(self, retriever, llm):
        self.retriever = retriever
        self.llm = llm

    def run(self, task: EvalTask) -> AgentRun:
        # Your agent logic here
        docs = self.retriever.search(task.prompt)
        answer = self.llm.generate(task.prompt, context=docs)

        return AgentRun(
            run_id=f"run-{task.task_id}",
            task_id=task.task_id,
            final_answer=answer,
            evidence_spans=[...],   # Map retrieved docs to EvidenceSpan
            tool_calls=[...],       # Record any tool invocations
            model_metadata=ModelMetadata(model_name="gpt-4o"),
        )
```

### Custom Scorer

Implement the `Scorer` protocol:

```python
from veritas_evalengine.core.protocols import Scorer
from veritas_evalengine.core.schemas import EvalTask, AgentRun, ScorerResult

class ToxicityScorer(Scorer):
    name = "toxicity"

    def score(self, task: EvalTask, run: AgentRun) -> ScorerResult:
        toxicity_score = self.model.predict(run.final_answer)
        return ScorerResult(
            scorer_name=self.name,
            passed=toxicity_score < 0.1,
            score=1.0 - toxicity_score,
            metrics={"toxicity_raw": toxicity_score},
        )
```

### Plugin Registration via Entry Points

Register your custom components in `pyproject.toml`:

```toml
[project.entry-points."veritas_evalengine.scorers"]
toxicity = "my_package.scorers:ToxicityScorer"

[project.entry-points."veritas_evalengine.adapters"]
my_rag = "my_package.adapters:MyRAGAgent"
```

Veritas discovers plugins automatically at startup via `importlib.metadata.entry_points()`.

---

## 📊 Benchmarks

Veritas includes adapters for established hallucination and factuality benchmarks:

| Benchmark | Domain | License | Metrics |
|:--|:--|:--|:--|
| [TruthfulQA](https://github.com/sylinrl/TruthfulQA) | Factuality / truthfulness | Apache-2.0 | Precision, Recall, F1, AUROC |
| [HaluEval](https://github.com/RUCAIBox/HaluEval) | Hallucination detection | MIT | Precision, Recall, F1, AUROC |
| [FEVER](https://fever.ai/) | Fact verification | CC-BY-SA | Precision, Recall, F1, AUROC |
| [SimpleQA](https://github.com/openai/simple-evals) | Short-answer factuality | MIT | Precision, Recall, F1, AUROC |

All benchmark adapters convert datasets to `EvalTask` objects with **pinned dataset revisions** for reproducibility. Each reports detection performance, latency, and cost for your scorer configuration.

```bash
# Install benchmark dependencies
pip install "veritas-evalengine[benchmarks]"

# Run against TruthfulQA
pytest tests/benchmarks/test_truthfulqa.py -m benchmark
```

---

## 📐 Mathematical Foundations

Veritas doesn't hide its math. Here's what's under the hood:

### Confidence Intervals

**Wilson score interval** for binomial proportions (grounding rate, attack success rate):

$$\tilde{p} = \frac{1}{1 + z^2/n} \left( \hat{p} + \frac{z^2}{2n} \pm z\sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}} \right)$$

Preferred over Wald intervals because it maintains valid coverage even at extreme proportions or small sample sizes.

**Bootstrap confidence intervals** for arbitrary statistics (metric deltas, drift magnitudes):

$$\text{CI}_{1-\alpha} = \left[ \hat{\theta}^*_{(\alpha/2)}, \; \hat{\theta}^*_{(1-\alpha/2)} \right]$$

### Significance Testing

**Paired bootstrap test** for comparing candidate vs. baseline runs on any metric. Accounts for paired structure of task-level results.

**McNemar's test** for paired binary outcomes (pass/fail per task). Appropriate when the same tasks are evaluated under two conditions.

### Drift Detection

| Method | Formulation | Use Case |
|:--|:--|:--|
| PSI | $\text{PSI} = \sum (p_i - q_i) \ln(p_i/q_i)$ | Distribution shift between versions |
| EWMA | $S_t = \lambda x_t + (1-\lambda) S_{t-1}$ | Smooth trend detection |
| CUSUM | $C_t^+ = \max(0, C_{t-1}^+ + x_t - \mu_0 - k)$ | Change-point detection with alarm |

### Semantic Entropy

Shannon entropy across semantic equivalence classes:

$$H(X) = -\sum_{c \in \mathcal{C}} p(c) \log p(c), \quad p(c) = \frac{|c|}{N}$$

where clusters $\mathcal{C}$ are formed by bidirectional entailment over $N$ stochastic samples.

### Judge Ranking

**Bradley-Terry model** fitted via Minorization-Maximization:

$$P(i \succ j) = \frac{\pi_i}{\pi_i + \pi_j}$$

Converts pairwise judge comparisons to a global ranking with bootstrapped confidence intervals on latent strength parameters.

### Code Quality Evaluation

**Pass@k estimator** (unbiased, per Chen et al.):

$$\text{pass@k} = 1 - \frac{\binom{n-c}{k}}{\binom{n}{k}}$$

---

## 🏛 Project Structure

```
veritas-evalengine/
├── src/veritas_evalengine/
│   ├── core/               # AgentRun, EvalTask, protocols, policy engine
│   │   ├── schemas.py      # Central data model (the contract boundary)
│   │   ├── protocols.py    # AgentAdapter & Scorer protocol definitions
│   │   ├── config.py       # YAML configuration loader
│   │   └── policy.py       # Release policy evaluation engine
│   ├── adapters/           # Agent-agnostic adapter layer
│   │   ├── generic.py      # Wrap any callable → AgentAdapter
│   │   ├── otel.py         # OpenTelemetry trace → AgentRun mapping
│   │   └── reference.py    # 4 reference agent adapters for testing
│   ├── scorers/            # 7 scorer types with sub-components
│   │   ├── evidence.py     # Claim decomposition + entailment scoring
│   │   ├── tool_replay.py  # Deterministic tool-call trace replay
│   │   ├── drift.py        # PSI / EWMA / CUSUM drift detection
│   │   ├── fidelity.py     # Abstention, citation, policy adherence
│   │   ├── judge.py        # Rubric, pairwise, G-Eval judges
│   │   └── trace.py        # Multi-agent failure attribution
│   ├── entropy/            # Semantic entropy & uncertainty probes
│   │   ├── sampling.py     # Stochastic N-sample generation
│   │   ├── clustering.py   # Entailment-based semantic clustering
│   │   └── probe.py        # Hidden-state linear probes (SEP)
│   ├── stress/             # Adversarial stress testing
│   │   ├── generators.py   # 8 attack family generators
│   │   ├── runner.py       # Stress suite execution & scoring
│   │   └── adapters.py     # Garak & PyRIT integration
│   ├── statistics/         # Statistical testing & drift math
│   │   ├── confidence.py   # Wilson CI, bootstrap CI, pass@k
│   │   ├── comparison.py   # Paired bootstrap, McNemar's test
│   │   ├── ranking.py      # Bradley-Terry model
│   │   └── drift_stats.py  # PSI, EWMA, CUSUM implementations
│   ├── benchmarks/         # Standard benchmark adapters
│   │   ├── truthfulqa.py   # TruthfulQA factuality benchmark
│   │   ├── halueval.py     # HaluEval hallucination benchmark
│   │   ├── fever.py        # FEVER fact verification
│   │   └── simpleqa.py     # SimpleQA short-answer benchmark
│   ├── reporting/          # Multi-format report generation
│   │   ├── json_report.py  # Structured JSON output
│   │   ├── junit_report.py # JUnit XML for CI pipelines
│   │   ├── markdown_report.py # Markdown summary tables
│   │   └── html_report.py  # Static HTML dashboard (Jinja2)
│   ├── engine/             # Evaluation orchestration
│   │   ├── runner.py       # Main evaluation runner
│   │   ├── registry.py     # Plugin discovery via entry points
│   │   └── report_types.py # EvalReport, PolicyVerdict types
│   └── cli/                # Click-based command interface
│       └── main.py         # init, run, compare, report, promote
├── evals/                  # Sample evaluation suites
│   ├── rag.yaml
│   ├── tool.yaml
│   ├── coding.yaml
│   ├── multi_agent.yaml
│   ├── policies/default.yaml
│   └── stress/             # Adversarial stress suites
├── examples/               # 4 complete reference implementations
│   ├── rag_agent/          # RAG pipeline evaluation
│   ├── tool_agent/         # Tool-using agent with sandboxed tools
│   ├── coding_agent/       # Code generation with test-based grading
│   └── multi_agent/        # Multi-agent system with injected failure
├── tests/                  # Comprehensive test suite
│   ├── scorers/golden/     # Golden test fixtures
│   ├── entropy/golden/
│   └── stress/golden/
└── .github/workflows/ci.yaml  # CI: lint, type-check, test, e2e
```

**47 source modules** · **31 test modules** · **3,900+ lines of Python** · **78 files**

---

## 🔄 Reproducibility Guarantees

Every evaluation run captures a complete provenance chain:

| Element | How It's Tracked |
|:--|:--|
| Agent outputs | `AgentRun.content_hash()` — SHA-256 of deterministic payload |
| Model configuration | `ModelMetadata` — model name, provider, temperature, prompt hash |
| Random state | `--seed` flag → `AgentRun.seed` on every run |
| Dataset version | `EvalSuite.dataset_revision` — pinned HuggingFace revision hash |
| Baseline comparison | `veritas-eval promote --reason "..."` — explicit, auditable promotion |
| Run history | Append-only JSONL — Git-trackable, never overwritten |

### Baseline Management

```bash
# Promote current results to baseline (requires explicit reason)
veritas-eval promote -r report.json -t baselines/v1.3.json \
  --reason "Release candidate v1.3 — all capabilities pass"

# Future runs compare against this baseline
veritas-eval compare -c new_report.json -b baselines/v1.3.json
```

CI detects uncommitted baseline changes. No silent regressions.

---

## 🔧 CI Integration

### GitHub Actions

Veritas ships with a ready-to-use CI workflow:

```yaml
# .github/workflows/ci.yaml
# Triggers: push/PR to main
# Matrix: Python 3.11, 3.12
# Pipeline:
#   1. Lint (Ruff) + Type check (mypy)
#   2. Unit tests (offline, no API keys)
#   3. E2E evaluation with reference agents
#   4. Compare against committed baselines
#   5. Block merge on statistically significant regressions
```

### JUnit Integration

```bash
# Generate JUnit XML for any CI system
veritas-eval report -r report.json -f junit > test-results.xml
```

Each evaluation task maps to a JUnit test case. Each scorer maps to a test suite. Compatible with Jenkins, CircleCI, GitLab CI, Azure DevOps, and any JUnit-compatible reporter.

---

## 🗺 Roadmap

- [ ] Interactive HTML dashboard with drill-down trace visualization
- [ ] Async agent adapter support for concurrent evaluation
- [ ] OpenTelemetry export for evaluation traces
- [ ] VS Code extension for inline evaluation results
- [ ] Multi-language agent support (TypeScript, Go adapters)
- [ ] Hosted benchmark leaderboard

---

## 🧪 Running Tests

```bash
# Full offline test suite (no API keys required)
pytest tests/ -m "not provider and not benchmark"

# With benchmark dataset tests (requires datasets download)
pytest tests/ -m "not provider"

# Provider-backed tests (requires API keys)
OPENAI_API_KEY=... pytest tests/ -m "provider"

# Type checking
mypy src/veritas_evalengine/

# Linting
ruff check src/ tests/
```

---

## 📄 Scope Disclaimer

Veritas provides two classes of evaluation:

1. **Deterministic checks** (tool replay, policy adherence, forbidden actions) — these prove bounded properties within the evaluation sandbox.
2. **Statistical checks** (grounding rates, drift detection, judge reliability, attack success rates) — these provide **confidence-bounded empirical evidence** over the declared task distribution.

Statistical results are not universal mathematical proofs. They are rigorous evidence, bounded by the tasks you define and the confidence levels you configure. Veritas makes this distinction explicit in every report.

---

## 🤝 Contributing

Contributions are welcome. Please see the [examples/](examples/) directory for reference implementations and the [extension guide](#-extending-veritas) for adding custom scorers and adapters.

```bash
# Development setup
git clone https://github.com/your-org/veritas-evalengine.git
cd veritas-evalengine
pip install -e ".[all,dev]"

# Run tests before submitting
pytest tests/ -m "not provider and not benchmark" --cov=veritas_evalengine
ruff check src/ tests/
mypy src/veritas_evalengine/
```

---

## 📜 License

Apache License 2.0 — see [LICENSE](LICENSE) for full text.

---

<p align="center">
  <strong>Stop guessing. Start proving.</strong>
  <br/>
  <em>Veritas EvalEngine — because "it seems to work" isn't a release criterion.</em>
</p>
