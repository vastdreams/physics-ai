# Context Memory System Documentation

## Overview

The Context Memory System is an intelligent, hierarchical memory architecture inspired by DREAM's "traffic-direction agents" with micro-maps. It provides atomic context units (bubbles) with embedded micro-agents that manage intelligent pathfinding through a knowledge graph.

## Architecture

### Core Components

#### 1. ContextBubble
Atomic unit of context with embedded micro-agents and traffic signals.

**Mathematical Foundation**:
- Bubble: $B = \{content, metadata, micro\_agents, traffic\_signals\}$
- Traffic signals: $T = \{pathway: weight\}$ where $weight \in [0, 1]$

**Key Features**:
- Atomic context storage
- Micro-agent embedding
- Traffic signal management
- Access tracking

**Usage**:
```python
from ai.context_memory import ContextBubble

bubble = ContextBubble(
    bubble_id="bubble_001",
    content={"data": "example"},
    metadata={"source": "api"}
)

# Add micro-agent
from ai.context_memory import MicroAgent
agent = MicroAgent(
    agent_id="agent_001",
    blueprint={"instructions": {"type": "route"}}
)
bubble.add_micro_agent(agent)

# Set traffic signal
bubble.set_traffic_signal("pathway_1", 0.8)
```

#### 2. MicroAgent
Sub-agentic structure within context bubbles for intelligent routing.

**Mathematical Foundation**:
- Agent: $A = \{blueprint, state, pathway\_map\}$
- Pathway map: $P = \{pathway: confidence\}$ where $confidence \in [0, 1]$

**Key Features**:
- Blueprint-based execution
- Pathway confidence tracking
- Context processing
- Traffic signal updates

**Usage**:
```python
from ai.context_memory import MicroAgent

agent = MicroAgent(
    agent_id="agent_001",
    blueprint={
        "instructions": {"type": "route", "pathways": ["path1", "path2"]},
        "constraints": ["has_energy"]
    }
)

# Process query
result = agent.process({"energy": 10.0}, bubble)
```

#### 3. TrafficAgent
Intelligent pathfinding through context tree using Dijkstra's algorithm.

**Mathematical Foundation**:
- Pathfinding: $P = \{bubble_1 \to bubble_2 \to ... \to bubble_n\}$
- Weight: $w(edge) = 1 / (traffic\_signal + 0.1)$
- Algorithm: Dijkstra's with traffic-weighted edges

**Key Features**:
- Optimal pathfinding
- Usage tracking
- Pathway management
- Statistics collection

**Usage**:
```python
from ai.context_memory import TrafficAgent, ContextTree

tree = ContextTree()
agent = TrafficAgent(tree)

# Find path
path = agent.find_path("bubble_1", "bubble_5", max_depth=10)
```

#### 4. ContextTree
Hierarchical organization of context bubbles.

**Mathematical Foundation**:
- Tree: $T = (B, E)$ where $B$ = bubbles, $E$ = edges
- Hierarchy: Parent-child relationships
- Depth: $depth(child) = depth(parent) + 1$

**Key Features**:
- Hierarchical organization
- Depth tracking
- Tree traversal
- Subtree extraction

**Usage**:
```python
from ai.context_memory import ContextTree, ContextBubble

tree = ContextTree()

# Add root bubble
root = ContextBubble(bubble_id="root", content={})
tree.add_bubble(root)

# Add child bubble
child = ContextBubble(bubble_id="child", content={})
tree.add_bubble(child, parent_id="root")

# Traverse tree
bubble_ids = tree.traverse_depth_first("root")
```

#### 5. PathOptimizer
Route optimization based on usage patterns.

**Mathematical Foundation**:
- Optimization: Minimize $C(path) = \sum weight(edge)$
- Adaptive: Update weights based on usage
- Refinement: Remove unnecessary hops

**Key Features**:
- Path refinement
- Weight adjustment
- Performance tracking
- Adaptive optimization

