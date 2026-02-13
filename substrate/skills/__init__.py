"""
PATH: substrate/skills/__init__.py
PURPOSE: Beyond Frontier Skills System - Modular, versioned physics capabilities

WHY: Inspired by OpenClaw's ClawHub skill registry, this provides a modular
     system for physics computations that can be discovered, composed, and
     evolved by the AI system.

REFERENCE: https://github.com/openclaw/clawhub (MIT License)

FLOW:
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│ Register    │────>│ Discover     │────>│ Execute         │
│ Skills      │     │ & Compose    │     │ Physics Tasks   │
└─────────────┘     └──────────────┘     └─────────────────┘

DEPENDENCIES:
- dataclasses: Skill definitions
- typing: Type hints for composability
"""

from .skill_registry import (
    Skill,
    SkillMetadata,
    SkillRegistry,
    skill,
    get_registry,
)

from .physics_skills import (
    # Quantum mechanics skills
    solve_schrodinger,
    quantum_time_evolution,
    lindblad_evolution,
    
    # Classical mechanics skills
    solve_lagrangian,
    orbital_mechanics,
    
    # Electromagnetism skills
    maxwell_solver,
    
    # Thermodynamics skills
    thermodynamic_process,
    
    # Astrophysics skills
    cosmological_distance,
    stellar_evolution,
    
    # Optics skills
    diffraction_pattern,
    optical_system_psf,
)

from .workflows import (
    Workflow,
    WorkflowStep,
    WorkflowEngine,
    ApprovalGate,
)

__all__ = [
    # Core
    'Skill',
    'SkillMetadata',
    'SkillRegistry',
    'skill',
    'get_registry',
    
    # Physics skills
    'solve_schrodinger',
    'quantum_time_evolution',
    'lindblad_evolution',
    'solve_lagrangian',
    'orbital_mechanics',
    'maxwell_solver',
    'thermodynamic_process',
    'cosmological_distance',
    'stellar_evolution',
    'diffraction_pattern',
    'optical_system_psf',
    
    # Workflows
    'Workflow',
    'WorkflowStep',
    'WorkflowEngine',
    'ApprovalGate',
]
