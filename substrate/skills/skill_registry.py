"""
PATH: substrate/skills/skill_registry.py
PURPOSE: Skill registration and discovery system inspired by OpenClaw's ClawHub

WHY: Provides a typed, versioned skill registry that allows the AI to discover
     and compose physics capabilities dynamically, enabling self-evolution.

REFERENCE: https://github.com/openclaw/clawhub

FLOW:
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│ @skill      │────>│ Registry     │────>│ Discovery &     │
│ Decorator   │     │ Storage      │     │ Execution       │
└─────────────┘     └──────────────┘     └─────────────────┘

DEPENDENCIES:
- dataclasses: Structured skill definitions
- typing: Type safety for inputs/outputs
- functools: Decorator utilities
"""

from typing import (
    Callable, Dict, List, Optional, Any, TypeVar, Generic,
    get_type_hints, Union, Tuple
)
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from functools import wraps
import inspect
import json
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T')
InputT = TypeVar('InputT')
OutputT = TypeVar('OutputT')


class SkillDomain(Enum):
    """Physics domains for skill categorization."""
    QUANTUM = "quantum"
    CLASSICAL = "classical"
    ELECTROMAGNETISM = "electromagnetism"
    THERMODYNAMICS = "thermodynamics"
    RELATIVITY = "relativity"
    ASTROPHYSICS = "astrophysics"
    OPTICS = "optics"
    NUCLEAR = "nuclear"
    CONDENSED_MATTER = "condensed_matter"
    FLUID_DYNAMICS = "fluid_dynamics"
    PLASMA = "plasma"
    ACOUSTICS = "acoustics"
    GENERAL = "general"


class SkillComplexity(Enum):
    """Computational complexity classification."""
    TRIVIAL = "trivial"      # O(1) - constant time lookups
    SIMPLE = "simple"        # O(n) - linear algorithms
    MODERATE = "moderate"    # O(n²) - quadratic algorithms
    COMPLEX = "complex"      # O(n³) or iterative solvers
    INTENSIVE = "intensive"  # GPU/parallel computation needed


