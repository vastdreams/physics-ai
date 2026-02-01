# Additional DREAM-Inspired Patterns

## Overview

This document describes additional sophisticated patterns extracted from the DREAM architecture that enhance the Physics AI system with advanced state management, workflow orchestration, and traceability.

## New Patterns Implemented

### 1. State Graph System (`utilities/state_graph.py`)

**Inspired by**: DREAM Section 1.3 - "Time-State and Scenario Testing"

**Purpose**: Model branching possibilities and track feasible transitions through state space.

**Features**:
- **State Representation**: States with properties and constraints
- **Transition Tracking**: Conditional, probabilistic, temporal transitions
- **Path Finding**: Find all paths between states
- **Scenario Exploration**: Explore multiple routes to reach target properties
- **Constraint Validation**: Ensure transitions respect physics constraints

**Mathematical Foundation**:
- Graph: $G = (S, T)$ where $S$ = states, $T$ = transitions
- Path finding: Find all paths $P = \{s_1 \rightarrow s_2 \rightarrow ... \rightarrow s_n\}$
- Scenario testing: Explore paths that satisfy target properties

**Usage**:
```python
from utilities.state_graph import StateGraph, State, Transition, TransitionType

graph = StateGraph()

# Add states
state1 = State(state_id="low_energy", name="Low Energy State", properties={'energy': 0.1})
state2 = State(state_id="high_energy", name="High Energy State", properties={'energy': 10.0})
graph.add_state(state1)
graph.add_state(state2)

# Add transition
def condition(ctx):
    return ctx.get('energy', 0) > 5.0

transition = Transition(
    from_state="low_energy",
    to_state="high_energy",
    condition=condition,
    transition_type=TransitionType.CONDITIONAL
)
graph.add_transition(transition)

# Find paths
paths = graph.find_paths("low_energy", "high_energy", max_depth=10)

# Explore scenarios
scenarios = graph.explore_scenarios(
    initial_state="low_energy",
    target_properties={'energy': 10.0},
    max_steps=10
)
```

### 2. Command & Control (C2) Center (`utilities/command_control.py`)

**Inspired by**: DREAM Section 4.3.3.6.2.1 - "Command and Control Center"

**Purpose**: Central orchestrator for algorithm selection and workflow management.

**Features**:
- **Algorithm Selection**: Choose MCMC vs Particle Filter based on problem characteristics
- **Decision Logic**: 
  - Real-time streaming + many factors → Particle Filters
  - Smaller dimension or offline → MCMC
  - High uncertainty → MHA for weighting
- **Variance Checks**: Automatic variance throttling
- **MHA Triggering**: Trigger Multi-Head Attention when needed
- **Overlay Validation**: Compare simple vs complex models
- **Workflow Orchestration**: Execute complete workflows

**Usage**:
```python
from utilities.command_control import CommandControlCenter, AlgorithmType

c2 = CommandControlCenter()

# Select algorithm
decision = c2.select_algorithm(
    problem_type="parameter_estimation",
    data_dimension=15,
    is_real_time=True
)
# Returns: AlgorithmType.PARTICLE_FILTER

# Check variance
throttled, stats = c2.check_variance(v_max=100.0)

# Trigger MHA
output, weights = c2.trigger_mha(
    queries=[...],
    keys=[...],
    values=[...],
    variances=[0.1, 0.2, 0.15]
)

# Orchestrate workflow
workflow = [
    {'type': 'variance_check', 'data': {'v_max': 100.0}},
    {'type': 'mha', 'data': {...}},
    {'type': 'overlay_validation', 'data': {...}}
]
result = c2.orchestrate_workflow(workflow, context={})
```

### 3. Function Flow Registry (`utilities/function_flow_registry.py`)

**Inspired by**: DREAM code patterns - `register_function_flow` and `log_node`

**Purpose**: Automatic traceability of function execution with dependency tracking.

**Features**:
- **Automatic Logging**: Wrap functions to log every call
- **Node Creation**: Each function call becomes a node
- **Dependency Tracking**: Track parent-child relationships
- **Execution Graphs**: Generate complete execution traces
- **Performance Metrics**: Track execution time and success rates

**Usage**:
```python
from utilities.function_flow_registry import FunctionFlowRegistry

registry = FunctionFlowRegistry()

# Register function with flow tracking
@registry.register_function_flow(dependencies=["dependency_func"])
def my_function(x, y):
    return x + y

# Function automatically logged when called
result = my_function(1, 2)

# Get execution trace
trace = registry.get_flow_trace("flow_my_function_...")

# Get execution graph
graph = registry.get_execution_graph("flow_my_function_...")
```

### 4. Confidence Weighting System (`utilities/confidence_weighting.py`)

**Inspired by**: DREAM architecture - `w_confidence(t)` for down-weighting uncertain expansions

**Purpose**: Dynamically weight expansions based on uncertainty.

