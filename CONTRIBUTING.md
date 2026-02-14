# Contributing to Beyond Frontier

Thank you for your interest in contributing to Beyond Frontier. This document provides guidelines and instructions for contributing.

## Development Workflow

### Branching Strategy

- **main**: Production-ready code
- **development**: Active development branch
- **feature/***: Feature branches
- **bugfix/***: Bug fix branches

### Getting Started

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/<your-username>/physics-ai.git
   cd physics-ai
   ```
3. Set up the development environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature
   ```
5. Make your changes
6. Write or update tests
7. Ensure all tests pass:
   ```bash
   pytest tests/ -v
   ```
8. Submit a pull request to `main`

### Code Standards

- **Python**: Follow PEP 8 (enforced via `black` and `flake8`)
- **JavaScript/React**: Follow existing conventions; use functional components with hooks
- Include a file header with `PATH`, `PURPOSE`, and key metadata
- Add validators and loggers to backend modules
- Write tests for new logic (happy path + primary failure mode)
- Update documentation as needed

### Commit Messages

Use the conventional format:

```
type(scope): short description
```

Types: `feat`, `fix`, `refactor`, `docs`, `style`, `test`, `chore`

Examples:
- `feat(solver): add relativistic orbit integration`
- `fix(api): handle missing initial conditions in simulate endpoint`
- `docs: update API reference for agents endpoints`

### Pull Request Process

1. Update documentation if needed
2. Ensure all tests pass
3. Update CHANGELOG.md if applicable
4. Fill out the pull request template
5. Request review from maintainers

## Architecture Principles

- **Modular design**: Each component can be used independently
- **First-principles foundation**: Grounded in mathematical principles
- **I/O decomposition**: Small pure functions with clear inputs and outputs
- **Validation everywhere**: Physics constraints checked at every step
- **Safe evolution**: Code changes require validation before application

## Need Help?

- Open a [Discussion](https://github.com/vastdreams/physics-ai/discussions) for questions
- Check existing [Issues](https://github.com/vastdreams/physics-ai/issues) before filing new ones
- Read the [docs/](docs/) directory for architecture and implementation details
