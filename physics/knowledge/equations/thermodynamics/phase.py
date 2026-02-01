"""
PATH: physics/knowledge/equations/thermodynamics/phase.py
PURPOSE: Phase transitions and critical phenomena equations
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Clausius-Clapeyron Equation
clausius_clapeyron = EquationNode(
    id="clausius_clapeyron",
    name="Clausius-Clapeyron Equation",
    domain="thermodynamics",
    latex=r"\frac{dP}{dT} = \frac{L}{T\Delta V} \approx \frac{LP}{RT^2} \text{ (ideal gas)}",
    sympy="dP/dT = L/(T*delta_V)",
    variables=(("dP/dT", "Slope of phase boundary", "Pa/K"), ("L", "Latent heat", "J/mol"), ("delta_V", "Volume change", "m³/mol")),
    description="Slope of coexistence curve in P-T diagram.",
    uses=("R",),
    status=NodeStatus.PROVEN,
    tags=("phase_transition", "coexistence"),
)

# Latent Heat
latent_heat = EquationNode(
    id="latent_heat",
    name="Latent Heat",
    domain="thermodynamics",
    latex=r"Q = mL = nL_m",
    sympy="Q = m*L",
    variables=(("Q", "Heat absorbed/released", "J"), ("m", "Mass", "kg"), ("L", "Specific latent heat", "J/kg"), ("L_m", "Molar latent heat", "J/mol")),
    description="Heat for phase change at constant T. Water: L_f = 334 kJ/kg, L_v = 2260 kJ/kg.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("phase_transition", "heat"),
)

# Triple Point
triple_point = EquationNode(
    id="triple_point",
    name="Triple Point",
    domain="thermodynamics",
    latex=r"f = c - p + 2 = 0 \text{ at triple point (c=1, p=3)}",
    sympy="f = c - p + 2",
    variables=(("f", "Degrees of freedom", "dimensionless"), ("c", "Components", "dimensionless"), ("p", "Phases", "dimensionless")),
    description="Where solid, liquid, gas coexist. Water: 273.16 K, 611.73 Pa.",
    derives_from=("gibbs_phase_rule",),
    status=NodeStatus.PROVEN,
    tags=("phase", "triple_point"),
)

# Gibbs Phase Rule
gibbs_phase_rule = EquationNode(
    id="gibbs_phase_rule",
    name="Gibbs Phase Rule",
    domain="thermodynamics",
    latex=r"F = C - P + 2",
    sympy="F = C - P + 2",
    variables=(("F", "Degrees of freedom", "dimensionless"), ("C", "Number of components", "dimensionless"), ("P", "Number of phases", "dimensionless")),
    description="Determines variance of system. At coexistence: F = C - P + 2.",
    status=NodeStatus.PROVEN,
    tags=("phase", "equilibrium"),
)

# Van der Waals Equation
van_der_waals = EquationNode(
    id="van_der_waals",
    name="Van der Waals Equation",
    domain="thermodynamics",
    latex=r"\left(P + \frac{a}{V_m^2}\right)(V_m - b) = RT",
    sympy="(P + a/V_m**2)*(V_m - b) = R*T",
    variables=(("P", "Pressure", "Pa"), ("V_m", "Molar volume", "m³/mol"), ("a", "Attraction parameter", "Pa⋅m⁶/mol²"), ("b", "Volume parameter", "m³/mol")),
    description="Real gas equation. a accounts for attraction, b for finite volume.",
    uses=("R",),
    status=NodeStatus.APPROXIMATE,
    tags=("real_gas", "equation_of_state"),
)

# Critical Point (Van der Waals)
critical_point = EquationNode(
    id="critical_point_vdw",
    name="Critical Point (Van der Waals)",
    domain="thermodynamics",
    latex=r"T_c = \frac{8a}{27Rb}, \quad P_c = \frac{a}{27b^2}, \quad V_c = 3b",
    sympy="T_c = 8*a/(27*R*b)",
    variables=(("T_c", "Critical temperature", "K"), ("P_c", "Critical pressure", "Pa"), ("V_c", "Critical molar volume", "m³/mol")),
    description="Critical point from Van der Waals. P_cV_c/(RT_c) = 3/8.",
    derives_from=("van_der_waals",),
    uses=("R",),
    status=NodeStatus.PROVEN,
    tags=("critical", "van_der_waals"),
)

# Reduced Variables
reduced_variables = EquationNode(
    id="reduced_variables",
    name="Reduced Variables (Law of Corresponding States)",
    domain="thermodynamics",
    latex=r"T_r = \frac{T}{T_c}, \quad P_r = \frac{P}{P_c}, \quad V_r = \frac{V_m}{V_c}",
    sympy="T_r = T/T_c",
    variables=(("T_r", "Reduced temperature", "dimensionless"), ("P_r", "Reduced pressure", "dimensionless"), ("V_r", "Reduced volume", "dimensionless")),
    description="Law of corresponding states: all fluids behave similarly in reduced variables.",
    status=NodeStatus.APPROXIMATE,
    tags=("critical", "scaling"),
)

# Order Parameter
order_parameter = EquationNode(
    id="order_parameter",
    name="Order Parameter",
    domain="thermodynamics",
    latex=r"\phi \propto |T - T_c|^\beta \text{ below } T_c",
    sympy="phi ~ |T - T_c|**beta",
    variables=(("phi", "Order parameter", "varies"), ("beta", "Critical exponent ~0.33", "dimensionless"), ("T_c", "Critical temperature", "K")),
    description="Measure of ordered phase. Zero above T_c, nonzero below.",
    status=NodeStatus.PROVEN,
    tags=("critical", "scaling"),
)

# Susceptibility Divergence
susceptibility_divergence = EquationNode(
    id="susceptibility_divergence",
    name="Susceptibility Divergence",
    domain="thermodynamics",
    latex=r"\chi \propto |T - T_c|^{-\gamma}",
    sympy="chi ~ |T - T_c|**(-gamma)",
    variables=(("chi", "Susceptibility", "varies"), ("gamma", "Critical exponent ~1.24", "dimensionless")),
    description="Response function diverges at critical point.",
    status=NodeStatus.PROVEN,
    tags=("critical", "scaling"),
)

# Heat Capacity Divergence
heat_capacity_critical = EquationNode(
    id="heat_capacity_critical",
    name="Heat Capacity at Critical Point",
    domain="thermodynamics",
    latex=r"C \propto |T - T_c|^{-\alpha}",
    sympy="C ~ |T - T_c|**(-alpha)",
    variables=(("C", "Heat capacity", "J/K"), ("alpha", "Critical exponent ~0.11", "dimensionless")),
    description="Heat capacity diverges (weakly) at critical point.",
    status=NodeStatus.PROVEN,
    tags=("critical", "scaling"),
)

# Correlation Length
correlation_length = EquationNode(
    id="correlation_length",
    name="Correlation Length",
    domain="thermodynamics",
    latex=r"\xi \propto |T - T_c|^{-\nu}",
    sympy="xi ~ |T - T_c|**(-nu)",
    variables=(("xi", "Correlation length", "m"), ("nu", "Critical exponent ~0.63", "dimensionless")),
    description="Length scale of fluctuations. Diverges at T_c.",
    status=NodeStatus.PROVEN,
    tags=("critical", "scaling"),
)

# Mean Field Theory
mean_field = EquationNode(
    id="mean_field_exponents",
    name="Mean Field Critical Exponents",
    domain="thermodynamics",
    latex=r"\alpha = 0, \; \beta = 1/2, \; \gamma = 1, \; \delta = 3, \; \nu = 1/2",
    sympy="beta_MF = 1/2",
    variables=(),
    description="Mean field (Landau) exponents. Valid above upper critical dimension (d=4 for Ising).",
    status=NodeStatus.PROVEN,
    tags=("critical", "mean_field"),
)

NODES = [
    clausius_clapeyron, latent_heat, triple_point, gibbs_phase_rule, van_der_waals,
    critical_point, reduced_variables, order_parameter, susceptibility_divergence,
    heat_capacity_critical, correlation_length, mean_field
]
