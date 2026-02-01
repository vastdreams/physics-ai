"""
PATH: physics/knowledge/equations/nuclear/nuclear_reactions.py
PURPOSE: Nuclear reactions, binding energy, fission, fusion
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Nuclear Binding Energy
binding_energy = EquationNode(
    id="nuclear_binding_energy",
    name="Nuclear Binding Energy",
    domain="nuclear_physics",
    latex=r"B = [Zm_p + Nm_n - M_{nucleus}]c^2",
    sympy="B = (Z*m_p + N*m_n - M_nuc)*c**2",
    variables=(("B", "Binding energy", "J"), ("Z", "Proton number", "dimensionless"), ("N", "Neutron number", "dimensionless"), ("m_p", "Proton mass", "kg"), ("m_n", "Neutron mass", "kg"), ("M_nuc", "Nuclear mass", "kg")),
    description="Energy to disassemble nucleus. B > 0 for stable nuclei.",
    derives_from=("mass_energy_equivalence",),
    uses=("m_p", "m_n", "c"),
    status=NodeStatus.PROVEN,
    tags=("binding", "mass_defect"),
)

# Semi-Empirical Mass Formula
semf = EquationNode(
    id="semi_empirical_mass_formula",
    name="Semi-Empirical Mass Formula (Weizsäcker)",
    domain="nuclear_physics",
    latex=r"B = a_V A - a_S A^{2/3} - a_C \frac{Z^2}{A^{1/3}} - a_A \frac{(N-Z)^2}{A} + \delta(A,Z)",
    sympy="B = a_V*A - a_S*A**(2/3) - a_C*Z**2/A**(1/3) - a_A*(N-Z)**2/A + delta",
    variables=(("B", "Binding energy", "MeV"), ("A", "Mass number", "dimensionless"), ("Z", "Atomic number", "dimensionless"), ("a_V", "Volume term ~15.8 MeV", "MeV"), ("a_S", "Surface term ~18.3 MeV", "MeV"), ("a_C", "Coulomb term ~0.71 MeV", "MeV"), ("a_A", "Asymmetry term ~23.2 MeV", "MeV"), ("delta", "Pairing term", "MeV")),
    description="Liquid drop model. Volume, surface, Coulomb, asymmetry, pairing terms.",
    derives_from=("nuclear_binding_energy",),
    status=NodeStatus.EMPIRICAL,
    tags=("binding", "model"),
)

# Q-Value
q_value = EquationNode(
    id="nuclear_q_value",
    name="Nuclear Reaction Q-Value",
    domain="nuclear_physics",
    latex=r"Q = (m_{initial} - m_{final})c^2 = \sum KE_{final} - \sum KE_{initial}",
    sympy="Q = (m_i - m_f)*c**2",
    variables=(("Q", "Q-value", "MeV"), ("m_i", "Initial masses", "kg"), ("m_f", "Final masses", "kg")),
    description="Energy released (Q>0) or required (Q<0) for reaction.",
    derives_from=("mass_energy_equivalence",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("reaction", "energy"),
)

# Cross Section
cross_section = EquationNode(
    id="nuclear_cross_section",
    name="Nuclear Cross Section",
    domain="nuclear_physics",
    latex=r"\sigma = \frac{R}{I \cdot n}",
    sympy="sigma = R/(I*n)",
    variables=(("sigma", "Cross section", "m² (barn = 10⁻²⁸ m²)"), ("R", "Reaction rate", "s⁻¹"), ("I", "Beam intensity", "m⁻²s⁻¹"), ("n", "Target density", "m⁻²")),
    description="Effective target area for reaction. 1 barn = 10⁻²⁸ m².",
    status=NodeStatus.FUNDAMENTAL,
    tags=("cross_section", "scattering"),
)

# Fission Energy
fission_energy = EquationNode(
    id="fission_energy",
    name="Fission Energy Release",
    domain="nuclear_physics",
    latex=r"E_{fission} \approx 200 \text{ MeV per U-235 fission}",
    sympy="E_fission = 200",  # MeV
    variables=(("E_fission", "Energy per fission", "MeV")),
    description="~200 MeV per fission: KE of fragments (~170), neutrons (~5), gammas (~7), betas (~8), neutrinos (~10).",
    derives_from=("nuclear_binding_energy",),
    status=NodeStatus.EXPERIMENTAL,
    tags=("fission", "energy"),
)

# Critical Mass
critical_mass = EquationNode(
    id="critical_mass",
    name="Critical Mass (Simplified)",
    domain="nuclear_physics",
    latex=r"k_{eff} = \eta f p \epsilon P_{NL} = 1 \text{ (critical)}",
    sympy="k_eff = eta*f*p*epsilon*P_NL",
    variables=(("k_eff", "Effective multiplication factor", "dimensionless"), ("eta", "Neutrons per fission absorbed", "dimensionless"), ("f", "Thermal utilization", "dimensionless"), ("p", "Resonance escape probability", "dimensionless")),
    description="k=1 critical, k<1 subcritical, k>1 supercritical.",
    status=NodeStatus.PROVEN,
    tags=("fission", "reactor"),
)

# Fusion Energy
fusion_energy_dt = EquationNode(
    id="fusion_energy_dt",
    name="D-T Fusion Energy",
    domain="nuclear_physics",
    latex=r"D + T \rightarrow {}^4He + n + 17.6 \text{ MeV}",
    sympy="E_DT = 17.6",  # MeV
    variables=(("E_DT", "D-T fusion energy", "MeV")),
    description="Most accessible fusion reaction. Neutron carries 14.1 MeV.",
    derives_from=("nuclear_binding_energy",),
    status=NodeStatus.EXPERIMENTAL,
    tags=("fusion", "energy"),
)

# Lawson Criterion
lawson_criterion = EquationNode(
    id="lawson_criterion",
    name="Lawson Criterion",
    domain="nuclear_physics",
    latex=r"n\tau_E > 1.5 \times 10^{20} \text{ m}^{-3}\text{s} \quad \text{(for D-T at 10 keV)}",
    sympy="n*tau_E > 1.5e20",
    variables=(("n", "Plasma density", "m⁻³"), ("tau_E", "Energy confinement time", "s")),
    description="Condition for fusion breakeven. Triple product nTτ for ignition.",
    status=NodeStatus.PROVEN,
    tags=("fusion", "plasma"),
)

# Coulomb Barrier
coulomb_barrier = EquationNode(
    id="coulomb_barrier",
    name="Coulomb Barrier",
    domain="nuclear_physics",
    latex=r"V_C = \frac{Z_1 Z_2 e^2}{4\pi\epsilon_0 r} \approx \frac{1.44 Z_1 Z_2}{r[\text{fm}]} \text{ MeV}",
    sympy="V_C = k_e*Z1*Z2*e**2/r",
    variables=(("V_C", "Coulomb barrier height", "MeV"), ("Z1", "Atomic number 1", "dimensionless"), ("Z2", "Atomic number 2", "dimensionless"), ("r", "Distance", "fm")),
    description="Electrostatic barrier nuclei must overcome or tunnel through.",
    derives_from=("coulomb_law",),
    uses=("e", "k_e"),
    status=NodeStatus.PROVEN,
    tags=("barrier", "coulomb"),
)

# Gamow Factor
gamow_factor = EquationNode(
    id="gamow_factor",
    name="Gamow Factor",
    domain="nuclear_physics",
    latex=r"G = e^{-2\pi\eta}, \quad \eta = \frac{Z_1 Z_2 e^2}{4\pi\epsilon_0 \hbar v}",
    sympy="G = exp(-2*pi*eta)",
    variables=(("G", "Gamow factor", "dimensionless"), ("eta", "Sommerfeld parameter", "dimensionless"), ("v", "Relative velocity", "m/s")),
    description="Quantum tunneling probability through Coulomb barrier.",
    derives_from=("coulomb_barrier",),
    uses=("hbar", "e"),
    status=NodeStatus.PROVEN,
    tags=("tunneling", "fusion"),
)

# Neutron Moderation
neutron_moderation = EquationNode(
    id="neutron_moderation",
    name="Neutron Moderation (Average Energy Loss)",
    domain="nuclear_physics",
    latex=r"\xi = 1 + \frac{(A-1)^2}{2A}\ln\frac{A-1}{A+1} \approx \frac{2}{A+2/3}",
    sympy="xi = 1 + (A-1)**2/(2*A)*ln((A-1)/(A+1))",
    variables=(("xi", "Mean logarithmic energy decrement", "dimensionless"), ("A", "Moderator mass number", "dimensionless")),
    description="Energy loss per collision. ξ=1 for H (best moderator).",
    status=NodeStatus.PROVEN,
    tags=("neutron", "moderation"),
)

# Nuclear Radius
nuclear_radius = EquationNode(
    id="nuclear_radius",
    name="Nuclear Radius",
    domain="nuclear_physics",
    latex=r"R = r_0 A^{1/3}, \quad r_0 \approx 1.2-1.3 \text{ fm}",
    sympy="R = r_0 * A**(1/3)",
    variables=(("R", "Nuclear radius", "fm"), ("r_0", "Constant ~1.25 fm", "fm"), ("A", "Mass number", "dimensionless")),
    description="Nuclear volume ∝ A. Constant nuclear density ~2×10¹⁷ kg/m³.",
    status=NodeStatus.EXPERIMENTAL,
    tags=("nucleus", "size"),
)

NODES = [
    binding_energy, semf, q_value, cross_section, fission_energy,
    critical_mass, fusion_energy_dt, lawson_criterion, coulomb_barrier,
    gamow_factor, neutron_moderation, nuclear_radius
]
