"""
PATH: physics/knowledge/constants/particle.py
PURPOSE: Particle masses and properties

Masses of fundamental particles (leptons, quarks, bosons) and composite
particles (proton, neutron).
"""

from physics.knowledge.base.node import ConstantNode, NodeStatus

# Electron mass
m_e = ConstantNode(
    id="m_e",
    name="Electron Mass",
    domain="particle_physics",
    symbol="m_e",
    value=9.1093837015e-31,
    uncertainty=2.8e-40,
    unit="kg",
    dimension="M",
    description="Mass of the electron. Lightest charged lepton. "
                "Determines atomic and molecular structure.",
    discoverer="J.J. Thomson",
    year=1897,
    status=NodeStatus.EXPERIMENTAL,
    tags=("lepton", "electron", "mass"),
)

# Proton mass
m_p = ConstantNode(
    id="m_p",
    name="Proton Mass",
    domain="particle_physics",
    symbol="m_p",
    value=1.67262192369e-27,
    uncertainty=5.1e-37,
    unit="kg",
    dimension="M",
    description="Mass of the proton. Composed of two up quarks and one down "
                "quark (uud). Stable against decay.",
    discoverer="Ernest Rutherford",
    year=1917,
    status=NodeStatus.EXPERIMENTAL,
    tags=("baryon", "proton", "mass"),
)

# Neutron mass
m_n = ConstantNode(
    id="m_n",
    name="Neutron Mass",
    domain="particle_physics",
    symbol="m_n",
    value=1.67492749804e-27,
    uncertainty=9.5e-37,
    unit="kg",
    dimension="M",
    description="Mass of the neutron. Composed of one up quark and two down "
                "quarks (udd). Beta-decays with half-life ~10 minutes.",
    discoverer="James Chadwick",
    year=1932,
    status=NodeStatus.EXPERIMENTAL,
    tags=("baryon", "neutron", "mass"),
)

# Muon mass
m_mu = ConstantNode(
    id="m_mu",
    name="Muon Mass",
    domain="particle_physics",
    symbol="m_μ",
    value=1.883531627e-28,
    uncertainty=4.2e-37,
    unit="kg",
    dimension="M",
    description="Mass of the muon. Second-generation charged lepton. "
                "~207 times heavier than electron. Mean lifetime 2.2 μs.",
    discoverer="Carl Anderson, Seth Neddermeyer",
    year=1936,
    status=NodeStatus.EXPERIMENTAL,
    tags=("lepton", "muon", "mass"),
)

# Tau mass
m_tau = ConstantNode(
    id="m_tau",
    name="Tau Mass",
    domain="particle_physics",
    symbol="m_τ",
    value=3.16754e-27,
    uncertainty=2.1e-31,
    unit="kg",
    dimension="M",
    description="Mass of the tau. Third-generation charged lepton. "
                "~3477 times heavier than electron. Mean lifetime 2.9×10⁻¹³ s.",
    discoverer="Martin Perl",
    year=1975,
    status=NodeStatus.EXPERIMENTAL,
    tags=("lepton", "tau", "mass"),
)

# Atomic mass unit
u = ConstantNode(
    id="u",
    name="Atomic Mass Unit",
    domain="particle_physics",
    symbol="u",
    value=1.66053906660e-27,
    uncertainty=5.0e-37,
    unit="kg",
    dimension="M",
    description="Defined as 1/12 of the mass of carbon-12. Standard unit "
                "for expressing atomic and molecular masses.",
    discoverer="(definition)",
    year=1961,
    status=NodeStatus.FUNDAMENTAL,
    tags=("atomic", "mass_unit"),
)

# Proton-electron mass ratio
m_p_over_m_e = ConstantNode(
    id="m_p_over_m_e",
    name="Proton-Electron Mass Ratio",
    domain="particle_physics",
    symbol="m_p/m_e",
    value=1836.15267343,
    uncertainty=1.1e-7,
    unit="(dimensionless)",
    dimension="1",
    description="Ratio of proton to electron mass. Fundamental dimensionless "
                "number in atomic physics. Determines atomic energy scales.",
    discoverer="(derived)",
    year=1913,
    status=NodeStatus.EXPERIMENTAL,
    tags=("mass_ratio", "dimensionless"),
)

# W boson mass
m_W = ConstantNode(
    id="m_W",
    name="W Boson Mass",
    domain="particle_physics",
    symbol="m_W",
    value=1.43296e-25,
    uncertainty=1.8e-29,
    unit="kg",
    dimension="M",
    description="Mass of the W± boson. Mediates charged weak interactions. "
                "~80.4 GeV/c². Discovered at CERN.",
    discoverer="UA1 and UA2 collaborations",
    year=1983,
    status=NodeStatus.EXPERIMENTAL,
    tags=("boson", "weak_force", "electroweak"),
)

# Z boson mass
m_Z = ConstantNode(
    id="m_Z",
    name="Z Boson Mass",
    domain="particle_physics",
    symbol="m_Z",
    value=1.62550e-25,
    uncertainty=3.9e-30,
    unit="kg",
    dimension="M",
    description="Mass of the Z⁰ boson. Mediates neutral weak interactions. "
                "~91.2 GeV/c². Most precisely measured particle mass.",
    discoverer="UA1 and UA2 collaborations",
    year=1983,
    status=NodeStatus.EXPERIMENTAL,
    tags=("boson", "weak_force", "electroweak"),
)

# Higgs boson mass
m_H = ConstantNode(
    id="m_H",
    name="Higgs Boson Mass",
    domain="particle_physics",
    symbol="m_H",
    value=2.2246e-25,
    uncertainty=2.7e-28,
    unit="kg",
    dimension="M",
    description="Mass of the Higgs boson. ~125 GeV/c². Gives mass to "
                "fundamental particles via the Higgs mechanism.",
    discoverer="ATLAS and CMS collaborations",
    year=2012,
    status=NodeStatus.EXPERIMENTAL,
    tags=("boson", "higgs", "electroweak_symmetry_breaking"),
)

# Export all nodes
NODES = [m_e, m_p, m_n, m_mu, m_tau, u, m_p_over_m_e, m_W, m_Z, m_H]
