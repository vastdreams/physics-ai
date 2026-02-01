"""
PATH: physics/knowledge/equations/fluids/compressible.py
PURPOSE: Compressible flow and gas dynamics equations
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Mach Number
mach_number = EquationNode(
    id="mach_number",
    name="Mach Number",
    domain="fluid_dynamics",
    latex=r"Ma = \frac{v}{a} = \frac{v}{\sqrt{\gamma RT}}",
    sympy="Ma = v/a",
    variables=(("Ma", "Mach number", "dimensionless"), ("v", "Flow velocity", "m/s"), ("a", "Speed of sound", "m/s"), ("gamma", "Specific heat ratio", "dimensionless"), ("T", "Temperature", "K")),
    description="Ratio of flow speed to sound speed. Ma<1 subsonic, Ma>1 supersonic.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("compressible", "dimensionless"),
)

# Speed of Sound
sound_speed = EquationNode(
    id="speed_of_sound",
    name="Speed of Sound",
    domain="fluid_dynamics",
    latex=r"a = \sqrt{\gamma \frac{p}{\rho}} = \sqrt{\gamma R T}",
    sympy="a = sqrt(gamma*p/rho)",
    variables=(("a", "Speed of sound", "m/s"), ("gamma", "Specific heat ratio", "dimensionless"), ("p", "Pressure", "Pa"), ("rho", "Density", "kg/m³"), ("T", "Temperature", "K")),
    description="Speed of pressure waves in medium. ~343 m/s in air at 20°C.",
    status=NodeStatus.PROVEN,
    tags=("sound", "wave"),
)

# Isentropic Flow Relations
isentropic_temp = EquationNode(
    id="isentropic_temperature",
    name="Isentropic Temperature Ratio",
    domain="fluid_dynamics",
    latex=r"\frac{T_0}{T} = 1 + \frac{\gamma-1}{2}Ma^2",
    sympy="T0/T = 1 + (gamma-1)/2 * Ma**2",
    variables=(("T0", "Stagnation temperature", "K"), ("T", "Static temperature", "K"), ("Ma", "Mach number", "dimensionless")),
    description="Temperature ratio for isentropic (reversible adiabatic) flow.",
    conditions=("Isentropic flow",),
    status=NodeStatus.PROVEN,
    tags=("isentropic", "compressible"),
)

# Isentropic Pressure Ratio
isentropic_pressure = EquationNode(
    id="isentropic_pressure",
    name="Isentropic Pressure Ratio",
    domain="fluid_dynamics",
    latex=r"\frac{p_0}{p} = \left(1 + \frac{\gamma-1}{2}Ma^2\right)^{\frac{\gamma}{\gamma-1}}",
    sympy="p0/p = (1 + (gamma-1)/2 * Ma**2)**(gamma/(gamma-1))",
    variables=(("p0", "Stagnation pressure", "Pa"), ("p", "Static pressure", "Pa")),
    description="Pressure ratio for isentropic flow.",
    derives_from=("isentropic_temperature",),
    conditions=("Isentropic flow",),
    status=NodeStatus.PROVEN,
    tags=("isentropic", "compressible"),
)

# Isentropic Density Ratio
isentropic_density = EquationNode(
    id="isentropic_density",
    name="Isentropic Density Ratio",
    domain="fluid_dynamics",
    latex=r"\frac{\rho_0}{\rho} = \left(1 + \frac{\gamma-1}{2}Ma^2\right)^{\frac{1}{\gamma-1}}",
    sympy="rho0/rho = (1 + (gamma-1)/2 * Ma**2)**(1/(gamma-1))",
    variables=(("rho0", "Stagnation density", "kg/m³"), ("rho", "Static density", "kg/m³")),
    description="Density ratio for isentropic flow.",
    derives_from=("isentropic_temperature",),
    conditions=("Isentropic flow",),
    status=NodeStatus.PROVEN,
    tags=("isentropic", "compressible"),
)

# Normal Shock Relations
normal_shock_mach = EquationNode(
    id="normal_shock_mach",
    name="Normal Shock Mach Relation",
    domain="fluid_dynamics",
    latex=r"Ma_2^2 = \frac{Ma_1^2 + \frac{2}{\gamma-1}}{\frac{2\gamma}{\gamma-1}Ma_1^2 - 1}",
    sympy="Ma2**2 = (Ma1**2 + 2/(gamma-1)) / (2*gamma/(gamma-1)*Ma1**2 - 1)",
    variables=(("Ma1", "Upstream Mach", "dimensionless"), ("Ma2", "Downstream Mach", "dimensionless")),
    description="Mach number ratio across normal shock. Ma1>1, Ma2<1.",
    conditions=("Normal shock", "Perfect gas"),
    status=NodeStatus.PROVEN,
    tags=("shock", "compressible"),
)

# Shock Pressure Ratio
shock_pressure = EquationNode(
    id="shock_pressure_ratio",
    name="Normal Shock Pressure Ratio",
    domain="fluid_dynamics",
    latex=r"\frac{p_2}{p_1} = 1 + \frac{2\gamma}{\gamma+1}(Ma_1^2 - 1)",
    sympy="p2/p1 = 1 + 2*gamma/(gamma+1)*(Ma1**2 - 1)",
    variables=(("p1", "Upstream pressure", "Pa"), ("p2", "Downstream pressure", "Pa")),
    description="Pressure jump across normal shock.",
    conditions=("Normal shock",),
    status=NodeStatus.PROVEN,
    tags=("shock", "pressure"),
)

# Shock Temperature Ratio
shock_temperature = EquationNode(
    id="shock_temperature_ratio",
    name="Normal Shock Temperature Ratio",
    domain="fluid_dynamics",
    latex=r"\frac{T_2}{T_1} = \frac{p_2/p_1}{\rho_2/\rho_1}",
    sympy="T2/T1 = (p2/p1)/(rho2/rho1)",
    variables=(("T1", "Upstream temperature", "K"), ("T2", "Downstream temperature", "K")),
    description="Temperature jump across normal shock.",
    derives_from=("shock_pressure_ratio",),
    status=NodeStatus.PROVEN,
    tags=("shock", "temperature"),
)

# Oblique Shock Relation
oblique_shock = EquationNode(
    id="oblique_shock",
    name="Oblique Shock θ-β-M Relation",
    domain="fluid_dynamics",
    latex=r"\tan\theta = 2\cot\beta \frac{Ma_1^2\sin^2\beta - 1}{Ma_1^2(\gamma + \cos 2\beta) + 2}",
    sympy="tan(theta) = 2*cot(beta)*(Ma1**2*sin(beta)**2 - 1)/(Ma1**2*(gamma + cos(2*beta)) + 2)",
    variables=(("theta", "Deflection angle", "rad"), ("beta", "Shock angle", "rad"), ("Ma1", "Upstream Mach", "dimensionless")),
    description="Relates flow deflection to shock angle for oblique shocks.",
    derives_from=("normal_shock_mach",),
    status=NodeStatus.PROVEN,
    tags=("shock", "oblique"),
)

# Prandtl-Meyer Function
prandtl_meyer = EquationNode(
    id="prandtl_meyer",
    name="Prandtl-Meyer Function",
    domain="fluid_dynamics",
    latex=r"\nu(Ma) = \sqrt{\frac{\gamma+1}{\gamma-1}}\arctan\sqrt{\frac{\gamma-1}{\gamma+1}(Ma^2-1)} - \arctan\sqrt{Ma^2-1}",
    sympy="nu = sqrt((gamma+1)/(gamma-1))*atan(sqrt((gamma-1)/(gamma+1)*(Ma**2-1))) - atan(sqrt(Ma**2-1))",
    variables=(("nu", "Prandtl-Meyer angle", "rad"), ("Ma", "Mach number", "dimensionless")),
    description="Expansion fan angle for supersonic flow turning.",
    conditions=("Supersonic flow", "Isentropic expansion"),
    status=NodeStatus.PROVEN,
    tags=("expansion", "supersonic"),
)

# Converging-Diverging Nozzle
nozzle_area = EquationNode(
    id="nozzle_area_ratio",
    name="Isentropic Area-Mach Relation",
    domain="fluid_dynamics",
    latex=r"\frac{A}{A^*} = \frac{1}{Ma}\left[\frac{2}{\gamma+1}\left(1+\frac{\gamma-1}{2}Ma^2\right)\right]^{\frac{\gamma+1}{2(\gamma-1)}}",
    sympy="A/A_star = (1/Ma)*(2/(gamma+1)*(1+(gamma-1)/2*Ma**2))**((gamma+1)/(2*(gamma-1)))",
    variables=(("A", "Area", "m²"), ("A_star", "Throat area", "m²"), ("Ma", "Mach number", "dimensionless")),
    description="Area ratio for isentropic flow through nozzle. A* at Ma=1.",
    conditions=("Isentropic", "Quasi-1D"),
    status=NodeStatus.PROVEN,
    tags=("nozzle", "compressible"),
)

# Choked Flow
choked_flow = EquationNode(
    id="choked_flow",
    name="Choked Mass Flow Rate",
    domain="fluid_dynamics",
    latex=r"\dot{m} = A^* p_0 \sqrt{\frac{\gamma}{RT_0}}\left(\frac{2}{\gamma+1}\right)^{\frac{\gamma+1}{2(\gamma-1)}}",
    sympy="mdot = A_star*p0*sqrt(gamma/(R*T0))*(2/(gamma+1))**((gamma+1)/(2*(gamma-1)))",
    variables=(("mdot", "Mass flow rate", "kg/s"), ("A_star", "Throat area", "m²"), ("p0", "Stagnation pressure", "Pa"), ("T0", "Stagnation temperature", "K")),
    description="Maximum mass flow rate through a nozzle (choked at throat).",
    derives_from=("nozzle_area_ratio",),
    status=NodeStatus.PROVEN,
    tags=("choked", "nozzle"),
)

# Fanno Flow (Adiabatic Duct)
fanno_flow = EquationNode(
    id="fanno_flow",
    name="Fanno Flow Equation",
    domain="fluid_dynamics",
    latex=r"\frac{4fL^*}{D} = \frac{1-Ma^2}{\gamma Ma^2} + \frac{\gamma+1}{2\gamma}\ln\left[\frac{(\gamma+1)Ma^2}{2+(\gamma-1)Ma^2}\right]",
    sympy="4*f*L_star/D = (1-Ma**2)/(gamma*Ma**2) + ...",
    variables=(("f", "Friction factor", "dimensionless"), ("L_star", "Duct length to sonic", "m"), ("D", "Diameter", "m")),
    description="Adiabatic flow with friction in constant-area duct.",
    status=NodeStatus.PROVEN,
    tags=("duct", "friction"),
)

# Rayleigh Flow (Heat Addition)
rayleigh_flow = EquationNode(
    id="rayleigh_flow",
    name="Rayleigh Flow Equation",
    domain="fluid_dynamics",
    latex=r"\frac{T}{T^*} = \frac{(\gamma+1)^2 Ma^2}{(1+\gamma Ma^2)^2}",
    sympy="T/T_star = (gamma+1)**2*Ma**2/(1+gamma*Ma**2)**2",
    variables=(("T", "Temperature", "K"), ("T_star", "Sonic temperature", "K")),
    description="Frictionless flow with heat addition in constant-area duct.",
    status=NodeStatus.PROVEN,
    tags=("duct", "heat"),
)

NODES = [
    mach_number, sound_speed, isentropic_temp, isentropic_pressure, isentropic_density,
    normal_shock_mach, shock_pressure, shock_temperature, oblique_shock, prandtl_meyer,
    nozzle_area, choked_flow, fanno_flow, rayleigh_flow
]
