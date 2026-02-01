"""
PATH: physics/knowledge/constants/electromagnetic.py
PURPOSE: Electromagnetic constants (e, μ₀, ε₀, α)

Constants defining electromagnetic interactions and the structure of atoms.
"""

from physics.knowledge.base.node import ConstantNode, NodeStatus

# Elementary charge
e = ConstantNode(
    id="e",
    name="Elementary Charge",
    domain="electromagnetism",
    symbol="e",
    value=1.602176634e-19,
    uncertainty=0.0,  # Exact by definition (SI 2019)
    unit="C",
    dimension="I T",
    description="Fundamental unit of electric charge. All observed charges "
                "are integer multiples of e (quarks have fractional charges but "
                "are always confined).",
    discoverer="Robert Millikan",
    year=1909,
    status=NodeStatus.FUNDAMENTAL,
    tags=("charge", "quantization", "electromagnetism"),
)

# Vacuum permittivity
epsilon_0 = ConstantNode(
    id="epsilon_0",
    name="Vacuum Permittivity",
    domain="electromagnetism",
    symbol="ε₀",
    value=8.8541878128e-12,
    uncertainty=1.3e-21,
    unit="F/m",
    dimension="M^-1 L^-3 T^4 I^2",
    description="Electric constant. Determines the strength of the electric "
                "field from charges in vacuum. Related to c by ε₀μ₀c² = 1.",
    discoverer="(derived quantity)",
    year=1865,
    status=NodeStatus.FUNDAMENTAL,
    tags=("electromagnetism", "vacuum", "permittivity"),
)

# Vacuum permeability
mu_0 = ConstantNode(
    id="mu_0",
    name="Vacuum Permeability",
    domain="electromagnetism",
    symbol="μ₀",
    value=1.25663706212e-6,
    uncertainty=1.9e-16,
    unit="H/m",
    dimension="M L T^-2 I^-2",
    description="Magnetic constant. Determines the strength of the magnetic "
                "field from currents in vacuum. Related to c by ε₀μ₀c² = 1.",
    discoverer="(derived quantity)",
    year=1865,
    status=NodeStatus.FUNDAMENTAL,
    tags=("electromagnetism", "vacuum", "permeability"),
)

# Fine structure constant
alpha = ConstantNode(
    id="alpha",
    name="Fine Structure Constant",
    domain="electromagnetism",
    symbol="α",
    value=7.2973525693e-3,
    uncertainty=1.1e-12,
    unit="(dimensionless)",
    dimension="1",
    description="α = e²/(4πε₀ℏc) ≈ 1/137. Coupling constant of QED. "
                "Determines the strength of electromagnetic interactions. "
                "One of the most precisely measured constants in physics.",
    discoverer="Arnold Sommerfeld",
    year=1916,
    status=NodeStatus.EXPERIMENTAL,
    tags=("qed", "coupling_constant", "dimensionless"),
)

# Coulomb constant
k_e = ConstantNode(
    id="k_e",
    name="Coulomb Constant",
    domain="electromagnetism",
    symbol="k_e",
    value=8.9875517923e9,
    uncertainty=1.4e-1,
    unit="N⋅m²/C²",
    dimension="M L^3 T^-4 I^-2",
    description="k = 1/(4πε₀). Appears in Coulomb's law F = kq₁q₂/r².",
    discoverer="(derived quantity)",
    year=1785,
    status=NodeStatus.FUNDAMENTAL,
    tags=("electrostatics", "coulomb"),
)

# Magnetic flux quantum
phi_0 = ConstantNode(
    id="phi_0",
    name="Magnetic Flux Quantum",
    domain="electromagnetism",
    symbol="Φ₀",
    value=2.067833848e-15,
    uncertainty=0.0,
    unit="Wb",
    dimension="M L^2 T^-2 I^-1",
    description="Φ₀ = h/(2e). Fundamental unit of magnetic flux in "
                "superconductors. Used in SQUIDs and Josephson junctions.",
    discoverer="Brian Josephson",
    year=1962,
    status=NodeStatus.EXPERIMENTAL,
    tags=("superconductivity", "quantization"),
)

# Conductance quantum
G_0 = ConstantNode(
    id="G_0",
    name="Conductance Quantum",
    domain="electromagnetism",
    symbol="G₀",
    value=7.748091729e-5,
    uncertainty=0.0,
    unit="S",
    dimension="M^-1 L^-2 T^3 I^2",
    description="G₀ = 2e²/h. Fundamental unit of electrical conductance. "
                "Appears in quantum point contacts and quantum Hall effect.",
    discoverer="(quantum mechanics)",
    year=1980,
    status=NodeStatus.EXPERIMENTAL,
    tags=("quantum_transport", "mesoscopic"),
)

# Export all nodes
NODES = [e, epsilon_0, mu_0, alpha, k_e, phi_0, G_0]
