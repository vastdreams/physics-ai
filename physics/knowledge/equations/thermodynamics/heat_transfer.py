"""
PATH: physics/knowledge/equations/thermodynamics/heat_transfer.py
PURPOSE: Heat transfer equations - conduction, convection, radiation
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Fourier's Law
fourier_law = EquationNode(
    id="fourier_law",
    name="Fourier's Law of Heat Conduction",
    domain="thermodynamics",
    latex=r"\vec{q} = -k\nabla T \quad \text{or} \quad \dot{Q} = -kA\frac{dT}{dx}",
    sympy="q = -k*grad(T)",
    variables=(("q", "Heat flux", "W/m²"), ("k", "Thermal conductivity", "W/(m⋅K)"), ("T", "Temperature", "K")),
    description="Heat flows from hot to cold. Metals: k~100-400, insulators: k~0.01-0.1 W/(m⋅K).",
    status=NodeStatus.FUNDAMENTAL,
    tags=("conduction", "heat"),
)

# Heat Equation
heat_equation = EquationNode(
    id="heat_equation",
    name="Heat Equation",
    domain="thermodynamics",
    latex=r"\frac{\partial T}{\partial t} = \alpha \nabla^2 T, \quad \alpha = \frac{k}{\rho c_p}",
    sympy="dT/dt = alpha*laplacian(T)",
    variables=(("T", "Temperature", "K"), ("alpha", "Thermal diffusivity", "m²/s")),
    description="Parabolic PDE for temperature evolution. Diffusion equation.",
    derives_from=("fourier_law",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("conduction", "diffusion"),
)

# Thermal Resistance
thermal_resistance = EquationNode(
    id="thermal_resistance",
    name="Thermal Resistance",
    domain="thermodynamics",
    latex=r"R_{th} = \frac{L}{kA}, \quad \dot{Q} = \frac{\Delta T}{R_{th}}",
    sympy="R_th = L/(k*A)",
    variables=(("R_th", "Thermal resistance", "K/W"), ("L", "Thickness", "m"), ("k", "Conductivity", "W/(m⋅K)"), ("A", "Area", "m²")),
    description="Analog to electrical resistance. Resistances in series add.",
    derives_from=("fourier_law",),
    status=NodeStatus.PROVEN,
    tags=("resistance", "conduction"),
)

# Newton's Law of Cooling
newton_cooling = EquationNode(
    id="newton_cooling",
    name="Newton's Law of Cooling",
    domain="thermodynamics",
    latex=r"\dot{Q} = hA(T_s - T_\infty)",
    sympy="Q_dot = h*A*(T_s - T_inf)",
    variables=(("Q_dot", "Heat transfer rate", "W"), ("h", "Heat transfer coefficient", "W/(m²⋅K)"), ("T_s", "Surface temperature", "K"), ("T_inf", "Ambient temperature", "K")),
    description="Convective heat transfer. h = 5-25 (free), 25-250 (forced) W/(m²⋅K) in air.",
    status=NodeStatus.EMPIRICAL,
    tags=("convection", "cooling"),
)

# Nusselt Number
nusselt_number = EquationNode(
    id="nusselt_number",
    name="Nusselt Number",
    domain="thermodynamics",
    latex=r"Nu = \frac{hL}{k}",
    sympy="Nu = h*L/k",
    variables=(("Nu", "Nusselt number", "dimensionless"), ("h", "Heat transfer coefficient", "W/(m²⋅K)"), ("L", "Characteristic length", "m"), ("k", "Fluid conductivity", "W/(m⋅K)")),
    description="Ratio of convective to conductive heat transfer. Nu=1 for pure conduction.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("convection", "dimensionless"),
)

# Prandtl Number
prandtl_number = EquationNode(
    id="prandtl_number",
    name="Prandtl Number",
    domain="thermodynamics",
    latex=r"Pr = \frac{\nu}{\alpha} = \frac{c_p\mu}{k}",
    sympy="Pr = nu/alpha = c_p*mu/k",
    variables=(("Pr", "Prandtl number", "dimensionless"), ("nu", "Kinematic viscosity", "m²/s"), ("alpha", "Thermal diffusivity", "m²/s")),
    description="Ratio of momentum to thermal diffusivity. Air: Pr~0.7, water: Pr~7, oils: Pr~100-10000.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("dimensionless", "convection"),
)

# Natural Convection Correlation
natural_convection = EquationNode(
    id="natural_convection",
    name="Natural Convection (Vertical Plate)",
    domain="thermodynamics",
    latex=r"Nu = C(Gr \cdot Pr)^n = C \cdot Ra^n, \quad Gr = \frac{g\beta\Delta T L^3}{\nu^2}",
    sympy="Nu = C*Ra**n",
    variables=(("Gr", "Grashof number", "dimensionless"), ("Ra", "Rayleigh number = Gr⋅Pr", "dimensionless"), ("beta", "Thermal expansion coefficient", "K⁻¹")),
    description="Buoyancy-driven convection. Laminar: n=1/4, turbulent: n=1/3.",
    derives_from=("nusselt_number",),
    status=NodeStatus.EMPIRICAL,
    tags=("natural_convection", "correlation"),
)

# Forced Convection Correlation
forced_convection = EquationNode(
    id="forced_convection_pipe",
    name="Forced Convection in Pipe (Dittus-Boelter)",
    domain="thermodynamics",
    latex=r"Nu = 0.023 Re^{0.8} Pr^n, \quad n = 0.4 \text{ (heating)}, 0.3 \text{ (cooling)}",
    sympy="Nu = 0.023*Re**0.8*Pr**n",
    variables=(("Re", "Reynolds number", "dimensionless")),
    description="Turbulent flow in smooth pipes. Valid for Re > 10000, 0.7 < Pr < 160.",
    conditions=("Turbulent", "Smooth pipe"),
    status=NodeStatus.EMPIRICAL,
    tags=("forced_convection", "correlation"),
)

# Blackbody Radiation
blackbody_power = EquationNode(
    id="blackbody_radiation_power",
    name="Blackbody Radiation Power",
    domain="thermodynamics",
    latex=r"\dot{Q} = \epsilon\sigma AT^4",
    sympy="Q_dot = epsilon*sigma*A*T**4",
    variables=(("Q_dot", "Radiated power", "W"), ("epsilon", "Emissivity", "dimensionless"), ("sigma", "Stefan-Boltzmann constant", "W/(m²⋅K⁴)"), ("A", "Surface area", "m²")),
    description="Thermal radiation emission. ε=1 for blackbody.",
    uses=("sigma",),
    status=NodeStatus.PROVEN,
    tags=("radiation", "thermal"),
)

# Radiative Heat Transfer
radiative_exchange = EquationNode(
    id="radiative_heat_exchange",
    name="Radiative Heat Exchange",
    domain="thermodynamics",
    latex=r"\dot{Q}_{1\to 2} = \epsilon\sigma A F_{1\to 2}(T_1^4 - T_2^4)",
    sympy="Q_dot = epsilon*sigma*A*F*(T1**4 - T2**4)",
    variables=(("F", "View factor", "dimensionless")),
    description="Net radiation between surfaces. F depends on geometry.",
    uses=("sigma",),
    status=NodeStatus.PROVEN,
    tags=("radiation", "exchange"),
)

# Overall Heat Transfer Coefficient
overall_htc = EquationNode(
    id="overall_heat_transfer",
    name="Overall Heat Transfer Coefficient",
    domain="thermodynamics",
    latex=r"\frac{1}{UA} = \frac{1}{h_1 A_1} + \frac{L}{kA} + \frac{1}{h_2 A_2}",
    sympy="1/(U*A) = 1/(h1*A1) + L/(k*A) + 1/(h2*A2)",
    variables=(("U", "Overall coefficient", "W/(m²⋅K)"), ("h", "Convection coefficient", "W/(m²⋅K)")),
    description="Total resistance from convection + conduction + convection.",
    derives_from=("thermal_resistance", "newton_cooling"),
    status=NodeStatus.PROVEN,
    tags=("heat_exchanger", "resistance"),
)

# Log Mean Temperature Difference
lmtd = EquationNode(
    id="log_mean_temp_difference",
    name="Log Mean Temperature Difference",
    domain="thermodynamics",
    latex=r"\Delta T_{lm} = \frac{\Delta T_1 - \Delta T_2}{\ln(\Delta T_1/\Delta T_2)}",
    sympy="delta_T_lm = (delta_T1 - delta_T2)/ln(delta_T1/delta_T2)",
    variables=(("delta_T_lm", "LMTD", "K"), ("delta_T1", "Temp difference at inlet", "K"), ("delta_T2", "Temp difference at outlet", "K")),
    description="Effective ΔT for heat exchanger. Q = UA × LMTD.",
    status=NodeStatus.PROVEN,
    tags=("heat_exchanger", "design"),
)

# Biot Number
biot_number = EquationNode(
    id="biot_number",
    name="Biot Number",
    domain="thermodynamics",
    latex=r"Bi = \frac{hL_c}{k}",
    sympy="Bi = h*L_c/k",
    variables=(("Bi", "Biot number", "dimensionless"), ("L_c", "Characteristic length V/A", "m")),
    description="Ratio of internal to external thermal resistance. Bi < 0.1: lumped capacitance valid.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("transient", "dimensionless"),
)

# Lumped Capacitance
lumped_capacitance = EquationNode(
    id="lumped_capacitance",
    name="Lumped Capacitance Model",
    domain="thermodynamics",
    latex=r"T(t) = T_\infty + (T_i - T_\infty)e^{-t/\tau}, \quad \tau = \frac{\rho c_p V}{hA}",
    sympy="T = T_inf + (T_i - T_inf)*exp(-t/tau)",
    variables=(("T", "Temperature", "K"), ("tau", "Time constant", "s"), ("T_i", "Initial temperature", "K")),
    description="Valid when Bi < 0.1. Uniform temperature in object.",
    conditions=("Bi < 0.1",),
    status=NodeStatus.PROVEN,
    tags=("transient", "lumped"),
)

NODES = [
    fourier_law, heat_equation, thermal_resistance, newton_cooling, nusselt_number,
    prandtl_number, natural_convection, forced_convection, blackbody_power, radiative_exchange,
    overall_htc, lmtd, biot_number, lumped_capacitance
]