**Features**:
- **Variance-Based Weighting**: $w = f(\sigma^2)$ where $f$ is decreasing
- **Multiple Strategies**:
  - Exponential: $w = \exp(-\lambda \times \sigma^2)$
  - Linear: $w = \max(0, 1 - \sigma^2/\sigma^2_{\text{threshold}})$
  - Inverse: $w = 1 / (1 + \sigma^2)$
- **Time-Dependent**: Weights can update as data arrives
- **Automatic Down-Weighting**: Uncertain expansions automatically receive lower weights

**Usage**:
```python
from utilities.confidence_weighting import ConfidenceWeighting

weighting = ConfidenceWeighting()

# Set weights based on variance
weighting.set_weight("expansion1", variance=0.1, strategy="exponential")
weighting.set_weight("expansion2", variance=0.5, strategy="exponential")

# Apply weights to values
values = {"expansion1": 1.0, "expansion2": 0.5}
weighted = weighting.apply_weights(values)
# expansion1: 1.0 * 0.9 = 0.9 (high confidence)
# expansion2: 0.5 * 0.6 = 0.3 (low confidence)
```

### 5. Synergy Expansion Engine (`utilities/synergy_expansion.py`)

**Inspired by**: DREAM architecture - Advanced synergy with interaction terms

**Purpose**: Compute net synergy with interaction terms and regularization.

**Features**:
- **Base Expansions**: $S_i$ for individual expansions
- **Interaction Terms**: $w_{ij} S_i S_j$ for pairwise interactions
- **Log-Space Calculations**: $\log(S_{\text{net}}) = \sum \log(1+\delta_i) + \sum w_{ij} \delta_i \delta_j$
- **Group-Lasso Regularization**: Zero out small interaction terms
- **Validation**: Check expansions against first-principles

**Mathematical**:
- Linear: $S_{\text{net}} = \sum S_i + \sum w_{ij} S_i S_j$
- Log-space: $\log(S_{\text{net}}) = \sum \log(1+\delta_i) + \sum w_{ij} \delta_i \delta_j$

**Usage**:
```python
from utilities.synergy_expansion import SynergyExpansionEngine, SynergyExpansion

engine = SynergyExpansionEngine()

# Create expansion with interaction terms
expansion = SynergyExpansion(
    name="theory_unification",
    base_value=1.0,
    delta_factors=["classical", "quantum"],
    interaction_terms={("classical", "quantum"): 0.1}
)
engine.add_expansion(expansion)

# Compute net synergy
delta_values = {"classical": 0.5, "quantum": 0.3}
net_synergy = engine.compute_net_synergy(
    expansion_names=["theory_unification"],
    delta_values=delta_values,
    use_log_space=True
)

# Apply regularization
regularized = engine.apply_group_lasso_regularization(lambda_reg=0.05)
```

## Integration with Existing Systems

### State Graph + Physics Integrator
- Track state transitions during simulations
- Explore different theory combinations
- Validate transitions against physics constraints

### C2 Center + All Systems
- Central orchestration point
- Algorithm selection for different problems
- Workflow management across components

### Function Flow Registry + Evolution
- Track code evolution steps
- Log all function calls during evolution
- Generate execution traces for debugging

### Confidence Weighting + VECTOR
- Integrate with VECTOR framework
- Down-weight uncertain delta factors
- Automatic uncertainty propagation

### Synergy Expansion + Theory Synergy
- Enhance theory synergy with interaction terms
- Regularize coupling constants
- Validate against first-principles

## API Endpoints

### State Graph
- `POST /api/v1/state-graph/states`: Add state
- `POST /api/v1/state-graph/paths`: Find paths
- `POST /api/v1/state-graph/scenarios`: Explore scenarios

## Mathematical Foundations

### State Transitions
- Graph: $G = (S, T)$
- Path: $P = s_1 \rightarrow s_2 \rightarrow ... \rightarrow s_n$
- Scenario: Path satisfying target properties

### Confidence Weighting
- Exponential: $w = \exp(-\lambda \sigma^2)$
- Linear: $w = \max(0, 1 - \sigma^2/\sigma^2_{\text{thresh}})$
- Inverse: $w = 1/(1 + \sigma^2)$

### Synergy Expansion
- Linear: $S_{\text{net}} = \sum S_i + \sum w_{ij} S_i S_j$
- Log-space: $\log(S_{\text{net}}) = \sum \log(1+\delta_i) + \sum w_{ij} \delta_i \delta_j$
- Regularization: $w_{ij} = 0$ if $|w_{ij}| < \lambda$

## Key Insights from DREAM

1. **State-Based Thinking**: Model systems as state graphs with transitions
2. **Central Orchestration**: C2 Center for algorithm selection
3. **Complete Traceability**: Function flow registry for debugging
4. **Uncertainty Propagation**: Confidence weighting for safe expansions
5. **Interaction Terms**: Synergy expansions with pairwise interactions

## References

- DREAM Architecture Document, Section 1.3 (Time-State and Scenario Testing)
- DREAM Architecture Document, Section 4.3.3.6.2.1 (C2 Center)
- DREAM Code Patterns (register_function_flow, log_node)

