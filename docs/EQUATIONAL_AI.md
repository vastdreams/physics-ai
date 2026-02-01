# Equational AI System Documentation

## Overview

The Equational AI System ingests research papers, extracts mathematical equations, validates them against first-principles, and stores them in a knowledge base. It includes a permanence system for pre-computing common simulation scenarios.

## Architecture

### Core Components

#### 1. ResearchIngestion
Ingests research papers from multiple sources.

**Supported Formats**:
- PDF files
- ArXiv papers
- LaTeX documents

**Mathematical Foundation**:
- Ingestion: $I(source) \to Paper$
- Paper: $P = \{id, title, authors, content, equations, metadata\}$

**Key Features**:
- Multi-format support
- Metadata extraction
- Content parsing
- Equation identification

**Usage**:
```python
from ai.equational import ResearchIngestion

ingestion = ResearchIngestion()

# Ingest PDF
paper = ingestion.ingest_pdf("path/to/paper.pdf")

# Ingest ArXiv
paper = ingestion.ingest_arxiv("2307.04772")

# Ingest LaTeX
paper = ingestion.ingest_latex(latex_content, paper_id="paper_001")
```

#### 2. EquationExtractor
Extracts mathematical equations from research papers.

**Mathematical Foundation**:
- Extraction: $E(paper) \to \{equation_1, equation_2, ...\}$
- Equation: $Eq = \{id, equation, type, context, variables, domain\}$
- Patterns: LaTeX math environments, inline math, display math

**Key Features**:
- Pattern-based extraction
- Variable identification
- Domain classification
- Context extraction

**Usage**:
```python
from ai.equational import EquationExtractor, ResearchIngestion

ingestion = ResearchIngestion()
extractor = EquationExtractor()

# Ingest and extract
paper = ingestion.ingest_pdf("paper.pdf")
equations = extractor.extract_from_paper(paper)

for eq in equations:
    print(f"Equation: {eq.equation}")
    print(f"Variables: {eq.variables}")
    print(f"Domain: {eq.domain}")
```

#### 3. EquationStore
Knowledge base for storing and querying equations.

**Mathematical Foundation**:
- Store: $S = \{equations, relationships, metadata\}$
- Relationships: Link equations to theories, domains, variables
- Query: $Q(criteria) \to \{matching\_equations\}$

**Key Features**:
- Equation storage
- Relationship tracking
- Query capabilities
- Physics graph integration

**Usage**:
```python
from ai.equational import EquationStore, ExtractedEquation

store = EquationStore()

# Store equation
equation = ExtractedEquation(...)
store.store_equation(
    equation,
    theory_links=["quantum_mechanics"],
    domain_links=["quantum"]
)

# Query equations
results = store.query_equations(
    domain="quantum",
    variables=["\\hbar", "\\psi"]
)

# Link equations
store.link_equations("eq_1", "eq_2", relation_type="related")
```

#### 4. EquationValidator
Validates equations against first-principles.

**Mathematical Foundation**:
- Validation: $V(equation) \to (is\_valid, violations)$
- First-principles: Conservation laws, symmetries, constraints
- Domain rules: Physics-specific validation rules

**Key Features**:
- Syntax checking
- Unit consistency
- Conservation law verification
- Constraint checking
- Domain-specific rules

**Usage**:
```python
from ai.equational import EquationValidator, ExtractedEquation

validator = EquationValidator()

equation = ExtractedEquation(...)
is_valid, violations = validator.validate(equation)

if not is_valid:
    print(f"Violations: {violations}")
```

### Permanence System

#### 1. StateCache
Hash-based cache for pre-computed states.

**Mathematical Foundation**:
- Cache: $C = \{hash(input): state\}$
- Hash: $H(input) = SHA256(JSON(input))$
- TTL: Time-to-live for cache entries

**Key Features**:
- Hash-based storage
- Fast lookup (O(1))
- TTL support
- LRU eviction

**Usage**:
```python
from physics.permanence import StateCache

cache = StateCache(max_size=10000, default_ttl=3600)

# Store state
cache_key = cache.store(
    input_data={"energy": 10.0, "velocity": 0.1},
    state={"result": "computed"},
    metadata={"source": "simulation"}
)

# Retrieve state
cached_state = cache.retrieve({"energy": 10.0, "velocity": 0.1})
```

#### 2. Precomputation
Pre-computes common simulation scenarios.

**Mathematical Foundation**:
- Precomputation: $P(scenarios) \to \{results\}$
- Scenarios: Common input combinations
- Results: Pre-computed states

**Key Features**:
- Scenario generation
- Priority-based computation
- Background processing
- Result caching

