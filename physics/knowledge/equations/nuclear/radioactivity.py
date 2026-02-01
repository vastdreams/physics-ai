"""
PATH: physics/knowledge/equations/nuclear/radioactivity.py
PURPOSE: Radioactive decay equations
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Radioactive Decay Law
decay_law = EquationNode(
    id="radioactive_decay_law",
    name="Radioactive Decay Law",
    domain="nuclear_physics",
    latex=r"N(t) = N_0 e^{-\lambda t}",
    sympy="N = N_0 * exp(-lambda*t)",
    variables=(("N", "Number of nuclei", "dimensionless"), ("N_0", "Initial number", "dimensionless"), ("lambda", "Decay constant", "s⁻¹"), ("t", "Time", "s")),
    description="Exponential decay of unstable nuclei. First-order kinetics.",
    status=NodeStatus.PROVEN,
    tags=("decay", "exponential"),
)

# Half-Life
half_life = EquationNode(
    id="half_life",
    name="Half-Life",
    domain="nuclear_physics",
    latex=r"t_{1/2} = \frac{\ln 2}{\lambda} \approx \frac{0.693}{\lambda}",
    sympy="t_half = ln(2)/lambda",
    variables=(("t_half", "Half-life", "s"), ("lambda", "Decay constant", "s⁻¹")),
    description="Time for half of nuclei to decay. Ranges from <1s to >10⁹ years.",
    derives_from=("radioactive_decay_law",),
    status=NodeStatus.PROVEN,
    tags=("decay", "half_life"),
)

# Mean Lifetime
mean_lifetime = EquationNode(
    id="mean_lifetime",
    name="Mean Lifetime",
    domain="nuclear_physics",
    latex=r"\tau = \frac{1}{\lambda} = \frac{t_{1/2}}{\ln 2}",
    sympy="tau = 1/lambda",
    variables=(("tau", "Mean lifetime", "s"), ("lambda", "Decay constant", "s⁻¹")),
    description="Average lifetime of nucleus. τ = 1.443 × t₁/₂.",
    derives_from=("radioactive_decay_law",),
    status=NodeStatus.PROVEN,
    tags=("decay", "lifetime"),
)

# Activity
activity = EquationNode(
    id="activity",
    name="Activity",
    domain="nuclear_physics",
    latex=r"A = -\frac{dN}{dt} = \lambda N = \lambda N_0 e^{-\lambda t}",
    sympy="A = lambda*N",
    variables=(("A", "Activity", "Bq"), ("lambda", "Decay constant", "s⁻¹"), ("N", "Number of nuclei", "dimensionless")),
    description="Decays per second. 1 Bq = 1 decay/s. 1 Ci = 3.7×10¹⁰ Bq.",
    derives_from=("radioactive_decay_law",),
    status=NodeStatus.PROVEN,
    tags=("decay", "activity"),
)

# Decay Chain (Bateman Equation simplified)
decay_chain = EquationNode(
    id="decay_chain",
    name="Decay Chain (Secular Equilibrium)",
    domain="nuclear_physics",
    latex=r"A_1 = A_2 = ... = A_n \quad \text{when } t \gg t_{1/2,parent}",
    sympy="A1 = A2 = A_n",
    variables=(("A_i", "Activity of nuclide i", "Bq")),
    description="In equilibrium, daughter activities equal parent activity.",
    derives_from=("radioactive_decay_law",),
    conditions=("λ_parent << λ_daughter", "Secular equilibrium"),
    status=NodeStatus.PROVEN,
    tags=("decay", "chain"),
)

# Alpha Decay Energy
alpha_decay = EquationNode(
    id="alpha_decay_energy",
    name="Alpha Decay Q-Value",
    domain="nuclear_physics",
    latex=r"Q_\alpha = (m_P - m_D - m_\alpha)c^2",
    sympy="Q_alpha = (m_P - m_D - m_alpha)*c**2",
    variables=(("Q_alpha", "Q-value", "J"), ("m_P", "Parent mass", "kg"), ("m_D", "Daughter mass", "kg"), ("m_alpha", "Alpha mass", "kg")),
    description="Energy released in alpha decay. Shared between α and recoil nucleus.",
    status=NodeStatus.PROVEN,
    tags=("alpha", "energy"),
)

# Geiger-Nuttall Law
geiger_nuttall = EquationNode(
    id="geiger_nuttall",
    name="Geiger-Nuttall Law",
    domain="nuclear_physics",
    latex=r"\log t_{1/2} = a + \frac{b}{\sqrt{E_\alpha}}",
    sympy="log(t_half) = a + b/sqrt(E_alpha)",
    variables=(("t_half", "Half-life", "s"), ("E_alpha", "Alpha energy", "MeV"), ("a", "Constant", "dimensionless"), ("b", "Constant", "MeV^0.5")),
    description="Empirical relation: higher energy α = shorter half-life.",
    status=NodeStatus.EMPIRICAL,
    tags=("alpha", "tunneling"),
)

# Beta Decay Spectrum
beta_spectrum = EquationNode(
    id="beta_decay_spectrum",
    name="Beta Decay Energy Spectrum",
    domain="nuclear_physics",
    latex=r"N(E_e) \propto E_e(Q - E_e)^2 p_e F(Z, E_e)",
    sympy="N_E ~ E_e*(Q - E_e)**2 * p_e * F(Z, E_e)",
    variables=(("N_E", "Electron count", "dimensionless"), ("E_e", "Electron energy", "MeV"), ("Q", "Maximum energy", "MeV"), ("F", "Fermi function", "dimensionless")),
    description="Continuous beta spectrum due to neutrino carrying variable energy.",
    status=NodeStatus.PROVEN,
    tags=("beta", "spectrum"),
)

# Fermi's Golden Rule (Decay)
fermi_golden_rule = EquationNode(
    id="fermi_golden_rule",
    name="Fermi's Golden Rule",
    domain="nuclear_physics",
    latex=r"\Gamma = \frac{2\pi}{\hbar}|M_{fi}|^2 \rho(E_f)",
    sympy="Gamma = 2*pi/hbar * |M_fi|**2 * rho_E",
    variables=(("Gamma", "Decay rate", "s⁻¹"), ("M_fi", "Matrix element", "J"), ("rho_E", "Density of final states", "J⁻¹")),
    description="Transition rate from perturbation theory. Basis of decay calculations.",
    uses=("hbar",),
    status=NodeStatus.PROVEN,
    tags=("decay", "quantum"),
)

# Gamma Ray Attenuation
gamma_attenuation = EquationNode(
    id="gamma_attenuation",
    name="Gamma Ray Attenuation",
    domain="nuclear_physics",
    latex=r"I(x) = I_0 e^{-\mu x}",
    sympy="I = I_0 * exp(-mu*x)",
    variables=(("I", "Intensity", "W/m²"), ("I_0", "Initial intensity", "W/m²"), ("mu", "Linear attenuation coefficient", "m⁻¹"), ("x", "Thickness", "m")),
    description="Exponential decrease of gamma intensity in matter.",
    status=NodeStatus.PROVEN,
    tags=("gamma", "attenuation"),
)

# Half-Value Layer
half_value_layer = EquationNode(
    id="half_value_layer",
    name="Half-Value Layer",
    domain="nuclear_physics",
    latex=r"HVL = \frac{\ln 2}{\mu}",
    sympy="HVL = ln(2)/mu",
    variables=(("HVL", "Half-value layer", "m"), ("mu", "Attenuation coefficient", "m⁻¹")),
    description="Thickness to reduce gamma intensity by half.",
    derives_from=("gamma_attenuation",),
    status=NodeStatus.PROVEN,
    tags=("gamma", "shielding"),
)

# Absorbed Dose
absorbed_dose = EquationNode(
    id="absorbed_dose",
    name="Absorbed Dose",
    domain="nuclear_physics",
    latex=r"D = \frac{E_{absorbed}}{m} \quad [Gy = J/kg]",
    sympy="D = E_abs/m",
    variables=(("D", "Absorbed dose", "Gy"), ("E_abs", "Energy absorbed", "J"), ("m", "Mass", "kg")),
    description="Energy absorbed per unit mass. 1 Gray = 1 J/kg.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("dose", "radiation"),
)

# Equivalent Dose
equivalent_dose = EquationNode(
    id="equivalent_dose",
    name="Equivalent Dose",
    domain="nuclear_physics",
    latex=r"H = w_R \cdot D \quad [Sv]",
    sympy="H = w_R * D",
    variables=(("H", "Equivalent dose", "Sv"), ("w_R", "Radiation weighting factor", "dimensionless"), ("D", "Absorbed dose", "Gy")),
    description="Biological effect weighted. w_R=1 for γ,β; w_R=20 for α, neutrons.",
    derives_from=("absorbed_dose",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("dose", "biological"),
)

NODES = [
    decay_law, half_life, mean_lifetime, activity, decay_chain,
    alpha_decay, geiger_nuttall, beta_spectrum, fermi_golden_rule,
    gamma_attenuation, half_value_layer, absorbed_dose, equivalent_dose
]
