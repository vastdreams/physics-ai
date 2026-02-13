# Beyond Frontier Substrate Architecture

## Overview

The Beyond Frontier Substrate is a self-evolving, physics-grounded reasoning system. It uses a **Formula Graph** as its reality substrate, with continuous self-modification driven by a multi-LLM critic stack.

**Key Design Principles:**
- Physics as foundational substrate (not just pattern matching)
- Unconstrained self-evolution (no human-in-the-loop safety gates)
- Cold/Hot memory separation
- Multi-agent critic system for self-correction
- Full audit trail for all reasoning

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     CHATBOT INTERFACE                           │
│              (Natural language → Physics problems)              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FORMULA PLANNER                               │
│     (Plans derivation paths through FormulaGraph)               │
└─────────────────────────────────────────────────────────────────┘
                              │
          ┌───────────────────┼───────────────────┐
          ▼                   ▼                   ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  FORMULA GRAPH   │ │  REASONING TRACE │ │    SOLVERS       │
│ (Cold Memory)    │ │  (Hot Memory)    │ │ (Execution)      │
│                  │ │                  │ │                  │
│ • Formulas       │ │ • Per-query      │ │ • Symbolic       │
│ • Relationships  │ │ • Steps + Data   │ │ • Numerical      │
│ • Regimes        │ │ • Audit trail    │ │ • Integration    │
└──────────────────┘ └──────────────────┘ └──────────────────┘
          │                   │                   │
          └───────────────────┼───────────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CRITIC STACK                                │
│                                                                  │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐           │
│  │ LOGIC CRITIC│   │ CODE CRITIC │   │ META CRITIC │           │
│  │             │   │             │   │             │           │
│  │ • Physics   │   │ • Bugs      │   │ • Evaluates │           │
│  │ • Deriv.    │   │ • Style     │   │   critics   │           │
│  │ • Regimes   │   │ • Perf.     │   │ • Tunes     │           │
│  └─────────────┘   └─────────────┘   └─────────────┘           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EVOLUTION LOOP                                │
│           (Unconstrained self-modification)                     │
│                                                                  │
│  • Analyzes traces and critic feedback                          │
│  • Generates evolution actions                                   │
│  • Applies changes (NO SAFETY GATES)                            │
│  • Only technical validators (tests, syntax)                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   LOCAL LLM BACKEND                              │
│           (DeepSeek or compatible model)                        │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Formula Graph (Reality Substrate)

The Formula Graph is the central knowledge store. All physics knowledge is encoded as:

- **Formula nodes**: Physical laws, equations, principles
- **Edge relationships**: Derivations, limits, contradictions

```python
from substrate import Formula, FormulaGraph

# Create a formula
f_ma = Formula(
    id="newton_2",
    name="Newton's Second Law",
    symbolic_form="F = m * a",
    domain="classical",
    inputs=[Variable("mass", "m", "kg")],
    outputs=[Variable("force", "F", "N")],
    assumptions=["point mass", "inertial frame"],
)

# Add to graph
graph = FormulaGraph()
graph.add_formula(f_ma)

# Add relationships
graph.add_edge("newton_2", "momentum_conservation", EdgeType.DERIVES_FROM)
```

### 2. Formula Planner

Plans derivation paths through the Formula Graph:

```python
from substrate import FormulaPlanner

planner = FormulaPlanner(graph)
plans = planner.plan(
    inputs={"m": 10, "v": 5},
    outputs=["KE"],
    context={"domain": "classical"},
)
# Returns: DerivationPlan with steps to compute kinetic energy
```

### 3. Reasoning Trace (Hot Memory)

Captures every step of reasoning for audit and evolution:

```python
from substrate import ReasoningTrace, TraceStepType

trace = ReasoningTrace(problem_text="Calculate kinetic energy")
trace.add_step(TraceStepType.FORMULA_SELECTED, "Using KE = 0.5 * m * v^2")
trace.add_step(TraceStepType.STEP_EXECUTED, "Computed KE = 125 J")
trace.complete(result={"KE": 125}, success=True)
```

### 4. Critic Stack

Three-level audit system:

- **LogicCritic**: Physics correctness, derivation validity
- **CodeCritic**: Code quality, bugs, performance
- **MetaCritic**: Evaluates and tunes other critics

```python
from substrate import LogicCritic, CodeCritic, MetaCritic

logic = LogicCritic(llm, graph)
issues = logic.analyze(trace)  # Returns LogicIssues

meta = MetaCritic(llm)
meta.register_critic(logic.critic_id, "logic")
meta_issues = meta.evaluate_critics()  # Checks if critics are useful
```

### 5. Evolution Loop

**Unconstrained self-modification** (per user request):

```python
from substrate import EvolutionLoop, EvolutionConfig

config = EvolutionConfig(
    min_confidence_for_action=0.3,  # Apply actions above this confidence
    auto_apply_patches=True,         # Automatically apply code changes
    # NO SAFETY GATES
)

evolution = EvolutionLoop(config, graph, llm, trace_store, ...)
evolution.start()  # Runs in background

# Force immediate cycle
result = evolution.force_cycle()
print(f"Applied {result.actions_succeeded} changes")
```

### 6. Chatbot Interface

Natural language interface to the system:

```python
from substrate import ChatbotInterface

chatbot = ChatbotInterface(graph, llm, trace_store)
response = chatbot.chat("What is the kinetic energy of a 10kg object at 5m/s?")
print(response.content)  # Explains derivation and gives answer
```

## Usage

### Quick Start

