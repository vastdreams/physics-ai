"""
PATH: substrate/skills/__init__.py
PURPOSE: Beyond Frontier Skills System - Modular, versioned physics capabilities

WHY: Inspired by OpenClaw's ClawHub skill registry, this provides a modular
     system for physics computations that can be discovered, composed, and
     evolved by the AI system.

REFERENCE: https://github.com/openclaw/clawhub (MIT License)

FLOW:
    Register Skills -> Discover & Compose -> Execute Physics Tasks

DEPENDENCIES:
- dataclasses: Skill definitions
- typing: Type hints for composability
"""

from .physics_skills import (
    cosmological_distance,
    diffraction_pattern,
    lindblad_evolution,
    maxwell_solver,
    optical_system_psf,
    orbital_mechanics,
    quantum_time_evolution,
    solve_lagrangian,
    solve_schrodinger,
    stellar_evolution,
    thermodynamic_process,
)
from .skill_registry import (
    Skill,
    SkillMetadata,
    SkillRegistry,
    get_registry,
    skill,
)
from .workflows import (
    ApprovalGate,
    Workflow,
    WorkflowEngine,
    WorkflowStep,
)

__all__ = [
    # Core
    "Skill",
    "SkillMetadata",
    "SkillRegistry",
    "skill",
    "get_registry",
    # Physics skills
    "solve_schrodinger",
    "quantum_time_evolution",
    "lindblad_evolution",
    "solve_lagrangian",
    "orbital_mechanics",
    "maxwell_solver",
    "thermodynamic_process",
    "cosmological_distance",
    "stellar_evolution",
    "diffraction_pattern",
    "optical_system_psf",
    # Workflows
    "Workflow",
    "WorkflowStep",
    "WorkflowEngine",
    "ApprovalGate",
]