**Usage**:
```python
from physics.permanence import Precomputation, StateCache

cache = StateCache()
precomp = Precomputation(cache)

# Generate common scenarios
scenarios = precomp.generate_common_scenarios()

# Pre-compute
results = precomp.precompute_common_scenarios(scenarios)
```

#### 3. Retrieval
Fast lookup with automatic fallback to computation.

**Mathematical Foundation**:
- Retrieval: $R(input) = Cache(input)$ if exists, else $Compute(input)$
- Fallback: Automatic computation if not cached

**Key Features**:
- Hash-based lookup
- Automatic fallback
- Cache management
- Performance optimization

**Usage**:
```python
from physics.permanence import Retrieval, StateCache
from physics.integration.physics_integrator import PhysicsIntegrator

cache = StateCache()
retrieval = Retrieval(cache)

# Get state (cached or computed)
state = retrieval.get_state(
    scenario={"energy": 10.0},
    initial_conditions={},
    time_span=(0.0, 1.0),
    num_steps=100,
    use_cache=True
)
```

## API Endpoints

### Research Ingestion
- `POST /api/v1/equational/ingest` - Ingest research paper
- `GET /api/v1/equational/equations` - List all equations
- `GET /api/v1/equational/equations/<eq_id>` - Get equation details
- `POST /api/v1/equational/validate` - Validate equation
- `GET /api/v1/equational/permanence` - Get permanence states

### Example API Usage

```python
import requests

# Ingest research paper
response = requests.post('http://localhost:5000/api/v1/equational/ingest', json={
    "type": "arxiv",
    "source": "2307.04772"
})

# List equations
response = requests.get('http://localhost:5000/api/v1/equational/equations')

# Validate equation
response = requests.post('http://localhost:5000/api/v1/equational/validate', json={
    "equation_id": "eq_123"
})
```

## Mathematical Foundations

### Equation Extraction Patterns

**Display Math**: `$$...$$`
```
$$E = mc^2$$
```

**Inline Math**: `$...$`
```
The energy $E$ is given by $E = mc^2$.
```

**Equation Environment**: `\begin{equation}...\end{equation}`
```latex
\begin{equation}
H\psi = E\psi
\end{equation}
```

**Align Environment**: `\begin{align}...\end{align}`
```latex
\begin{align}
\frac{d}{dt}\vec{p} &= \vec{F} \\
E &= \frac{p^2}{2m}
\end{align}
```

### Validation Rules

1. **Syntax**: Balanced parentheses, brackets, braces
2. **Units**: Unit consistency checking
3. **Conservation**: Energy, momentum, charge conservation
4. **Constraints**: Causality, unitarity, energy bounds
5. **Domain Rules**: Physics-specific validation

### Hash Function

For permanence caching:
$$H(input) = SHA256(JSON(input))$$

## Performance Considerations

- **PDF Parsing**: O(n) where n = document size
- **Equation Extraction**: O(n) pattern matching
- **Cache Lookup**: O(1) hash-based
- **Validation**: O(1) for syntax, O(n) for complex checks

## Best Practices

1. **Research Ingestion**: Use appropriate format (PDF for quality, ArXiv for metadata)
2. **Equation Extraction**: Review extracted equations for accuracy
3. **Validation**: Always validate before storing
4. **Permanence**: Pre-compute frequently used scenarios
5. **Cache Management**: Set appropriate TTL and max size

## Integration Examples

### Complete Pipeline
```python
from ai.equational import ResearchIngestion, EquationExtractor, EquationStore, EquationValidator
from physics.permanence import StateCache, Precomputation

# Ingest
ingestion = ResearchIngestion()
paper = ingestion.ingest_arxiv("2307.04772")

# Extract
extractor = EquationExtractor()
equations = extractor.extract_from_paper(paper)

# Validate and store
validator = EquationValidator()
store = EquationStore()

for eq in equations:
    is_valid, violations = validator.validate(eq)
    if is_valid:
        store.store_equation(eq, theory_links=["quantum_mechanics"])
```

### With Physics Integrator
```python
from physics.permanence import Retrieval, StateCache
from physics.integration.physics_integrator import PhysicsIntegrator

cache = StateCache()
retrieval = Retrieval(cache)

# Get state (uses cache if available)
state = retrieval.get_state(
    scenario={"energy": 10.0},
    initial_conditions={},
    time_span=(0.0, 1.0),
    use_cache=True
)
```

## Future Enhancements

1. **Advanced Parsing**: Machine learning for equation extraction
2. **Semantic Validation**: Deep understanding of equation meaning
3. **Equation Synthesis**: Generate new equations from existing ones
4. **Multi-Language**: Support for multiple languages
5. **Collaborative**: Shared equation knowledge base

