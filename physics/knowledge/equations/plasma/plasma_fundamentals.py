"""
PATH: physics/knowledge/equations/plasma/plasma_fundamentals.py
PURPOSE: Fundamental plasma physics equations
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Plasma Frequency
plasma_frequency = EquationNode(
    id="plasma_frequency",
    name="Plasma Frequency",
    domain="plasma_physics",
    latex=r"\omega_p = \sqrt{\frac{n_e e^2}{\epsilon_0 m_e}}",
    sympy="omega_p = sqrt(n_e*e**2/(epsilon_0*m_e))",
    variables=(("omega_p", "Plasma frequency", "rad/s"), ("n_e", "Electron density", "m⁻³"), ("e", "Electron charge", "C"), ("m_e", "Electron mass", "kg")),
    description="Natural oscillation frequency of electrons. EM waves with ω < ω_p reflected.",
    uses=("e", "epsilon_0", "m_e"),
    status=NodeStatus.FUNDAMENTAL,
    tags=("plasma", "oscillation"),
)

# Debye Length
debye_length = EquationNode(
    id="debye_length",
    name="Debye Length",
    domain="plasma_physics",
    latex=r"\lambda_D = \sqrt{\frac{\epsilon_0 k_B T_e}{n_e e^2}}",
    sympy="lambda_D = sqrt(epsilon_0*k_B*T_e/(n_e*e**2))",
    variables=(("lambda_D", "Debye length", "m"), ("T_e", "Electron temperature", "K"), ("n_e", "Electron density", "m⁻³")),
    description="Screening distance. Charges shielded beyond this. λ_D ~ cm in lab, ~10m in ionosphere.",
    uses=("epsilon_0", "k_B", "e"),
    status=NodeStatus.FUNDAMENTAL,
    tags=("plasma", "shielding"),
)

# Plasma Parameter
plasma_parameter = EquationNode(
    id="plasma_parameter",
    name="Plasma Parameter",
    domain="plasma_physics",
    latex=r"\Lambda = 4\pi n_e \lambda_D^3 = \frac{4\pi}{3}\times(\text{particles in Debye sphere})",
    sympy="Lambda = 4*pi*n_e*lambda_D**3",
    variables=(("Lambda", "Plasma parameter", "dimensionless"), ("n_e", "Electron density", "m⁻³"), ("lambda_D", "Debye length", "m")),
    description="Number of particles in Debye sphere. Λ >> 1 for ideal plasma.",
    derives_from=("debye_length",),
    status=NodeStatus.PROVEN,
    tags=("plasma", "collective"),
)

# Cyclotron Frequency
cyclotron_frequency = EquationNode(
    id="cyclotron_frequency",
    name="Cyclotron (Gyro) Frequency",
    domain="plasma_physics",
    latex=r"\omega_c = \frac{|q|B}{m}",
    sympy="omega_c = |q|*B/m",
    variables=(("omega_c", "Cyclotron frequency", "rad/s"), ("q", "Particle charge", "C"), ("B", "Magnetic field", "T"), ("m", "Particle mass", "kg")),
    description="Rotation frequency around B-field. For electron: ω_ce ≈ 1.76×10¹¹ B rad/s.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("plasma", "magnetic"),
)

# Larmor Radius
larmor_radius = EquationNode(
    id="larmor_radius",
    name="Larmor (Gyro) Radius",
    domain="plasma_physics",
    latex=r"r_L = \frac{v_\perp}{\omega_c} = \frac{mv_\perp}{|q|B}",
    sympy="r_L = m*v_perp/(|q|*B)",
    variables=(("r_L", "Larmor radius", "m"), ("v_perp", "Perpendicular velocity", "m/s"), ("omega_c", "Cyclotron frequency", "rad/s")),
    description="Radius of particle orbit around B-field line.",
    derives_from=("cyclotron_frequency",),
    status=NodeStatus.PROVEN,
    tags=("plasma", "magnetic"),
)

# Thermal Velocity
thermal_velocity = EquationNode(
    id="thermal_velocity",
    name="Thermal Velocity",
    domain="plasma_physics",
    latex=r"v_{th} = \sqrt{\frac{k_B T}{m}}",
    sympy="v_th = sqrt(k_B*T/m)",
    variables=(("v_th", "Thermal velocity", "m/s"), ("T", "Temperature", "K"), ("m", "Particle mass", "kg")),
    description="Characteristic speed of particles at temperature T.",
    uses=("k_B",),
    status=NodeStatus.PROVEN,
    tags=("thermal", "velocity"),
)

# Collision Frequency
collision_frequency = EquationNode(
    id="collision_frequency",
    name="Electron-Ion Collision Frequency",
    domain="plasma_physics",
    latex=r"\nu_{ei} \approx \frac{n_e e^4 \ln\Lambda}{4\pi\epsilon_0^2 m_e^2 v_{th,e}^3}",
    sympy="nu_ei ~ n_e*e**4*ln(Lambda)/(4*pi*epsilon_0**2*m_e**2*v_th**3)",
    variables=(("nu_ei", "Collision frequency", "s⁻¹"), ("ln_Lambda", "Coulomb logarithm ~10-20", "dimensionless")),
    description="Electron-ion collision rate. Determines resistivity.",
    uses=("e", "epsilon_0", "m_e"),
    status=NodeStatus.APPROXIMATE,
    tags=("collision", "transport"),
)

# Spitzer Resistivity
spitzer_resistivity = EquationNode(
    id="spitzer_resistivity",
    name="Spitzer Resistivity",
    domain="plasma_physics",
    latex=r"\eta = \frac{m_e \nu_{ei}}{n_e e^2} \approx 5 \times 10^{-3} \frac{Z \ln\Lambda}{T_e^{3/2}} \text{ Ω⋅m}",
    sympy="eta = m_e*nu_ei/(n_e*e**2)",
    variables=(("eta", "Resistivity", "Ω⋅m"), ("Z", "Ion charge number", "dimensionless"), ("T_e", "Electron temperature in eV", "eV")),
    description="Classical plasma resistivity. η ∝ T^(-3/2).",
    derives_from=("collision_frequency",),
    status=NodeStatus.PROVEN,
    tags=("resistivity", "transport"),
)

# Langmuir Probe
langmuir_probe = EquationNode(
    id="langmuir_probe",
    name="Langmuir Probe Current",
    domain="plasma_physics",
    latex=r"I = I_{sat}\left(1 - e^{-e(V-V_p)/k_B T_e}\right)",
    sympy="I = I_sat*(1 - exp(-e*(V-V_p)/(k_B*T_e)))",
    variables=(("I", "Probe current", "A"), ("I_sat", "Saturation current", "A"), ("V", "Probe voltage", "V"), ("V_p", "Plasma potential", "V")),
    description="I-V characteristic of Langmuir probe. Determines n_e and T_e.",
    uses=("e", "k_B"),
    status=NodeStatus.PROVEN,
    tags=("diagnostic", "probe"),
)

# Child-Langmuir Law
child_langmuir = EquationNode(
    id="child_langmuir",
    name="Child-Langmuir Law",
    domain="plasma_physics",
    latex=r"j = \frac{4\epsilon_0}{9}\sqrt{\frac{2e}{m}}\frac{V^{3/2}}{d^2}",
    sympy="j = 4*epsilon_0/9 * sqrt(2*e/m) * V**(3/2)/d**2",
    variables=(("j", "Current density", "A/m²"), ("V", "Voltage", "V"), ("d", "Gap distance", "m")),
    description="Space-charge-limited current between electrodes.",
    uses=("epsilon_0", "e"),
    status=NodeStatus.PROVEN,
    tags=("sheath", "current"),
)

# Bohm Criterion
bohm_criterion = EquationNode(
    id="bohm_criterion",
    name="Bohm Criterion",
    domain="plasma_physics",
    latex=r"v_s \geq c_s = \sqrt{\frac{k_B T_e}{m_i}}",
    sympy="v_s >= sqrt(k_B*T_e/m_i)",
    variables=(("v_s", "Ion velocity at sheath edge", "m/s"), ("c_s", "Ion sound speed", "m/s"), ("T_e", "Electron temperature", "K"), ("m_i", "Ion mass", "kg")),
    description="Ions must enter sheath at least at sound speed.",
    uses=("k_B",),
    status=NodeStatus.PROVEN,
    tags=("sheath", "boundary"),
)

# Debye Shielding
debye_potential = EquationNode(
    id="debye_shielding",
    name="Debye Shielding Potential",
    domain="plasma_physics",
    latex=r"\phi(r) = \frac{q}{4\pi\epsilon_0 r}e^{-r/\lambda_D}",
    sympy="phi = q/(4*pi*epsilon_0*r)*exp(-r/lambda_D)",
    variables=(("phi", "Potential", "V"), ("r", "Distance", "m"), ("lambda_D", "Debye length", "m")),
    description="Screened Coulomb potential in plasma.",
    derives_from=("debye_length",),
    uses=("epsilon_0",),
    status=NodeStatus.PROVEN,
    tags=("shielding", "potential"),
)

NODES = [
    plasma_frequency, debye_length, plasma_parameter, cyclotron_frequency, larmor_radius,
    thermal_velocity, collision_frequency, spitzer_resistivity, langmuir_probe,
    child_langmuir, bohm_criterion, debye_potential
]