@dataclass
class SkillMetadata:
    """
    Metadata for a physics skill.
    
    Inspired by ClawHub's skill frontmatter system.
    """
    name: str
    description: str
    domain: SkillDomain
    version: str = "1.0.0"
    
    # Categorization
    tags: List[str] = field(default_factory=list)
    complexity: SkillComplexity = SkillComplexity.MODERATE
    
    # Dependencies
    requires_skills: List[str] = field(default_factory=list)
    requires_packages: List[str] = field(default_factory=list)
    
    # Physics metadata
    equations_used: List[str] = field(default_factory=list)
    constants_used: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    limitations: List[str] = field(default_factory=list)
    
    # Validation
    validated: bool = False
    validation_date: Optional[datetime] = None
    validation_reference: Optional[str] = None
    
    # Evolution tracking
    created_at: datetime = field(default_factory=datetime.now)
    evolved_from: Optional[str] = None
    evolution_reason: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize metadata to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "domain": self.domain.value,
            "version": self.version,
            "tags": self.tags,
            "complexity": self.complexity.value,
            "requires_skills": self.requires_skills,
            "requires_packages": self.requires_packages,
            "equations_used": self.equations_used,
            "constants_used": self.constants_used,
            "assumptions": self.assumptions,
            "limitations": self.limitations,
            "validated": self.validated,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class SkillResult(Generic[T]):
    """
    Result from skill execution with metadata.
    """
    success: bool
    value: Optional[T] = None
    error: Optional[str] = None
    
    # Execution metadata
    execution_time_ms: float = 0.0
    skill_name: str = ""
    skill_version: str = ""
    
    # Physics validation
    units: Optional[str] = None
    uncertainty: Optional[float] = None
    assumptions_applied: List[str] = field(default_factory=list)
    
    # Provenance
    equations_applied: List[str] = field(default_factory=list)
    intermediate_values: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize result."""
        return {
            "success": self.success,
            "value": self.value if not hasattr(self.value, 'tolist') else self.value.tolist(),
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
            "skill_name": self.skill_name,
            "skill_version": self.skill_version,
            "units": self.units,
            "uncertainty": self.uncertainty,
        }


@dataclass
class Skill:
    """
    A registered physics skill.
    
    Skills are the atomic units of physics computation that can be
    discovered, composed, and evolved by the AI system.
    """
    metadata: SkillMetadata
    func: Callable
    
    # Type information extracted from function
    input_types: Dict[str, type] = field(default_factory=dict)
    output_type: Optional[type] = None
    
    # Usage tracking
    call_count: int = 0
    total_execution_time_ms: float = 0.0
    error_count: int = 0
    
    def __post_init__(self):
        """Extract type hints from function."""
        try:
            hints = get_type_hints(self.func)
            self.output_type = hints.pop('return', None)
            self.input_types = hints
        except Exception:
            pass
    
    def __call__(self, *args, **kwargs) -> SkillResult:
        """Execute the skill with result wrapping."""
        import time
        start = time.perf_counter()
        
        try:
            result = self.func(*args, **kwargs)
            elapsed = (time.perf_counter() - start) * 1000
            
            self.call_count += 1
            self.total_execution_time_ms += elapsed
            
            return SkillResult(
                success=True,
                value=result,
                execution_time_ms=elapsed,
                skill_name=self.metadata.name,
                skill_version=self.metadata.version,
            )
        except Exception as e:
            elapsed = (time.perf_counter() - start) * 1000
            self.error_count += 1
            
            logger.error(f"Skill {self.metadata.name} failed: {e}")
            
            return SkillResult(
                success=False,
                error=str(e),
                execution_time_ms=elapsed,
                skill_name=self.metadata.name,
                skill_version=self.metadata.version,
            )
    
    @property
    def signature(self) -> str:
        """Get function signature as string."""
        sig = inspect.signature(self.func)
        return f"{self.metadata.name}{sig}"
    
    @property
    def docstring(self) -> Optional[str]:
        """Get function docstring."""
        return self.func.__doc__
    
    def get_help(self) -> str:
        """Generate help text for this skill."""
        lines = [
            f"# {self.metadata.name} v{self.metadata.version}",
            f"Domain: {self.metadata.domain.value}",
            f"Complexity: {self.metadata.complexity.value}",
            "",
            f"## Description",
            self.metadata.description,
            "",
            f"## Signature",
            f"```python",
            self.signature,
            f"```",
        ]
        
        if self.docstring:
            lines.extend(["", "## Details", self.docstring])
        
        if self.metadata.assumptions:
            lines.extend(["", "## Assumptions"])
            for assumption in self.metadata.assumptions:
                lines.append(f"- {assumption}")
        
        if self.metadata.limitations:
            lines.extend(["", "## Limitations"])
            for limitation in self.metadata.limitations:
                lines.append(f"- {limitation}")
        
        if self.metadata.equations_used:
            lines.extend(["", "## Equations Used"])
            for eq in self.metadata.equations_used:
                lines.append(f"- {eq}")
        
        return "\n".join(lines)


class SkillRegistry:
    """
    Central registry for physics skills.
    
    Inspired by OpenClaw's ClawHub, this provides:
    - Skill discovery and search
    - Version management
    - Dependency resolution
    - Usage tracking for evolution
    """
    
    _instance: Optional['SkillRegistry'] = None
    
    def __init__(self):
        self._skills: Dict[str, Dict[str, Skill]] = {}  # name -> version -> skill
        self._latest: Dict[str, str] = {}  # name -> latest version
        self._by_domain: Dict[SkillDomain, List[str]] = {d: [] for d in SkillDomain}
        self._by_tag: Dict[str, List[str]] = {}
    
    @classmethod
    def get_instance(cls) -> 'SkillRegistry':
        """Get singleton registry instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def register(self, skill: Skill) -> None:
        """Register a skill in the registry."""
        name = skill.metadata.name
        version = skill.metadata.version
        
        if name not in self._skills:
            self._skills[name] = {}
        
        self._skills[name][version] = skill
        self._latest[name] = version
        
        # Index by domain
        if name not in self._by_domain[skill.metadata.domain]:
            self._by_domain[skill.metadata.domain].append(name)
        
        # Index by tags
        for tag in skill.metadata.tags:
            if tag not in self._by_tag:
                self._by_tag[tag] = []
            if name not in self._by_tag[tag]:
                self._by_tag[tag].append(name)
        
        logger.info(f"Registered skill: {name} v{version}")
    
    def get(self, name: str, version: Optional[str] = None) -> Optional[Skill]:
        """Get a skill by name and optional version."""
        if name not in self._skills:
            return None
        
        if version is None:
            version = self._latest.get(name)
        
        return self._skills[name].get(version)
    
    def list_skills(self, domain: Optional[SkillDomain] = None) -> List[str]:
        """List all registered skills, optionally filtered by domain."""
        if domain is not None:
            return self._by_domain.get(domain, [])
        return list(self._skills.keys())
    
    def search(self, query: str, domain: Optional[SkillDomain] = None) -> List[Skill]:
        """
        Search skills by query string.
        
        Searches name, description, and tags.
        """
        results = []
        query_lower = query.lower()
        
        for name in self.list_skills(domain):
            skill = self.get(name)
            if skill is None:
                continue
            
            # Check name
            if query_lower in name.lower():
                results.append(skill)
                continue
            
            # Check description
            if query_lower in skill.metadata.description.lower():
                results.append(skill)
                continue
            
            # Check tags
            if any(query_lower in tag.lower() for tag in skill.metadata.tags):
                results.append(skill)
        
        return results
    
    def get_by_tag(self, tag: str) -> List[Skill]:
        """Get all skills with a specific tag."""
        names = self._by_tag.get(tag, [])
        return [self.get(name) for name in names if self.get(name)]
    
    def get_dependencies(self, name: str) -> List[Skill]:
        """Get all skills that a skill depends on."""
        skill = self.get(name)
        if skill is None:
            return []
        
        deps = []
        for dep_name in skill.metadata.requires_skills:
            dep = self.get(dep_name)
            if dep:
                deps.append(dep)
                # Recursive dependencies
                deps.extend(self.get_dependencies(dep_name))
        
        return deps
    
    def get_usage_stats(self) -> Dict[str, Dict[str, Any]]:
        """Get usage statistics for all skills."""
        stats = {}
        for name, versions in self._skills.items():
            for version, skill in versions.items():
                key = f"{name}@{version}"
                stats[key] = {
                    "call_count": skill.call_count,
                    "total_time_ms": skill.total_execution_time_ms,
                    "error_count": skill.error_count,
                    "avg_time_ms": (
                        skill.total_execution_time_ms / skill.call_count
                        if skill.call_count > 0 else 0
                    ),
                    "error_rate": (
                        skill.error_count / (skill.call_count + skill.error_count)
                        if (skill.call_count + skill.error_count) > 0 else 0
                    ),
                }
        return stats
    
    def export_catalog(self) -> Dict[str, Any]:
        """Export skill catalog as JSON-serializable dict."""
        catalog = {
            "skills": {},
            "domains": {d.value: self._by_domain[d] for d in SkillDomain},
            "tags": self._by_tag,
        }
        
        for name, versions in self._skills.items():
            catalog["skills"][name] = {
                "versions": list(versions.keys()),
                "latest": self._latest.get(name),
                "metadata": versions[self._latest[name]].metadata.to_dict(),
            }
        
        return catalog


