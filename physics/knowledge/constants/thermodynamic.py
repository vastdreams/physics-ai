"""
PATH: physics/knowledge/constants/thermodynamic.py
PURPOSE: Thermodynamic constants (kB, R, σ)

Constants governing thermal and statistical phenomena.
"""

from physics.knowledge.base.node import ConstantNode, NodeStatus

# Boltzmann constant
k_B = ConstantNode(
    id="k_B",
    name="Boltzmann Constant",
    domain="thermodynamics",
    symbol="k_B",
    value=1.380649e-23,
    uncertainty=0.0,  # Exact by definition (SI 2019)
    unit="J/K",
    dimension="M L^2 T^-2 Θ^-1",
    description="Relates temperature to energy: E = kT. Bridges microscopic "
                "particle energies to macroscopic temperature. Defines the "
                "kelvin in the SI system.",
    discoverer="Ludwig Boltzmann",
    year=1877,
    status=NodeStatus.FUNDAMENTAL,
    tags=("statistical_mechanics", "temperature", "entropy"),
)

# Gas constant
R = ConstantNode(
    id="R",
    name="Molar Gas Constant",
    domain="thermodynamics",
    symbol="R",
    value=8.314462618,
    uncertainty=0.0,
    unit="J/(mol⋅K)",
    dimension="M L^2 T^-2 N^-1 Θ^-1",
    description="R = N_A × k_B. Appears in ideal gas law PV = nRT. "
                "Universal constant for ideal gas behavior.",
    discoverer="(derived)",
    year=1834,
    status=NodeStatus.FUNDAMENTAL,
    tags=("gas", "ideal_gas", "molar"),
)

# Avogadro constant
N_A = ConstantNode(
    id="N_A",
    name="Avogadro Constant",
    domain="thermodynamics",
    symbol="N_A",
    value=6.02214076e23,
    uncertainty=0.0,  # Exact by definition (SI 2019)
    unit="mol⁻¹",
    dimension="N^-1",
    description="Number of particles in one mole. Links microscopic "
                "quantities to macroscopic amounts. Defines the mole.",
    discoverer="Jean Perrin (experimental)",
    year=1909,
    status=NodeStatus.FUNDAMENTAL,
    tags=("mole", "counting", "macroscopic"),
)

# Stefan-Boltzmann constant
sigma = ConstantNode(
    id="sigma",
    name="Stefan-Boltzmann Constant",
    domain="thermodynamics",
    symbol="σ",
    value=5.670374419e-8,
    uncertainty=0.0,
    unit="W/(m²⋅K⁴)",
    dimension="M T^-3 Θ^-4",
    description="σ = π²k⁴/(60ℏ³c²). Relates blackbody radiation power "
                "to temperature: P = σAT⁴.",
    discoverer="Josef Stefan, Ludwig Boltzmann",
    year=1879,
    status=NodeStatus.PROVEN,
    tags=("blackbody", "radiation", "thermal"),
)

# First radiation constant
c_1 = ConstantNode(
    id="c_1",
    name="First Radiation Constant",
    domain="thermodynamics",
    symbol="c₁",
    value=3.741771852e-16,
    uncertainty=0.0,
    unit="W⋅m²",
    dimension="M L^4 T^-3",
    description="c₁ = 2πhc². Appears in Planck's law for spectral radiance.",
    discoverer="Max Planck",
    year=1900,
    status=NodeStatus.PROVEN,
    tags=("blackbody", "planck_law"),
)

# Second radiation constant
c_2 = ConstantNode(
    id="c_2",
    name="Second Radiation Constant",
    domain="thermodynamics",
    symbol="c₂",
    value=1.438776877e-2,
    uncertainty=0.0,
    unit="m⋅K",
    dimension="L Θ",
    description="c₂ = hc/k_B. Appears in Planck's law exponent.",
    discoverer="Max Planck",
    year=1900,
    status=NodeStatus.PROVEN,
    tags=("blackbody", "planck_law"),
)

# Wien displacement constant
b = ConstantNode(
    id="b_wien",
    name="Wien Displacement Constant",
    domain="thermodynamics",
    symbol="b",
    value=2.897771955e-3,
    uncertainty=0.0,
    unit="m⋅K",
    dimension="L Θ",
    description="λ_max × T = b. Relates blackbody peak wavelength to temperature.",
    discoverer="Wilhelm Wien",
    year=1893,
    status=NodeStatus.PROVEN,
    tags=("blackbody", "wien_law"),
)

# Export all nodes
NODES = [k_B, R, N_A, sigma, c_1, c_2, b]
