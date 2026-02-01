"""
PATH: physics/knowledge/equations/fluids/turbulence.py
PURPOSE: Turbulence equations and models
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Turbulent Kinetic Energy
tke = EquationNode(
    id="turbulent_kinetic_energy",
    name="Turbulent Kinetic Energy",
    domain="fluid_dynamics",
    latex=r"k = \frac{1}{2}\langle u_i' u_i' \rangle = \frac{1}{2}(\overline{u'^2} + \overline{v'^2} + \overline{w'^2})",
    sympy="k = (1/2)*(u_prime**2 + v_prime**2 + w_prime**2)",
    variables=(("k", "TKE", "m²/s²"), ("u_prime", "Velocity fluctuation", "m/s")),
    description="Energy in turbulent fluctuations. Key quantity in turbulence modeling.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("turbulence", "energy"),
)

# Reynolds Stress
reynolds_stress = EquationNode(
    id="reynolds_stress",
    name="Reynolds Stress Tensor",
    domain="fluid_dynamics",
    latex=r"\tau_{ij}^R = -\rho \overline{u_i' u_j'}",
    sympy="tau_R = -rho*mean(u_i_prime * u_j_prime)",
    variables=(("tau_R", "Reynolds stress", "Pa"), ("u_prime", "Velocity fluctuation", "m/s")),
    description="Apparent stress from turbulent momentum transport. Closure problem in RANS.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("turbulence", "stress"),
)

# Boussinesq Hypothesis
boussinesq = EquationNode(
    id="boussinesq_hypothesis",
    name="Boussinesq Hypothesis",
    domain="fluid_dynamics",
    latex=r"-\overline{u_i' u_j'} = \nu_t\left(\frac{\partial \bar{u}_i}{\partial x_j} + \frac{\partial \bar{u}_j}{\partial x_i}\right) - \frac{2}{3}k\delta_{ij}",
    sympy="reynolds_stress = nu_t * (du_i/dx_j + du_j/dx_i) - 2/3*k*delta_ij",
    variables=(("nu_t", "Eddy viscosity", "m²/s"), ("k", "TKE", "m²/s²")),
    description="Relates Reynolds stress to mean strain rate. Foundation of eddy viscosity models.",
    status=NodeStatus.APPROXIMATE,
    tags=("turbulence", "modeling"),
)

# Kolmogorov Scales
kolmogorov_length = EquationNode(
    id="kolmogorov_length",
    name="Kolmogorov Length Scale",
    domain="fluid_dynamics",
    latex=r"\eta = \left(\frac{\nu^3}{\epsilon}\right)^{1/4}",
    sympy="eta = (nu**3/epsilon)**(1/4)",
    variables=(("eta", "Kolmogorov length", "m"), ("nu", "Kinematic viscosity", "m²/s"), ("epsilon", "Dissipation rate", "m²/s³")),
    description="Smallest scale in turbulence where viscous dissipation occurs.",
    status=NodeStatus.PROVEN,
    tags=("turbulence", "scales"),
)

kolmogorov_time = EquationNode(
    id="kolmogorov_time",
    name="Kolmogorov Time Scale",
    domain="fluid_dynamics",
    latex=r"\tau_\eta = \left(\frac{\nu}{\epsilon}\right)^{1/2}",
    sympy="tau_eta = (nu/epsilon)**(1/2)",
    variables=(("tau_eta", "Kolmogorov time", "s")),
    description="Smallest time scale in turbulence.",
    derives_from=("kolmogorov_length",),
    status=NodeStatus.PROVEN,
    tags=("turbulence", "scales"),
)

kolmogorov_velocity = EquationNode(
    id="kolmogorov_velocity",
    name="Kolmogorov Velocity Scale",
    domain="fluid_dynamics",
    latex=r"v_\eta = (\nu\epsilon)^{1/4}",
    sympy="v_eta = (nu*epsilon)**(1/4)",
    variables=(("v_eta", "Kolmogorov velocity", "m/s")),
    description="Velocity scale at smallest turbulent eddies.",
    derives_from=("kolmogorov_length",),
    status=NodeStatus.PROVEN,
    tags=("turbulence", "scales"),
)

# Energy Cascade
kolmogorov_spectrum = EquationNode(
    id="kolmogorov_spectrum",
    name="Kolmogorov Energy Spectrum",
    domain="fluid_dynamics",
    latex=r"E(k) = C_K \epsilon^{2/3} k^{-5/3}",
    sympy="E_k = C_K * epsilon**(2/3) * k**(-5/3)",
    variables=(("E_k", "Energy spectrum", "m³/s²"), ("C_K", "Kolmogorov constant ≈1.5", "dimensionless"), ("epsilon", "Dissipation", "m²/s³"), ("k", "Wavenumber", "m⁻¹")),
    description="Energy distribution in inertial subrange. -5/3 law.",
    status=NodeStatus.EXPERIMENTAL,
    tags=("turbulence", "spectrum"),
)

# Taylor Microscale
taylor_microscale = EquationNode(
    id="taylor_microscale",
    name="Taylor Microscale",
    domain="fluid_dynamics",
    latex=r"\lambda = \sqrt{\frac{10\nu k}{\epsilon}}",
    sympy="lambda_T = sqrt(10*nu*k/epsilon)",
    variables=(("lambda_T", "Taylor microscale", "m"), ("nu", "Kinematic viscosity", "m²/s"), ("k", "TKE", "m²/s²")),
    description="Intermediate scale between energy-containing and dissipative eddies.",
    status=NodeStatus.PROVEN,
    tags=("turbulence", "scales"),
)

# Integral Length Scale
integral_length = EquationNode(
    id="integral_length_scale",
    name="Integral Length Scale",
    domain="fluid_dynamics",
    latex=r"L = \frac{k^{3/2}}{\epsilon}",
    sympy="L = k**(3/2)/epsilon",
    variables=(("L", "Integral scale", "m"), ("k", "TKE", "m²/s²"), ("epsilon", "Dissipation", "m²/s³")),
    description="Size of largest energy-containing eddies.",
    status=NodeStatus.PROVEN,
    tags=("turbulence", "scales"),
)

# k-epsilon Model
k_epsilon = EquationNode(
    id="k_epsilon_model",
    name="k-ε Turbulence Model",
    domain="fluid_dynamics",
    latex=r"\nu_t = C_\mu \frac{k^2}{\epsilon}",
    sympy="nu_t = C_mu * k**2 / epsilon",
    variables=(("nu_t", "Eddy viscosity", "m²/s"), ("C_mu", "Model constant ≈0.09", "dimensionless"), ("k", "TKE", "m²/s²"), ("epsilon", "Dissipation", "m²/s³")),
    description="Two-equation turbulence model. Most widely used in CFD.",
    derives_from=("boussinesq_hypothesis",),
    status=NodeStatus.APPROXIMATE,
    tags=("turbulence", "rans", "model"),
)

# k-omega Model
k_omega = EquationNode(
    id="k_omega_model",
    name="k-ω Turbulence Model",
    domain="fluid_dynamics",
    latex=r"\nu_t = \frac{k}{\omega}",
    sympy="nu_t = k/omega",
    variables=(("nu_t", "Eddy viscosity", "m²/s"), ("k", "TKE", "m²/s²"), ("omega", "Specific dissipation", "s⁻¹")),
    description="Two-equation model better for near-wall flows than k-ε.",
    derives_from=("boussinesq_hypothesis",),
    status=NodeStatus.APPROXIMATE,
    tags=("turbulence", "rans", "model"),
)

# Wall Law (Log Law)
log_law = EquationNode(
    id="log_law_of_wall",
    name="Log Law of the Wall",
    domain="fluid_dynamics",
    latex=r"u^+ = \frac{1}{\kappa}\ln(y^+) + B",
    sympy="u_plus = (1/kappa)*ln(y_plus) + B",
    variables=(("u_plus", "u/u_τ dimensionless velocity", "dimensionless"), ("y_plus", "yu_τ/ν wall distance", "dimensionless"), ("kappa", "von Kármán constant ≈0.41", "dimensionless"), ("B", "Log-law constant ≈5.0", "dimensionless")),
    description="Universal velocity profile in turbulent boundary layer log region.",
    status=NodeStatus.EXPERIMENTAL,
    tags=("turbulence", "boundary_layer"),
)

# Viscous Sublayer
viscous_sublayer = EquationNode(
    id="viscous_sublayer",
    name="Viscous Sublayer Law",
    domain="fluid_dynamics",
    latex=r"u^+ = y^+ \quad (y^+ < 5)",
    sympy="u_plus = y_plus",
    variables=(("u_plus", "Dimensionless velocity", "dimensionless"), ("y_plus", "Dimensionless wall distance", "dimensionless")),
    description="Linear velocity profile very close to wall where viscous forces dominate.",
    conditions=("y+ < 5",),
    status=NodeStatus.EXPERIMENTAL,
    tags=("turbulence", "boundary_layer"),
)

# Friction Velocity
friction_velocity = EquationNode(
    id="friction_velocity",
    name="Friction Velocity",
    domain="fluid_dynamics",
    latex=r"u_\tau = \sqrt{\frac{\tau_w}{\rho}}",
    sympy="u_tau = sqrt(tau_w/rho)",
    variables=(("u_tau", "Friction velocity", "m/s"), ("tau_w", "Wall shear stress", "Pa"), ("rho", "Density", "kg/m³")),
    description="Characteristic velocity scale for wall-bounded turbulent flows.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("turbulence", "wall"),
)

# Turbulence Intensity
turbulence_intensity = EquationNode(
    id="turbulence_intensity",
    name="Turbulence Intensity",
    domain="fluid_dynamics",
    latex=r"I = \frac{\sqrt{2k/3}}{U} = \frac{u'_{rms}}{U}",
    sympy="I = sqrt(2*k/3)/U",
    variables=(("I", "Turbulence intensity", "dimensionless"), ("k", "TKE", "m²/s²"), ("U", "Mean velocity", "m/s")),
    description="Ratio of RMS velocity fluctuation to mean velocity.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("turbulence", "intensity"),
)

NODES = [
    tke, reynolds_stress, boussinesq, kolmogorov_length, kolmogorov_time, kolmogorov_velocity,
    kolmogorov_spectrum, taylor_microscale, integral_length, k_epsilon, k_omega,
    log_law, viscous_sublayer, friction_velocity, turbulence_intensity
]
