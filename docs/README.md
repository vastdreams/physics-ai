# Beyond Frontier Documentation

Welcome to the Beyond Frontier documentation. This folder contains all technical documentation for the project.

## Quick Links

| Document | Description |
|----------|-------------|
| [Master Architecture](MASTER_ARCHITECTURE.md) | System architecture and design principles |
| [API Reference](API_REFERENCE.md) | Complete REST API documentation |
| [Physics Framework](PHYSICS_FRAMEWORK.md) | Physics domain structure |
| [Complete Feature List](COMPLETE_FEATURE_LIST.md) | All implemented features |

## Documentation Structure

```
docs/
├── README.md                          # This file
├── MASTER_ARCHITECTURE.md             # System architecture
├── API_REFERENCE.md                   # REST API documentation
├── PHYSICS_FRAMEWORK.md               # Physics modules
├── COMPLETE_FEATURE_LIST.md           # Feature inventory
│
├── implementation/                    # Implementation details
│   ├── IMPLEMENTATION_SUMMARY.md      # Implementation overview
│   ├── FINAL_IMPLEMENTATION_REPORT.md # Final report
│   └── API_IMPLEMENTATION_STATUS.md   # API status
│
├── setup/                             # Setup guides
│   ├── GITHUB_SETUP.md                # GitHub configuration
│   ├── OPEN_SOURCE_SETUP.md           # Open source setup
│   └── FINAL_SETUP_CHECKLIST.md       # Setup checklist
│
└── archive/                           # Archived docs
    └── PROJECT_SUMMARY.md             # Legacy summary
```

## Core Concepts

### Neurosymbolic AI
Beyond Frontier combines two AI paradigms:
- **Neural**: Pattern recognition through embeddings
- **Symbolic**: Logical reasoning through rules and equations

See [MASTER_ARCHITECTURE.md](MASTER_ARCHITECTURE.md) for details.

### Physics Domains
The physics module covers:
- Classical mechanics (Newtonian, Lagrangian, Hamiltonian)
- Quantum mechanics (Schrödinger, path integrals)
- Field theory (Electromagnetism, gauge theory, GR)
- Statistical mechanics (Thermodynamics, phase transitions)

See [PHYSICS_FRAMEWORK.md](PHYSICS_FRAMEWORK.md) for details.

### Self-Evolution
The system can analyze and improve its own code:
- AST-based code analysis
- Validated code generation
- Performance-based selection

See [SELF_EVOLVING_AI_IMPLEMENTATION.md](SELF_EVOLVING_AI_IMPLEMENTATION.md) for details.

## API Overview

The REST API provides:
- **41 endpoints** across 11 categories
- **WebSocket** support for real-time updates
- **Full CRUD** for rules, nodes, and state

See [API_REFERENCE.md](API_REFERENCE.md) for complete documentation.

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/beyondfrontier/beyondfrontier/issues)
- **Discussions**: [GitHub Discussions](https://github.com/beyondfrontier/beyondfrontier/discussions)
- **Contributing**: See [CONTRIBUTING.md](../CONTRIBUTING.md)
