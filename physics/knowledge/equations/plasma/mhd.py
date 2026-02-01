"""
PATH: physics/knowledge/equations/plasma/mhd.py
PURPOSE: Magnetohydrodynamics (MHD) equations
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# MHD Momentum Equation
mhd_momentum = EquationNode(
    id="mhd_momentum",
    name="MHD Momentum Equation",
    domain="plasma_physics",
    latex=r"\rho\frac{d\vec{v}}{dt} = -\nabla p + \vec{J} \times \vec{B}",
    sympy="rho*dv/dt = -grad(p) + J cross B",
    variables=(("rho", "Mass density", "kg/m³"), ("v", "Fluid velocity", "m/s"), ("p", "Pressure", "Pa"), ("J", "Current density", "A/m²"), ("B", "Magnetic field", "T")),
    description="Fluid momentum with magnetic force. J×B is the Lorentz force.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("mhd", "momentum"),
)

# MHD Ohm's Law
mhd_ohm = EquationNode(
    id="mhd_ohm_law",
    name="MHD Ohm's Law (Ideal)",
    domain="plasma_physics",
    latex=r"\vec{E} + \vec{v} \times \vec{B} = 0 \quad \text{or} \quad \vec{E} = -\vec{v} \times \vec{B}",
    sympy="E + v cross B = 0",
    variables=(("E", "Electric field", "V/m"), ("v", "Velocity", "m/s"), ("B", "Magnetic field", "T")),
    description="Ideal MHD: infinite conductivity. Field frozen into plasma.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("mhd", "ideal"),
)

# Magnetic Pressure
magnetic_pressure = EquationNode(
    id="magnetic_pressure",
    name="Magnetic Pressure",
    domain="plasma_physics",
    latex=r"p_B = \frac{B^2}{2\mu_0}",
    sympy="p_B = B**2/(2*mu_0)",
    variables=(("p_B", "Magnetic pressure", "Pa"), ("B", "Magnetic field", "T")),
    description="Pressure exerted by magnetic field. 1 T → 400 kPa.",
    uses=("mu_0",),
    status=NodeStatus.PROVEN,
    tags=("magnetic", "pressure"),
)

# Plasma Beta
plasma_beta = EquationNode(
    id="plasma_beta",
    name="Plasma Beta",
    domain="plasma_physics",
    latex=r"\beta = \frac{p}{B^2/2\mu_0} = \frac{2\mu_0 n k_B T}{B^2}",
    sympy="beta = 2*mu_0*p/B**2",
    variables=(("beta", "Plasma beta", "dimensionless"), ("p", "Plasma pressure", "Pa"), ("B", "Magnetic field", "T")),
    description="Ratio of thermal to magnetic pressure. β << 1 in tokamaks, β ~ 1 in Sun.",
    uses=("mu_0", "k_B"),
    status=NodeStatus.FUNDAMENTAL,
    tags=("mhd", "confinement"),
)

# Alfvén Speed
alfven_speed = EquationNode(
    id="alfven_speed",
    name="Alfvén Speed",
    domain="plasma_physics",
    latex=r"v_A = \frac{B}{\sqrt{\mu_0 \rho}}",
    sympy="v_A = B/sqrt(mu_0*rho)",
    variables=(("v_A", "Alfvén speed", "m/s"), ("B", "Magnetic field", "T"), ("rho", "Mass density", "kg/m³")),
    description="Speed of magnetic tension waves. ~1000 km/s in solar corona.",
    uses=("mu_0",),
    status=NodeStatus.PROVEN,
    tags=("waves", "mhd"),
)

# Magnetic Reynolds Number
magnetic_reynolds = EquationNode(
    id="magnetic_reynolds",
    name="Magnetic Reynolds Number",
    domain="plasma_physics",
    latex=r"R_m = \frac{vL}{\eta} = \mu_0 \sigma vL",
    sympy="R_m = mu_0*sigma*v*L",
    variables=(("R_m", "Magnetic Reynolds number", "dimensionless"), ("v", "Velocity", "m/s"), ("L", "Length scale", "m"), ("eta", "Magnetic diffusivity", "m²/s"), ("sigma", "Conductivity", "S/m")),
    description="R_m >> 1: frozen-in field. R_m << 1: diffusive.",
    uses=("mu_0",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("mhd", "dimensionless"),
)

# Magnetic Induction Equation
induction_equation = EquationNode(
    id="magnetic_induction",
    name="Magnetic Induction Equation",
    domain="plasma_physics",
    latex=r"\frac{\partial \vec{B}}{\partial t} = \nabla \times (\vec{v} \times \vec{B}) + \eta \nabla^2 \vec{B}",
    sympy="dB/dt = curl(v cross B) + eta*laplacian(B)",
    variables=(("B", "Magnetic field", "T"), ("v", "Velocity", "m/s"), ("eta", "Magnetic diffusivity", "m²/s")),
    description="B-field evolution. First term: convection. Second: diffusion.",
    derives_from=("mhd_ohm_law",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("mhd", "induction"),
)

# MHD Equilibrium (Force Balance)
mhd_equilibrium = EquationNode(
    id="mhd_equilibrium",
    name="MHD Force Balance",
    domain="plasma_physics",
    latex=r"\nabla p = \vec{J} \times \vec{B}",
    sympy="grad(p) = J cross B",
    variables=(("p", "Pressure", "Pa"), ("J", "Current density", "A/m²"), ("B", "Magnetic field", "T")),
    description="Static equilibrium: pressure gradient balanced by magnetic force.",
    derives_from=("mhd_momentum",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("mhd", "equilibrium"),
)

# Bennett Pinch
bennett_pinch = EquationNode(
    id="bennett_pinch",
    name="Bennett Pinch Relation",
    domain="plasma_physics",
    latex=r"I^2 = \frac{8\pi N k_B (T_e + T_i)}{\mu_0}",
    sympy="I**2 = 8*pi*N*k_B*(T_e + T_i)/mu_0",
    variables=(("I", "Current", "A"), ("N", "Linear density", "m⁻¹"), ("T_e", "Electron temperature", "K"), ("T_i", "Ion temperature", "K")),
    description="Current required to confine Z-pinch plasma.",
    uses=("k_B", "mu_0"),
    status=NodeStatus.PROVEN,
    tags=("pinch", "confinement"),
)

# Grad-Shafranov Equation
grad_shafranov = EquationNode(
    id="grad_shafranov",
    name="Grad-Shafranov Equation",
    domain="plasma_physics",
    latex=r"R\frac{\partial}{\partial R}\frac{1}{R}\frac{\partial \psi}{\partial R} + \frac{\partial^2 \psi}{\partial Z^2} = -\mu_0 R^2 \frac{dp}{d\psi} - F\frac{dF}{d\psi}",
    sympy="...",
    variables=(("psi", "Poloidal flux", "Wb"), ("p", "Pressure", "Pa"), ("F", "Toroidal field function", "T⋅m")),
    description="2D MHD equilibrium for axisymmetric plasma (tokamak).",
    derives_from=("mhd_equilibrium",),
    uses=("mu_0",),
    status=NodeStatus.PROVEN,
    tags=("tokamak", "equilibrium"),
)

# Kruskal-Shafranov Limit
kruskal_shafranov = EquationNode(
    id="kruskal_shafranov",
    name="Kruskal-Shafranov Limit",
    domain="plasma_physics",
    latex=r"q(a) = \frac{aB_\phi}{RB_\theta} > 1",
    sympy="q_a = a*B_phi/(R*B_theta) > 1",
    variables=(("q", "Safety factor", "dimensionless"), ("a", "Minor radius", "m"), ("R", "Major radius", "m"), ("B_phi", "Toroidal field", "T"), ("B_theta", "Poloidal field", "T")),
    description="Stability limit for tokamak. q > 1 required at edge.",
    status=NodeStatus.PROVEN,
    tags=("tokamak", "stability"),
)

# Reconnection Rate (Sweet-Parker)
sweet_parker = EquationNode(
    id="sweet_parker",
    name="Sweet-Parker Reconnection Rate",
    domain="plasma_physics",
    latex=r"v_{rec} = \frac{v_A}{\sqrt{S}}, \quad S = \frac{\mu_0 Lv_A}{\eta}",
    sympy="v_rec = v_A/sqrt(S)",
    variables=(("v_rec", "Reconnection velocity", "m/s"), ("v_A", "Alfvén speed", "m/s"), ("S", "Lundquist number", "dimensionless")),
    description="Reconnection rate in resistive MHD. Too slow for solar flares.",
    derives_from=("alfven_speed", "magnetic_reynolds"),
    uses=("mu_0",),
    status=NodeStatus.PROVEN,
    tags=("reconnection", "mhd"),
)

NODES = [
    mhd_momentum, mhd_ohm, magnetic_pressure, plasma_beta, alfven_speed,
    magnetic_reynolds, induction_equation, mhd_equilibrium, bennett_pinch,
    grad_shafranov, kruskal_shafranov, sweet_parker
]
