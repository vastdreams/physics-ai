# Beyond Frontier — Contribution Checklist

## Overview

This checklist tracks the production-readiness of the Beyond Frontier project. Items are prioritized by impact and complexity. Completed items are checked off; remaining work is clearly marked.

> **Last audited**: February 2026

---

## P0 — Critical (Security & Core)

### Security Fixes

- [x] **Remove hardcoded secret key** (`api/app.py`)
  - Uses `os.getenv('FLASK_SECRET_KEY')` / `os.getenv('SECRET_KEY')` with `secrets.token_hex(32)` fallback
  - Added to `.env.example`

- [x] **Implement AST-based code validator** (`validators/code_validator.py`)
  - `DangerousNodeVisitor` detects dangerous builtins, imports, and attribute access via AST
  - `CodeComplexityVisitor` calculates cyclomatic complexity, nesting depth, function counts
  - Full `validate_all()` pipeline: syntax → safety → complexity
  - [ ] _Remaining_: Add sandboxed execution for generated code (RestrictedPython or subprocess jail)

- [x] **Implement JWT authentication** (`api/middleware/auth.py`)
  - Custom HMAC-SHA256 JWT creation & verification
  - User registration with pbkdf2 password hashing
  - Login with access + refresh tokens
  - `@require_auth`, `@require_role`, `@optional_auth` decorators
  - [ ] _Remaining_: Replace in-memory `USERS` dict with a database backend (SQLite/Postgres)

- [x] **Add rate limiting** (`api/middleware/rate_limit.py`) — **NEW**
  - Token-bucket algorithm with per-IP and per-user tracking
  - `@rate_limit()` decorator for per-route limits
  - `@rate_limit_auth` for stricter auth endpoint throttling
  - `RateLimitMiddleware` for global before-request check
  - Automatic stale-bucket cleanup
  - [ ] _Remaining_: Replace in-memory store with Redis for multi-process / multi-server setups

### Core Engine

- [x] **Neural processing** (`core/engine.py` → `NeuralComponent`)
  - Hash-based character n-gram embeddings
  - Cosine similarity search
  - Pattern learning & memory
  - Weak/strong match classification
  - [ ] _Remaining_: Integrate PyTorch for transformer-based embeddings; add pre-trained model loading

- [x] **Symbolic processing** (`core/engine.py` → `SymbolicComponent`)
  - SymPy integration: simplify, differentiate, integrate, solve, substitute
  - Rule-based inference engine with condition evaluation
  - Fact/axiom knowledge base
  - [ ] _Remaining_: Add knowledge graph querying

- [x] **Neurosymbotic integration** (`core/engine.py` → `NeurosymboticEngine`)
  - Weighted hybrid of neural + symbolic results
  - Auto mode detection based on input type
  - Self-evolution via feedback loop (alpha tuning)

---

## P1 — High Priority

### Reasoning Engine (`core/reasoning.py`)

- [x] **Deductive reasoning** — `DeductiveReasoner`
  - Modus ponens: P, P→Q ⊢ Q
  - Modus tollens: ¬Q, P→Q ⊢ ¬P
  - Hypothetical syllogism: P→Q, Q→R ⊢ P→R
  - Forward chaining with iteration limit
  - Proof-step trace

- [x] **Inductive reasoning** — `InductiveReasoner`
  - Pattern discovery across observations (constant, monotonic, linear, dominant)
  - Statistical generalization with confidence scores
  - Hypothesis formation from patterns

- [x] **Abductive reasoning** — `AbductiveReasoner`
  - Best-explanation selection
  - Bayesian-style hypothesis ranking
  - Causal reasoning support

- [x] **Analogical reasoning** — `AnalogicalReasoner`
  - Structure mapping between domains
  - Similarity metrics
  - Analogy retrieval from knowledge base

### Rule Engine (`rules/rule_engine.py`)

- [x] **Pattern matching** — `PatternMatcher`
  - Variable binding (`$var` syntax)
  - Comparison operators (`$gt`, `$lt`, `$gte`, `$lte`, `$ne`, `$eq`, `$in`, `$nin`)
  - Logical operators (`$and`, `$or`, `$not`)
  - Regex matching, type checking, existence testing
  - Nested recursive matching with match scoring

