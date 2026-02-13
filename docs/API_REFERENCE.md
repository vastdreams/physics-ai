# Beyond Frontier - API Reference

## Overview

Beyond Frontier provides a comprehensive REST API for physics simulations, reasoning, and AI-powered analysis.

**Base URL**: `http://localhost:5002`

---

## Authentication

Currently, the API does not require authentication for local development. For production deployments, set the `FLASK_SECRET_KEY` environment variable and implement appropriate authentication middleware.

---

## Endpoints

### Health Check

#### `GET /health`

Check API health status.

**Response:**
```json
{
  "status": "healthy"
}
```

---

### Simulation

#### `POST /api/v1/simulate`

Run a physics simulation.

**Request Body:**
```json
{
  "model": "harmonic_oscillator",
  "parameters": {
    "mass": 1.0,
    "spring_constant": 4.0,
    "damping": 0.0
  },
  "initial_conditions": {
    "x": 1.0,
    "v": 0.0
  },
  "t_start": 0.0,
  "t_end": 10.0,
  "dt": 0.01,
  "method": "rk4"
}
```

**Available Models:**
- `harmonic_oscillator` - Simple/damped harmonic oscillator
- `pendulum` - Simple pendulum (small and large angles)
- `two_body_gravity` - Two-body gravitational system
- `projectile_motion` - Projectile with optional drag

**Integration Methods:**
- `euler` - Euler method (fast, less accurate)
- `rk4` - 4th order Runge-Kutta (recommended)
- `rk45` - Adaptive Runge-Kutta (scipy)

**Response:**
```json
{
  "success": true,
  "states": [...],
  "times": [...],
  "method_used": "rk4",
  "conservation_violations": [],
  "metadata": {
    "dt": 0.01,
    "num_steps": 1001,
    "model_type": "harmonic_oscillator"
  }
}
```

---

### Nodes (Code Graph)

#### `GET /api/v1/nodes`

List all code nodes in the graph.

**Query Parameters:**
- `limit` (int, optional): Maximum nodes to return
- `type` (string, optional): Filter by node type

**Response:**
```json
{
  "nodes": [
    {
      "id": "node_1",
      "name": "engine.py",
      "type": "module",
      "dependencies": ["validator.py", "logger.py"]
    }
  ],
  "total": 42
}
```

#### `GET /api/v1/nodes/<node_id>`

Get details of a specific node.

#### `POST /api/v1/nodes/analyze`

Analyze a code file or directory.

**Request Body:**
```json
{
  "path": "core/engine.py",
  "include_dependencies": true
}
```

#### `GET /api/v1/nodes/graph/statistics`

Get graph statistics.

---

### Rules

#### `GET /api/v1/rules`

List all rules.

#### `POST /api/v1/rules`

Add a new rule.

**Request Body:**
```json
{
  "name": "kinetic_energy_rule",
  "condition": {
    "mass": {"$gt": 0},
    "velocity": {"$exists": true}
  },
  "action": {
    "$compute": {
      "expression": "0.5 * mass * velocity ** 2",
      "target": "kinetic_energy"
    }
  },
  "priority": 10
}
```

**Condition Operators:**
- `$gt`, `$gte`, `$lt`, `$lte` - Comparisons
- `$eq`, `$ne` - Equality
- `$in`, `$nin` - Set membership
- `$exists` - Field existence
- `$and`, `$or`, `$not` - Logical operators
- `$regex` - Pattern matching

**Action Types:**
- `$set` - Set values
- `$compute` - Evaluate expression
- `$call` - Call registered function
- `$remove` - Remove keys
- `$return` - Return value

#### `GET /api/v1/rules/<rule_name>`

Get a specific rule.

#### `POST /api/v1/rules/execute`

Execute rules on a context.

**Request Body:**
```json
{
  "context": {
    "mass": 10,
    "velocity": 5
  }
}
```

#### `GET /api/v1/rules/statistics`

Get rule engine statistics.

---

### Evolution

#### `POST /api/v1/evolution/analyze`

Analyze codebase for improvement opportunities.

**Request Body:**
```json
{
  "directory": "core/",
  "include_metrics": true
}
```

#### `POST /api/v1/evolution/evolve`

Evolve a specific function.

**Request Body:**
```json
{
  "file_path": "core/engine.py",
  "function_name": "process",
  "improvement_spec": {
    "type": "optimize",
    "target": "performance"
  }
}
```

#### `GET /api/v1/evolution/history`

Get evolution history.

#### `POST /api/v1/evolution/rollback`

Rollback a code change.

**Request Body:**
```json
{
  "file_path": "core/engine.py"
}
```

---

### Chain-of-Thought

#### `GET /api/v1/cot/tree`

Get the chain-of-thought reasoning tree.

