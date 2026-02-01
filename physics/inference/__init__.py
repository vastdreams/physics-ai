# PATH: physics/inference/__init__.py
# PURPOSE:
#   - Inference package for physics computation, following DeepSeek's inference patterns
#   - Handles model definition, computation kernels, and generation logic
#
# ROLE IN ARCHITECTURE:
#   - Inference layer: Separates computation from problem representation
#
# MAIN EXPORTS:
#   - PhysicsModelArgs: Configuration dataclass
#   - PhysicsTransformer: Core physics reasoning model
#   - generate_solution: Generation pipeline
#
# NON-RESPONSIBILITIES:
#   - This package does NOT handle:
#     - Problem formatting (handled by encoding layer)
#     - API endpoints (handled by API layer)
#
# NOTES FOR FUTURE AI:
#   - Follows DeepSeek's inference/model.py patterns
#   - Uses dataclass for configuration (like ModelArgs)
#   - Kernel optimizations inspired by DeepSeek's kernel.py

from .model import (
    PhysicsModelArgs,
    PhysicsTransformer,
    TheorySelector,
    EquationSolver,
    ConservationChecker,
)

from .generate import (
    generate_solution,
    sample_theory,
    validate_solution,
)

from .kernel import (
    physics_gemm,
    conservation_kernel,
    symmetry_kernel,
    integration_kernel,
)

__all__ = [
    "PhysicsModelArgs",
    "PhysicsTransformer",
    "TheorySelector",
    "EquationSolver",
    "ConservationChecker",
    "generate_solution",
    "sample_theory",
    "validate_solution",
    "physics_gemm",
    "conservation_kernel",
    "symmetry_kernel",
    "integration_kernel",
]