**Usage**:
```python
from ai.context_memory import PathOptimizer, TrafficAgent, ContextTree

tree = ContextTree()
traffic_agent = TrafficAgent(tree)
optimizer = PathOptimizer(traffic_agent)

# Optimize path
optimized_path = optimizer.optimize_path("start", "target", tree)
```

#### 6. UsageTracker
Track pathway usage and statistics.

**Mathematical Foundation**:
- Usage tracking: $U = \{pathway: count\}$ over time
- Statistics: Mean, variance, trends
- Hot/cold identification: Based on usage frequency

**Key Features**:
- Usage recording
- Statistics computation
- Trend analysis
- Hot/cold pathway identification

**Usage**:
```python
from ai.context_memory import UsageTracker

tracker = UsageTracker(retention_days=30)

# Record usage
tracker.record_usage("pathway_1", metadata={"source": "api"})

# Get statistics
stats = tracker.get_pathway_statistics("pathway_1")

# Get hot pathways
hot_pathways = tracker.get_hot_pathways(limit=10)
```

## API Endpoints

### Context Tree
- `GET /api/v1/context/tree` - Get context tree structure
- `GET /api/v1/context/bubbles` - List all context bubbles
- `POST /api/v1/context/bubbles` - Create context bubble
- `POST /api/v1/context/pathways` - Find pathway between bubbles
- `POST /api/v1/context/pathways/optimize` - Optimize pathways
- `GET /api/v1/context/statistics` - Get context memory statistics

### Example API Usage

```python
import requests

# Create context bubble
response = requests.post('http://localhost:5000/api/v1/context/bubbles', json={
    "content": {"data": "example"},
    "metadata": {"source": "api"},
    "parent_id": None
})

# Find pathway
response = requests.post('http://localhost:5000/api/v1/context/pathways', json={
    "start_bubble_id": "bubble_1",
    "target_bubble_id": "bubble_5",
    "max_depth": 10
})
```

## Mathematical Foundations

### Traffic Signal Weighting
Traffic signals are weighted based on usage:
$$w_i = \frac{usage_i}{\max(usage)}$$

### Pathfinding Algorithm
Dijkstra's algorithm with traffic-weighted edges:
$$weight(edge) = \frac{1}{traffic\_signal + 0.1}$$

### Pathway Optimization
Path cost minimization:
$$C(path) = \sum_{edge \in path} weight(edge)$$

## Performance Considerations

- **Pathfinding**: O(n log n) with Dijkstra's algorithm
- **Tree Traversal**: O(n) for depth-first traversal
- **Cache Lookup**: O(1) for hash-based operations
- **Usage Tracking**: O(1) for recording, O(n) for statistics

## Best Practices

1. **Bubble Creation**: Keep bubbles atomic and focused
2. **Micro-Agents**: Use for routing decisions, not heavy computation
3. **Traffic Signals**: Update based on actual usage patterns
4. **Path Optimization**: Run periodically, not on every request
5. **Usage Tracking**: Set appropriate retention periods

## Integration Examples

### With Physics Integrator
```python
from ai.context_memory import ContextTree, ContextBubble
from physics.integration.physics_integrator import PhysicsIntegrator

tree = ContextTree()
integrator = PhysicsIntegrator()

# Create bubble for simulation result
result = integrator.simulate(...)
bubble = ContextBubble(
    bubble_id="sim_result_001",
    content=result,
    metadata={"type": "simulation"}
)
tree.add_bubble(bubble)
```

### With Chain-of-Thought Logging
```python
from ai.context_memory import ContextBubble
from utilities.cot_logging import ChainOfThoughtLogger

cot = ChainOfThoughtLogger()
step_id = cot.start_step(action="CREATE_BUBBLE", level=LogLevel.INFO)

bubble = ContextBubble(...)
# ... operations ...

cot.end_step(step_id, output_data={"bubble_id": bubble.bubble_id})
```

## Future Enhancements

1. **Persistence**: Database storage for context bubbles
2. **Distributed**: Multi-node context tree
3. **Advanced Analytics**: Machine learning for pathway prediction
4. **Visualization**: Graph visualization of context tree
5. **Compression**: Efficient storage of large context trees

