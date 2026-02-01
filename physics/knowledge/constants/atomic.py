"""
PATH: physics/knowledge/constants/atomic.py
PURPOSE: Atomic-scale constants (Bohr radius, Rydberg, etc.)

Constants derived from electromagnetic and quantum constants that
characterize atomic structure and spectra.
"""

from physics.knowledge.base.node import ConstantNode, NodeStatus

# Bohr radius
a_0 = ConstantNode(
    id="a_0",
    name="Bohr Radius",
    domain="atomic",
    symbol="a₀",
    value=5.29177210903e-11,
    uncertainty=8.0e-21,
    unit="m",
    dimension="L",
    description="a₀ = 4πε₀ℏ²/(m_e e²) = ℏ/(m_e c α). Most probable "
                "electron-nucleus distance in hydrogen ground state. "
                "Natural length scale for atomic physics.",
    discoverer="Niels Bohr",
    year=1913,
    status=NodeStatus.PROVEN,
    tags=("hydrogen", "atomic_structure", "length_scale"),
)

# Rydberg constant
R_inf = ConstantNode(
    id="R_inf",
    name="Rydberg Constant",
    domain="atomic",
    symbol="R_∞",
    value=10973731.568160,
    uncertainty=2.1e-5,
    unit="m⁻¹",
    dimension="L^-1",
    description="R_∞ = m_e e⁴/(8ε₀²h³c) = α²m_e c/(2h). Most precisely "
                "measured constant in physics. Determines atomic spectra.",
    discoverer="Johannes Rydberg",
    year=1888,
    status=NodeStatus.EXPERIMENTAL,
    tags=("spectroscopy", "hydrogen", "precision"),
)

# Rydberg energy
E_h = ConstantNode(
    id="E_h",
    name="Hartree Energy",
    domain="atomic",
    symbol="E_h",
    value=4.3597447222071e-18,
    uncertainty=8.5e-30,
    unit="J",
    dimension="M L^2 T^-2",
    description="E_h = m_e(e²/(4πε₀ℏ))² = 2R_∞hc ≈ 27.2 eV. Natural "
                "energy unit in atomic physics. Twice the hydrogen "
                "ground state binding energy.",
    discoverer="Douglas Hartree",
    year=1928,
    status=NodeStatus.PROVEN,
    tags=("atomic_units", "energy_scale"),
)

# Bohr magneton
mu_B = ConstantNode(
    id="mu_B",
    name="Bohr Magneton",
    domain="atomic",
    symbol="μ_B",
    value=9.2740100783e-24,
    uncertainty=2.8e-33,
    unit="J/T",
    dimension="I L^2",
    description="μ_B = eℏ/(2m_e). Natural unit of electron magnetic moment. "
                "Appears in Zeeman effect and electron spin.",
    discoverer="Niels Bohr",
    year=1913,
    status=NodeStatus.PROVEN,
    tags=("magnetism", "electron", "spin"),
)

# Nuclear magneton
mu_N = ConstantNode(
    id="mu_N",
    name="Nuclear Magneton",
    domain="atomic",
    symbol="μ_N",
    value=5.0507837461e-27,
    uncertainty=1.5e-36,
    unit="J/T",
    dimension="I L^2",
    description="μ_N = eℏ/(2m_p). Natural unit for nuclear magnetic moments. "
                "~1836 times smaller than Bohr magneton.",
    discoverer="(derived)",
    year=1928,
    status=NodeStatus.PROVEN,
    tags=("nuclear", "magnetism", "nmr"),
)

# Electron g-factor
g_e = ConstantNode(
    id="g_e",
    name="Electron g-Factor",
    domain="atomic",
    symbol="g_e",
    value=-2.00231930436256,
    uncertainty=3.5e-13,
    unit="(dimensionless)",
    dimension="1",
    description="Ratio of electron magnetic moment to Bohr magneton times "
                "spin. Deviation from -2 is the anomalous magnetic moment, "
                "predicted by QED to 12 decimal places.",
    discoverer="(QED calculation)",
    year=1947,
    status=NodeStatus.EXPERIMENTAL,
    tags=("qed", "precision_test", "spin"),
)

# Compton wavelength
lambda_C = ConstantNode(
    id="lambda_C",
    name="Compton Wavelength",
    domain="atomic",
    symbol="λ_C",
    value=2.42631023867e-12,
    uncertainty=7.3e-22,
    unit="m",
    dimension="L",
    description="λ_C = h/(m_e c). Scale at which relativistic quantum "
                "effects (particle creation) become important for electrons.",
    discoverer="Arthur Compton",
    year=1923,
    status=NodeStatus.PROVEN,
    tags=("relativistic", "quantum", "length_scale"),
)

# Classical electron radius
r_e = ConstantNode(
    id="r_e",
    name="Classical Electron Radius",
    domain="atomic",
    symbol="r_e",
    value=2.8179403262e-15,
    uncertainty=1.3e-24,
    unit="m",
    dimension="L",
    description="r_e = e²/(4πε₀m_e c²) = α²a₀. Classical model radius "
                "equating electrostatic energy to rest mass. Appears in "
                "Thomson scattering cross section.",
    discoverer="(classical EM)",
    year=1902,
    status=NodeStatus.PROVEN,
    tags=("classical", "scattering", "thomson"),
)

# Export all nodes
NODES = [a_0, R_inf, E_h, mu_B, mu_N, g_e, lambda_C, r_e]
