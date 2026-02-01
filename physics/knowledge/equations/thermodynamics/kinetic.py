"""
PATH: physics/knowledge/equations/thermodynamics/kinetic.py
PURPOSE: Kinetic theory of gases equations
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Maxwell-Boltzmann Speed Distribution
maxwell_boltzmann = EquationNode(
    id="maxwell_boltzmann_speed",
    name="Maxwell-Boltzmann Speed Distribution",
    domain="thermodynamics",
    latex=r"f(v) = 4\pi n\left(\frac{m}{2\pi k_B T}\right)^{3/2} v^2 e^{-mv^2/2k_B T}",
    sympy="f_v = 4*pi*n*(m/(2*pi*k_B*T))**(3/2)*v**2*exp(-m*v**2/(2*k_B*T))",
    variables=(("f_v", "Speed distribution", "s/m"), ("v", "Speed", "m/s"), ("m", "Particle mass", "kg"), ("T", "Temperature", "K")),
    description="Distribution of molecular speeds in ideal gas at equilibrium.",
    uses=("k_B",),
    status=NodeStatus.PROVEN,
    tags=("kinetic_theory", "distribution"),
)

# Most Probable Speed
most_probable_speed = EquationNode(
    id="most_probable_speed",
    name="Most Probable Speed",
    domain="thermodynamics",
    latex=r"v_p = \sqrt{\frac{2k_B T}{m}}",
    sympy="v_p = sqrt(2*k_B*T/m)",
    variables=(("v_p", "Most probable speed", "m/s")),
    description="Speed at peak of Maxwell-Boltzmann distribution.",
    derives_from=("maxwell_boltzmann_speed",),
    uses=("k_B",),
    status=NodeStatus.PROVEN,
    tags=("kinetic_theory", "speed"),
)

# Mean Speed
mean_speed = EquationNode(
    id="mean_speed",
    name="Mean Speed",
    domain="thermodynamics",
    latex=r"\bar{v} = \sqrt{\frac{8k_B T}{\pi m}}",
    sympy="v_mean = sqrt(8*k_B*T/(pi*m))",
    variables=(("v_mean", "Mean speed", "m/s")),
    description="Average speed of molecules. v̄ = 1.128 v_p.",
    derives_from=("maxwell_boltzmann_speed",),
    uses=("k_B",),
    status=NodeStatus.PROVEN,
    tags=("kinetic_theory", "speed"),
)

# RMS Speed
rms_speed = EquationNode(
    id="rms_speed",
    name="RMS Speed",
    domain="thermodynamics",
    latex=r"v_{rms} = \sqrt{\frac{3k_B T}{m}}",
    sympy="v_rms = sqrt(3*k_B*T/m)",
    variables=(("v_rms", "RMS speed", "m/s")),
    description="Root-mean-square speed. v_rms = 1.225 v_p.",
    derives_from=("maxwell_boltzmann_speed",),
    uses=("k_B",),
    status=NodeStatus.PROVEN,
    tags=("kinetic_theory", "speed"),
)

# Pressure from Kinetic Theory
pressure_kinetic = EquationNode(
    id="pressure_kinetic_theory",
    name="Pressure from Kinetic Theory",
    domain="thermodynamics",
    latex=r"P = \frac{1}{3}\rho v_{rms}^2 = \frac{1}{3}nm\langle v^2\rangle = nk_B T",
    sympy="P = (1/3)*rho*v_rms**2 = n*k_B*T",
    variables=(("P", "Pressure", "Pa"), ("rho", "Density", "kg/m³"), ("n", "Number density", "m⁻³")),
    description="Ideal gas law from molecular collisions with walls.",
    derives_from=("rms_speed",),
    uses=("k_B",),
    status=NodeStatus.PROVEN,
    tags=("kinetic_theory", "pressure"),
)

# Mean Free Path
mean_free_path = EquationNode(
    id="mean_free_path",
    name="Mean Free Path",
    domain="thermodynamics",
    latex=r"\lambda = \frac{1}{\sqrt{2}\pi d^2 n} = \frac{k_B T}{\sqrt{2}\pi d^2 P}",
    sympy="lambda = 1/(sqrt(2)*pi*d**2*n)",
    variables=(("lambda", "Mean free path", "m"), ("d", "Molecular diameter", "m"), ("n", "Number density", "m⁻³")),
    description="Average distance between collisions. Air at STP: λ ~ 70 nm.",
    uses=("k_B",),
    status=NodeStatus.PROVEN,
    tags=("kinetic_theory", "collision"),
)

# Collision Frequency
collision_freq = EquationNode(
    id="collision_frequency_kinetic",
    name="Collision Frequency",
    domain="thermodynamics",
    latex=r"Z = \frac{\bar{v}}{\lambda} = \sqrt{2}\pi d^2 n \bar{v}",
    sympy="Z = v_mean/lambda",
    variables=(("Z", "Collision frequency", "s⁻¹"), ("lambda", "Mean free path", "m"), ("v_mean", "Mean speed", "m/s")),
    description="Collisions per second per molecule. Air at STP: Z ~ 5×10⁹ s⁻¹.",
    derives_from=("mean_free_path", "mean_speed"),
    status=NodeStatus.PROVEN,
    tags=("kinetic_theory", "collision"),
)

# Viscosity from Kinetic Theory
viscosity_kinetic = EquationNode(
    id="viscosity_kinetic",
    name="Viscosity from Kinetic Theory",
    domain="thermodynamics",
    latex=r"\eta = \frac{1}{3}\rho \bar{v} \lambda = \frac{2}{3\pi^{3/2}}\frac{\sqrt{mk_BT}}{d^2}",
    sympy="eta = (1/3)*rho*v_mean*lambda",
    variables=(("eta", "Dynamic viscosity", "Pa⋅s")),
    description="Gas viscosity ∝ √T, independent of pressure (low P).",
    derives_from=("mean_free_path", "mean_speed"),
    uses=("k_B",),
    status=NodeStatus.APPROXIMATE,
    tags=("kinetic_theory", "transport"),
)

# Thermal Conductivity from Kinetic Theory
thermal_conductivity_kinetic = EquationNode(
    id="thermal_conductivity_kinetic",
    name="Thermal Conductivity from Kinetic Theory",
    domain="thermodynamics",
    latex=r"\kappa = \frac{1}{3}nmc_v\bar{v}\lambda",
    sympy="kappa = (1/3)*n*m*c_v*v_mean*lambda",
    variables=(("kappa", "Thermal conductivity", "W/(m⋅K)"), ("c_v", "Specific heat at constant V", "J/(kg⋅K)")),
    description="Heat conduction by molecular motion.",
    derives_from=("mean_free_path", "mean_speed"),
    status=NodeStatus.APPROXIMATE,
    tags=("kinetic_theory", "transport"),
)

# Diffusion Coefficient
diffusion_kinetic = EquationNode(
    id="diffusion_kinetic",
    name="Diffusion Coefficient from Kinetic Theory",
    domain="thermodynamics",
    latex=r"D = \frac{1}{3}\bar{v}\lambda",
    sympy="D = (1/3)*v_mean*lambda",
    variables=(("D", "Diffusion coefficient", "m²/s")),
    description="Self-diffusion coefficient. D ∝ T^(3/2)/P.",
    derives_from=("mean_free_path", "mean_speed"),
    status=NodeStatus.APPROXIMATE,
    tags=("kinetic_theory", "transport"),
)

# Effusion Rate
effusion = EquationNode(
    id="effusion_rate",
    name="Effusion Rate (Graham's Law)",
    domain="thermodynamics",
    latex=r"\frac{r_1}{r_2} = \sqrt{\frac{M_2}{M_1}}",
    sympy="r1/r2 = sqrt(M2/M1)",
    variables=(("r", "Effusion rate", "mol/s"), ("M", "Molar mass", "kg/mol")),
    description="Lighter gases effuse faster. Used for isotope separation.",
    status=NodeStatus.PROVEN,
    tags=("effusion", "isotope"),
)

# Equipartition Theorem
equipartition = EquationNode(
    id="equipartition_theorem",
    name="Equipartition Theorem",
    domain="thermodynamics",
    latex=r"\langle E_{quadratic}\rangle = \frac{1}{2}k_B T \text{ per degree of freedom}",
    sympy="E_dof = (1/2)*k_B*T",
    variables=(("E_dof", "Energy per DOF", "J")),
    description="Each quadratic term in energy contributes kT/2. Monatomic: 3, diatomic: 5 (low T), 7 (high T).",
    uses=("k_B",),
    status=NodeStatus.PROVEN,
    tags=("kinetic_theory", "energy"),
)

NODES = [
    maxwell_boltzmann, most_probable_speed, mean_speed, rms_speed, pressure_kinetic,
    mean_free_path, collision_freq, viscosity_kinetic, thermal_conductivity_kinetic,
    diffusion_kinetic, effusion, equipartition
]
