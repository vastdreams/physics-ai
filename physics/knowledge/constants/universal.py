"""
PATH: physics/knowledge/constants/universal.py
PURPOSE: Universal physical constants (c, h, G)

These are the fundamental constants that appear across all physics domains.
They define the scales of relativistic, quantum, and gravitational phenomena.
"""

from physics.knowledge.base.node import ConstantNode, NodeStatus

# Speed of light in vacuum
c = ConstantNode(
    id="c",
    name="Speed of Light",
    domain="universal",
    symbol="c",
    value=299792458.0,
    uncertainty=0.0,  # Exact by definition
    unit="m/s",
    dimension="L T^-1",
    description="Maximum speed of information propagation in the universe. "
                "Defines the causal structure of spacetime.",
    discoverer="Ole Rømer (measurement), Einstein (interpretation)",
    year=1905,
    status=NodeStatus.FUNDAMENTAL,
    tags=("relativity", "electromagnetism", "causality"),
)

# Planck constant
h = ConstantNode(
    id="h",
    name="Planck Constant",
    domain="universal",
    symbol="h",
    value=6.62607015e-34,
    uncertainty=0.0,  # Exact by definition (SI 2019)
    unit="J⋅s",
    dimension="M L^2 T^-1",
    description="Fundamental quantum of action. Relates energy to frequency. "
                "Defines the scale at which quantum effects become significant.",
    discoverer="Max Planck",
    year=1900,
    status=NodeStatus.FUNDAMENTAL,
    tags=("quantum", "action", "energy"),
)

# Reduced Planck constant
hbar = ConstantNode(
    id="hbar",
    name="Reduced Planck Constant",
    domain="universal",
    symbol="ℏ",
    value=1.054571817e-34,
    uncertainty=0.0,
    unit="J⋅s",
    dimension="M L^2 T^-1",
    description="h/(2π). Appears in angular momentum quantization and "
                "the canonical commutation relations.",
    discoverer="Paul Dirac (notation)",
    year=1926,
    status=NodeStatus.FUNDAMENTAL,
    tags=("quantum", "angular_momentum"),
)

# Gravitational constant
G = ConstantNode(
    id="G",
    name="Gravitational Constant",
    domain="universal",
    symbol="G",
    value=6.67430e-11,
    uncertainty=1.5e-15,
    unit="m³/(kg⋅s²)",
    dimension="L^3 M^-1 T^-2",
    description="Coupling strength of gravitational interaction. "
                "Determines the relationship between mass and spacetime curvature.",
    discoverer="Henry Cavendish (measurement)",
    year=1798,
    status=NodeStatus.EXPERIMENTAL,
    tags=("gravity", "general_relativity"),
)

# Planck units (derived but fundamental)
planck_length = ConstantNode(
    id="l_P",
    name="Planck Length",
    domain="universal",
    symbol="l_P",
    value=1.616255e-35,
    uncertainty=1.8e-40,
    unit="m",
    dimension="L",
    description="sqrt(ℏG/c³). The scale at which quantum gravitational effects "
                "become significant. May be the smallest meaningful length.",
    discoverer="Max Planck",
    year=1899,
    status=NodeStatus.THEORETICAL,
    tags=("quantum_gravity", "planck_units"),
)

planck_time = ConstantNode(
    id="t_P",
    name="Planck Time",
    domain="universal",
    symbol="t_P",
    value=5.391247e-44,
    uncertainty=6.0e-49,
    unit="s",
    dimension="T",
    description="sqrt(ℏG/c⁵). Time for light to travel one Planck length. "
                "May be the smallest meaningful time interval.",
    discoverer="Max Planck",
    year=1899,
    status=NodeStatus.THEORETICAL,
    tags=("quantum_gravity", "planck_units"),
)

planck_mass = ConstantNode(
    id="m_P",
    name="Planck Mass",
    domain="universal",
    symbol="m_P",
    value=2.176434e-8,
    uncertainty=2.4e-13,
    unit="kg",
    dimension="M",
    description="sqrt(ℏc/G). Mass scale at which quantum and gravitational "
                "effects are comparable.",
    discoverer="Max Planck",
    year=1899,
    status=NodeStatus.THEORETICAL,
    tags=("quantum_gravity", "planck_units"),
)

# Export all nodes
NODES = [c, h, hbar, G, planck_length, planck_time, planck_mass]