- [x] **Conflict resolution** — `ConflictResolutionStrategy`
  - Priority-based selection
  - Specificity ordering (calculated from condition complexity)
  - Recency ordering (last-fired timestamp)
  - First-match and all-match modes

- [x] **Action execution** — `ActionExecutor`
  - `$set`, `$compute`, `$call`, `$remove`, `$return` operations
  - Variable substitution from bindings
  - Expression evaluation
  - Custom action registration

### Physics Equation Solver (`physics/equations.py`)

- [x] **Equation solving**
  - SymPy-based symbolic solving with `solve()`, `solveset()`, `dsolve()`
  - Numerical fallback via SciPy (`fsolve`, `brentq`)
  - Auto-detect method (symbolic first, numerical fallback)
  - Expression parsing with implicit multiplication
  - LaTeX output support
  - [ ] _Remaining_: Full unit handling with Pint

### Physics Model Simulation (`physics/models.py`)

- [x] **Simulation engine**
  - Multiple integration methods: Euler, RK4, RK45, Adaptive
  - SciPy `solve_ivp` integration for stiff/non-stiff systems
  - State management with `SimulationState` dataclass
  - Conservation law validation (energy, momentum)
  - Boundary condition support
  - [ ] _Remaining_: PDE solvers, GPU-accelerated integration

---

## P2 — Medium Priority

### Test Coverage
- [ ] **Core engine tests** (`tests/test_core.py`) — expand with neural/symbolic integration tests
- [ ] **Reasoning tests** (create `tests/test_reasoning.py`) — test all 4 reasoning types with edge cases
- [ ] **Rule engine tests** (`tests/test_rules.py`) — expand pattern matching, conflict resolution coverage
- [ ] **Physics domain tests** (`tests/test_physics.py`) — Schrödinger accuracy, conservation law validation
- [ ] **API endpoint tests** (create `tests/test_api.py`) — all endpoints + auth + rate limiting
- [ ] **Integration tests** (`integration/`) — end-to-end physics calculations, reasoning pipeline

### LLM Integration (`ai/llm_integration.py`)
- [ ] **Real synergy extraction** — parse LLM response with NLP, extract numerical values
- [ ] **Retry logic** — exponential backoff, circuit breaker, fallback responses
- [ ] **Response caching** — TTL-based with invalidation strategy

### Physics Domains
- [ ] **Classical mechanics** (`physics/domains/classical/`) — complete Lagrangian/Hamiltonian solvers
- [ ] **Quantum mechanics** (`physics/domains/quantum/`) — path integrals, perturbation theory
- [ ] **Field theory** (`physics/domains/fields/`) — gauge transformations, EM field solver
- [ ] **Statistical mechanics** (`physics/domains/statistical/`) — ensembles, phase transitions

---

## P3 — Nice to Have

### Code Quality
- [ ] Remove `sys.path` hacks → proper `pyproject.toml` package structure
- [ ] Add comprehensive type annotations + strict mypy
- [ ] NumPy-style docstrings everywhere

### Observability
- [ ] Prometheus metrics endpoint
- [ ] OpenTelemetry distributed tracing
- [ ] Structured JSON logging

### Performance
- [ ] Redis caching layer for computations and LLM responses
- [ ] Batch physics simulations / parallel equation solving
- [ ] Profile and optimize hot paths (NumPy vectorization, Cython)

### Documentation
- [ ] OpenAPI/Swagger spec with request/response examples
- [ ] Architecture deep-dive developer guide
- [ ] Physics reference (supported equations, domain coverage, accuracy)

---

## File-by-File Status

### Core (`core/`)
| File | Status | Notes |
|------|--------|-------|
| `engine.py` | **Done** | Neural + Symbolic + Hybrid integration |
| `reasoning.py` | **Done** | All 4 reasoning types implemented |
| `knowledge_synthesis.py` | Partial | Review and complete |