#### `GET /api/v1/cot/statistics`

Get CoT statistics.

#### `POST /api/v1/cot/export`

Export reasoning logs.

**Request Body:**
```json
{
  "format": "json",
  "start_time": "2024-01-01T00:00:00Z",
  "end_time": "2024-12-31T23:59:59Z"
}
```

---

### VECTOR Framework

#### `POST /api/v1/vector/delta-factors`

Add delta factors for uncertainty management.

**Request Body:**
```json
{
  "parameter": "energy",
  "delta": 0.05,
  "source": "measurement_error"
}
```

#### `POST /api/v1/vector/throttle`

Apply variance throttling.

**Request Body:**
```json
{
  "variance": 0.1,
  "max_variance": 0.5
}
```

#### `POST /api/v1/vector/bayesian-update`

Perform Bayesian parameter update.

**Request Body:**
```json
{
  "prior_mean": 1.0,
  "prior_variance": 0.1,
  "observation": 1.05,
  "observation_variance": 0.02
}
```

#### `POST /api/v1/vector/overlay-validation`

Validate complex model against simple overlay.

#### `GET /api/v1/vector/statistics`

Get VECTOR framework statistics.

---

### State Graph

#### `POST /api/v1/state-graph/states`

Add or query states.

#### `POST /api/v1/state-graph/paths`

Find paths between states.

**Request Body:**
```json
{
  "from_state": "initial",
  "to_state": "equilibrium",
  "max_steps": 10
}
```

#### `POST /api/v1/state-graph/scenarios`

Explore scenarios.

---

### Context Memory

#### `GET /api/v1/context/tree`

Get context tree structure.

#### `GET /api/v1/context/bubbles`

List context bubbles.

#### `POST /api/v1/context/bubbles`

Create a new context bubble.

#### `POST /api/v1/context/pathways`

Create context pathway.

#### `POST /api/v1/context/pathways/optimize`

Optimize context pathway.

#### `GET /api/v1/context/statistics`

Get context memory statistics.

---

### Equational AI

#### `POST /api/v1/equational/ingest`

Ingest equations from text or documents.

**Request Body:**
```json
{
  "text": "E = mc^2",
  "source": "einstein_1905"
}
```

#### `GET /api/v1/equational/equations`

List all equations.

#### `GET /api/v1/equational/equations/<eq_id>`

Get specific equation.

#### `POST /api/v1/equational/validate`

Validate an equation.

#### `GET /api/v1/equational/permanence`

Get equation permanence score.

---

### Brain Modal

#### `POST /api/v1/brain/feedback`

Submit human feedback.

#### `POST /api/v1/brain/audit`

Audit AI decision.

#### `POST /api/v1/brain/review`

Request human review.

#### `GET /api/v1/brain/feedback-history`

Get feedback history.

---

## WebSocket Events

Connect to WebSocket at `ws://localhost:5002/socket.io/`

### Events

| Event | Direction | Description |
|-------|-----------|-------------|
| `connect` | Server → Client | Connection established |
| `simulation_update` | Server → Client | Simulation progress |
| `evolution_status` | Server → Client | Evolution progress |
| `rule_fired` | Server → Client | Rule execution notification |
| `error` | Server → Client | Error notification |

---

## Error Handling

All endpoints return errors in this format:

```json
{
  "error": "Error message",
  "code": "ERROR_CODE",
  "details": {}
}
```

**Common Error Codes:**
- `VALIDATION_ERROR` - Invalid request data
- `NOT_FOUND` - Resource not found
- `INTERNAL_ERROR` - Server error
- `RATE_LIMITED` - Too many requests

---

## Rate Limiting

Default limits (configurable):
- 100 requests per minute per IP
- 10 concurrent simulations

---

## Examples

### Python Client

```python
import requests

BASE_URL = "http://localhost:5002"

# Run simulation
response = requests.post(f"{BASE_URL}/api/v1/simulate", json={
    "model": "harmonic_oscillator",
    "parameters": {"mass": 1.0, "spring_constant": 4.0},
    "initial_conditions": {"x": 1.0, "v": 0.0},
    "t_end": 10.0
})
result = response.json()
print(f"Simulation completed: {len(result['states'])} states")
```

### cURL

```bash
# Add a rule
curl -X POST http://localhost:5002/api/v1/rules \
  -H "Content-Type: application/json" \
  -d '{"name": "test_rule", "condition": {}, "action": {"$return": "success"}}'

# Execute rules
curl -X POST http://localhost:5002/api/v1/rules/execute \
  -H "Content-Type: application/json" \
  -d '{"context": {"x": 5}}'
```

---

## Changelog

### v1.0.0
- Initial API release
- Core simulation endpoints
- Rule engine API
- Evolution endpoints
- VECTOR framework