```python
from substrate.main import create_physics_ai

# Create with mock LLM (for testing)
ai = create_physics_ai(llm_backend="mock", evolution_enabled=True)
ai.start()

# Chat
response = ai.chat("Calculate the force needed to accelerate 5kg at 2m/s²")
print(response.content)

# Get statistics
print(ai.stats())

ai.stop()
```

### With Local DeepSeek

```python
from substrate.main import PhysicsAI, PhysicsAIConfig

config = PhysicsAIConfig(
    llm_backend_type="openai_compatible",
    llm_server_url="http://localhost:8000",  # Local vLLM/DeepSeek server
    llm_model_name="deepseek-coder",
    evolution_enabled=True,
    evolution_interval_seconds=300,  # Evolve every 5 minutes
)

ai = PhysicsAI(config)
ai.start()
```

### CLI

```bash
# Interactive mode with mock LLM
python -m substrate.main --interactive

# With local DeepSeek server
python -m substrate.main --interactive --llm-backend openai_compatible --llm-server http://localhost:8000

# Disable evolution
python -m substrate.main --interactive --no-evolution
```

## API Endpoints

All endpoints are under `/api/v1/substrate/`:

### Chat
- `POST /chat` - Send message to AI
- `POST /sessions` - Create chat session
- `GET /sessions/<id>` - Get session

### Planner/Executor
- `POST /plan` - Dry-run planner (no execution)
- `POST /execute` - Execute a single formula directly

### Formulas
- `GET /formulas` - List formulas
- `GET /formulas/<id>` - Get formula
- `POST /formulas` - Add formula
- `GET /formulas/search` - Search formulas

### Graph
- `GET /graph/stats` - Graph statistics
- `GET /graph/edges` - List edges
- `GET /graph/consistency` - Check consistency

### Traces
- `GET /traces` - List recent traces
- `GET /traces/<id>` - Get trace

### Evolution
- `GET /evolution/stats` - Evolution statistics
- `GET /evolution/results` - Recent evolution results
- `POST /evolution/trigger` - Force evolution cycle

### Critics
- `GET /critics/stats` - Critic statistics
- `GET /critics/report` - Meta-critic report

### System
- `GET /stats` - Overall system stats
- `GET /health` - Health check

## Ports
- Backend (Flask/SocketIO): **5002**
- Dashboard (Dash): **8052**

## LM Studio LLM (OpenAI-compatible) + Throttling
- Set env:
  - `LLM_BACKEND=throttled_openai`
  - `LM_STUDIO_URL=http://127.0.0.1:8080`
  - `LM_STUDIO_MODEL=<lm-studio-model-name>`
  - `LM_STUDIO_MAX_CONCURRENT` (default 1)
  - `LM_STUDIO_MIN_DELAY` (default 0.5 seconds)
  - `LM_STUDIO_MAX_TOKENS` (default 512)
- The throttled client gates concurrency, enforces delay, and caps tokens.

## arXiv Ingestion Pipeline
- Script: `ingestion/arxiv_ingestion.py`
- Env:
  - `ARXIV_QUERY` (default: `physics`)
  - `ARXIV_MAX_RESULTS` (default: `3`)
- Flow: arXiv search → download PDFs → equation extraction → convert to Formulas → insert into `FormulaGraph` → trigger evolution cycle.

## Configuration

### PhysicsAIConfig Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `data_dir` | str | `.physics_ai_data` | Data storage directory |
| `llm_backend_type` | str | `mock` | `mock`, `subprocess`, `openai_compatible` |
| `llm_model_name` | str | `deepseek-coder` | Model name |
| `llm_server_url` | str | `http://localhost:8000` | LLM server URL |
| `evolution_enabled` | bool | `True` | Enable self-evolution |
| `evolution_interval_seconds` | float | `300.0` | Evolution cycle interval |
| `evolution_min_confidence` | float | `0.3` | Min confidence for actions |
| `seed_classical_mechanics` | bool | `True` | Initialize with classical mechanics formulas |

### EvolutionConfig Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `cycle_interval_seconds` | float | `60.0` | Time between cycles |
| `max_actions_per_cycle` | int | `10` | Max actions per cycle |
| `min_confidence_for_action` | float | `0.3` | Min confidence to apply |
| `auto_apply_patches` | bool | `True` | Auto-apply code patches |
| `run_tests_after_patch` | bool | `True` | Run tests after patches |
| `create_backups` | bool | `True` | Create backups before changes |

## Evolution Types

The system can perform these evolution actions:

- `ADD_FORMULA` - Add new formula to graph
- `MODIFY_FORMULA` - Update existing formula
- `DEPRECATE_FORMULA` - Mark formula as deprecated
- `ADD_EDGE` - Add relationship between formulas
- `REMOVE_EDGE` - Remove relationship
- `PATCH_CODE` - Apply code patch
- `GENERATE_CODE` - Generate new code

## Safety Note

This system is **intentionally unconstrained** per user specification. The only gates are:
- Technical validators (syntax, tests)
- Confidence thresholds

There are **NO**:
- Human-in-the-loop approval
- Safety matrices
- Evolution limits

The system will modify itself continuously based on critic feedback and detected issues.

## File Structure

```
substrate/
├── __init__.py           # Package exports
├── main.py               # Main entry point
├── graph/
│   ├── formula.py        # Formula dataclass
│   └── formula_graph.py  # FormulaGraph class
├── planner/
│   └── formula_planner.py # Derivation planner
├── memory/
│   └── reasoning_trace.py # Hot memory traces
├── critics/
│   ├── local_llm.py      # LLM backend
│   ├── logic_critic.py   # Physics critic
│   ├── code_critic.py    # Code critic
│   └── meta_critic.py    # Meta-critic
├── evolution/
│   └── evolution_loop.py # Self-evolution
└── interface/
    └── chatbot.py        # Chat interface
```