### Rules (`rules/`)
| File | Status | Notes |
|------|--------|-------|
| `rule_engine.py` | **Done** | Pattern matching, conflict resolution, action execution |
| `rule_storage.py` | OK | Minor improvements |
| `rule_evolution.py` | Partial | Test and validate |
| `enhanced_rule_engine.py` | Partial | Complete implementation |
| `vector_rule_integration.py` | Partial | Test integration |

### Physics (`physics/`)
| File | Status | Notes |
|------|--------|-------|
| `equations.py` | **Done** | SymPy + SciPy numerical fallback |
| `models.py` | **Done** | Multiple integration methods + conservation laws |
| `theory_integration.py` | Partial | Complete unification |
| `domains/quantum/schrodinger.py` | OK | Add more tests |
| `domains/classical/*.py` | Partial | Complete solvers |
| `domains/fields/*.py` | Partial | Implement field equations |
| `domains/statistical/*.py` | Partial | Complete thermodynamics |

### Validators (`validators/`)
| File | Status | Notes |
|------|--------|-------|
| `code_validator.py` | **Done** | Full AST-based validation |
| `data_validator.py` | OK | Add more checks |
| `rule_validator.py` | OK | Minor improvements |

### API (`api/`)
| File | Status | Notes |
|------|--------|-------|
| `app.py` | **Done** | Secure secret key, WebSocket, hot reload |
| `middleware/auth.py` | **Done** | JWT auth, roles, registration |
| `middleware/rate_limit.py` | **Done** | Token-bucket rate limiting |
| `v1/*.py` | OK | Add input validation |

### Tests (`tests/`)
| File | Status | Notes |
|------|--------|-------|
| `test_core.py` | Minimal | Needs expansion |
| `test_physics.py` | Minimal | Needs physics validation |
| `test_rules.py` | Partial | Expand coverage |

### Frontend (`frontend/`)
| Feature | Status | Notes |
|---------|--------|-------|
| Auto-update detection | **Done** | Polls `/version.json`, shows refresh banner |
| WebSocket resilience | **Done** | Health-check-first, reconnection limits |

### CI/CD (`.github/workflows/`)
| Workflow | Status | Notes |
|----------|--------|-------|
| `ci.yml` | **Done** | Backend tests (3.10-3.12), lint, frontend build, security audit |
| `cd.yml` | **Done** | Auto-deploy on push to main, Docker build, GitHub Releases |

---

## Auto-Update Architecture

When code is pushed to `main`:

1. **CI** runs tests + lint + frontend build
2. **CD** builds the frontend with `COMMIT_SHA` embedded
3. The Vite build plugin writes `dist/version.json` with a unique `buildHash`
4. The deployed frontend's `useAutoUpdate` hook polls `/version.json` every 60 seconds
5. When the hash misses, an `UpdateBanner` appears prompting the user to refresh

```
Push to main → CI tests → CD builds → version.json updated
                                            ↓
                      Frontend polls → detects mismatch → shows banner → user refreshes
```

---

## Quick Start for Contributors

### 1. Pick an unchecked item
Focus on test coverage (P2) or physics domains — core infrastructure is solid.

### 2. Create a feature branch
```bash
git checkout -b feature/your-feature-name
```

### 3. Write tests first
```bash
pytest tests/ -v
```

### 4. Implement and validate
```bash
black --check .
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
mypy . --ignore-missing-imports
```

### 5. Submit PR
Follow the PR template in `.github/pull_request_template.md`.

---

## Estimated Remaining Effort

| Priority | Done | Remaining | Est. Hours |
|----------|------|-----------|------------|
| P0 | 7/7 | Sub-items only | 10-15 |
| P1 | 8/8 | Sub-items only | 10-20 |
| P2 | 0/9 | 9 items | 60-100 |
| P3 | 0/9 | 9 items | 40-60 |
| **Total** | **15/33** | **18 items** | **120-195** |

---

## Contact

For questions about contributing, open a [GitHub Discussion](https://github.com/vastdreams/physics-ai/discussions) or [Issue](https://github.com/vastdreams/physics-ai/issues).

**Maintainer**: Abhishek Sehgal