def skill(
    name: str,
    description: str,
    domain: SkillDomain,
    version: str = "1.0.0",
    tags: Optional[List[str]] = None,
    complexity: SkillComplexity = SkillComplexity.MODERATE,
    equations: Optional[List[str]] = None,
    assumptions: Optional[List[str]] = None,
    limitations: Optional[List[str]] = None,
    requires: Optional[List[str]] = None,
) -> Callable:
    """
    Decorator to register a function as a physics skill.
    
    Example:
        @skill(
            name="solve_harmonic_oscillator",
            description="Solve 1D quantum harmonic oscillator",
            domain=SkillDomain.QUANTUM,
            equations=["H = p²/2m + mω²x²/2"],
            assumptions=["Single particle", "No perturbations"],
        )
        def solve_harmonic_oscillator(omega: float, n_states: int = 10):
            ...
    """
    def decorator(func: Callable) -> Skill:
        metadata = SkillMetadata(
            name=name,
            description=description,
            domain=domain,
            version=version,
            tags=tags or [],
            complexity=complexity,
            equations_used=equations or [],
            assumptions=assumptions or [],
            limitations=limitations or [],
            requires_skills=requires or [],
        )
        
        registered_skill = Skill(metadata=metadata, func=func)
        
        # Register in global registry
        SkillRegistry.get_instance().register(registered_skill)
        
        return registered_skill
    
    return decorator


def get_registry() -> SkillRegistry:
    """Get the global skill registry."""
    return SkillRegistry.get_instance()
