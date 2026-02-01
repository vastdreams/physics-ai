"""
PATH: physics/knowledge/equations/fluids/fundamental.py
PURPOSE: Fundamental fluid dynamics equations
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Continuity Equation
continuity = EquationNode(
    id="continuity_equation",
    name="Continuity Equation",
    domain="fluid_dynamics",
    latex=r"\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \vec{v}) = 0",
    sympy="drho/dt + div(rho*v) = 0",
    variables=(("rho", "Density", "kg/m³"), ("v", "Velocity", "m/s")),
    description="Mass conservation. For incompressible: ∇⋅v = 0.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("conservation", "mass"),
)

# Navier-Stokes Equation
navier_stokes = EquationNode(
    id="navier_stokes",
    name="Navier-Stokes Equation",
    domain="fluid_dynamics",
    latex=r"\rho\left(\frac{\partial \vec{v}}{\partial t} + \vec{v} \cdot \nabla\vec{v}\right) = -\nabla p + \mu\nabla^2\vec{v} + \vec{f}",
    sympy="rho*(dv/dt + v*grad(v)) = -grad(p) + mu*laplacian(v) + f",
    variables=(("rho", "Density", "kg/m³"), ("v", "Velocity", "m/s"), ("p", "Pressure", "Pa"), ("mu", "Dynamic viscosity", "Pa⋅s"), ("f", "Body force density", "N/m³")),
    description="Momentum conservation for viscous fluid. One of the millennium prize problems.",
    derives_from=("newton_second_law",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("momentum", "viscous"),
)

# Euler Equation (Inviscid)
euler_fluid = EquationNode(
    id="euler_fluid_equation",
    name="Euler Equation (Fluid)",
    domain="fluid_dynamics",
    latex=r"\rho\left(\frac{\partial \vec{v}}{\partial t} + \vec{v} \cdot \nabla\vec{v}\right) = -\nabla p + \vec{f}",
    sympy="rho*(dv/dt + v*grad(v)) = -grad(p) + f",
    variables=(("rho", "Density", "kg/m³"), ("v", "Velocity", "m/s"), ("p", "Pressure", "Pa")),
    description="Inviscid fluid momentum equation. Navier-Stokes with μ=0.",
    derives_from=("navier_stokes",),
    conditions=("Inviscid flow (μ=0)",),
    status=NodeStatus.PROVEN,
    tags=("momentum", "inviscid"),
)

# Bernoulli Equation
bernoulli = EquationNode(
    id="bernoulli_equation",
    name="Bernoulli's Equation",
    domain="fluid_dynamics",
    latex=r"p + \frac{1}{2}\rho v^2 + \rho gh = \text{const}",
    sympy="p + (1/2)*rho*v**2 + rho*g*h = const",
    variables=(("p", "Pressure", "Pa"), ("rho", "Density", "kg/m³"), ("v", "Velocity", "m/s"), ("h", "Height", "m")),
    description="Energy conservation along streamline. Valid for steady, inviscid, incompressible flow.",
    derives_from=("euler_fluid_equation",),
    conditions=("Steady flow", "Inviscid", "Incompressible", "Along streamline"),
    status=NodeStatus.PROVEN,
    tags=("energy", "streamline"),
)

# Reynolds Number
reynolds_number = EquationNode(
    id="reynolds_number",
    name="Reynolds Number",
    domain="fluid_dynamics",
    latex=r"Re = \frac{\rho v L}{\mu} = \frac{vL}{\nu}",
    sympy="Re = rho*v*L/mu",
    variables=(("Re", "Reynolds number", "dimensionless"), ("rho", "Density", "kg/m³"), ("v", "Velocity", "m/s"), ("L", "Length scale", "m"), ("mu", "Dynamic viscosity", "Pa⋅s"), ("nu", "Kinematic viscosity", "m²/s")),
    description="Ratio of inertial to viscous forces. Determines flow regime: Re<2300 laminar, Re>4000 turbulent.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("dimensionless", "turbulence"),
)

# Stokes Flow (Creeping Flow)
stokes_flow = EquationNode(
    id="stokes_flow",
    name="Stokes Flow Equation",
    domain="fluid_dynamics",
    latex=r"\nabla p = \mu \nabla^2 \vec{v}",
    sympy="grad(p) = mu*laplacian(v)",
    variables=(("p", "Pressure", "Pa"), ("mu", "Viscosity", "Pa⋅s"), ("v", "Velocity", "m/s")),
    description="Low Reynolds number flow. Viscous forces dominate inertia.",
    derives_from=("navier_stokes",),
    conditions=("Re << 1",),
    status=NodeStatus.PROVEN,
    tags=("viscous", "creeping"),
)

# Stokes Drag
stokes_drag = EquationNode(
    id="stokes_drag",
    name="Stokes Drag Law",
    domain="fluid_dynamics",
    latex=r"F_D = 6\pi\mu Rv",
    sympy="F_D = 6*pi*mu*R*v",
    variables=(("F_D", "Drag force", "N"), ("mu", "Viscosity", "Pa⋅s"), ("R", "Sphere radius", "m"), ("v", "Velocity", "m/s")),
    description="Drag on sphere in creeping flow. Valid for Re << 1.",
    derives_from=("stokes_flow",),
    conditions=("Sphere", "Re << 1"),
    status=NodeStatus.PROVEN,
    tags=("drag", "sphere"),
)

# Drag Force General
drag_force = EquationNode(
    id="drag_force",
    name="Drag Force (General)",
    domain="fluid_dynamics",
    latex=r"F_D = \frac{1}{2}C_D \rho A v^2",
    sympy="F_D = (1/2)*C_D*rho*A*v**2",
    variables=(("F_D", "Drag force", "N"), ("C_D", "Drag coefficient", "dimensionless"), ("rho", "Fluid density", "kg/m³"), ("A", "Cross-sectional area", "m²"), ("v", "Velocity", "m/s")),
    description="General drag force formula. C_D depends on Re and shape.",
    status=NodeStatus.EMPIRICAL,
    tags=("drag", "aerodynamics"),
)

# Lift Force
lift_force = EquationNode(
    id="lift_force",
    name="Lift Force",
    domain="fluid_dynamics",
    latex=r"F_L = \frac{1}{2}C_L \rho A v^2",
    sympy="F_L = (1/2)*C_L*rho*A*v**2",
    variables=(("F_L", "Lift force", "N"), ("C_L", "Lift coefficient", "dimensionless"), ("rho", "Fluid density", "kg/m³"), ("A", "Wing area", "m²"), ("v", "Velocity", "m/s")),
    description="Lift force on airfoil. C_L depends on angle of attack.",
    status=NodeStatus.EMPIRICAL,
    tags=("lift", "aerodynamics"),
)

# Poiseuille Flow
poiseuille = EquationNode(
    id="poiseuille_flow",
    name="Hagen-Poiseuille Equation",
    domain="fluid_dynamics",
    latex=r"Q = \frac{\pi R^4 \Delta p}{8\mu L}",
    sympy="Q = pi*R**4*dp/(8*mu*L)",
    variables=(("Q", "Volume flow rate", "m³/s"), ("R", "Pipe radius", "m"), ("dp", "Pressure drop", "Pa"), ("mu", "Viscosity", "Pa⋅s"), ("L", "Pipe length", "m")),
    description="Laminar flow in circular pipe. Flow rate ∝ R⁴.",
    derives_from=("navier_stokes",),
    conditions=("Laminar", "Circular pipe", "Steady", "Fully developed"),
    status=NodeStatus.PROVEN,
    tags=("pipe_flow", "laminar"),
)

# Vorticity Equation
vorticity_eq = EquationNode(
    id="vorticity_equation",
    name="Vorticity Equation",
    domain="fluid_dynamics",
    latex=r"\frac{D\vec{\omega}}{Dt} = (\vec{\omega} \cdot \nabla)\vec{v} + \nu\nabla^2\vec{\omega}",
    sympy="Domega/Dt = (omega . grad)v + nu*laplacian(omega)",
    variables=(("omega", "Vorticity", "s⁻¹"), ("v", "Velocity", "m/s"), ("nu", "Kinematic viscosity", "m²/s")),
    description="Evolution of vorticity. First term: vortex stretching. Second: diffusion.",
    derives_from=("navier_stokes",),
    status=NodeStatus.PROVEN,
    tags=("vorticity", "rotation"),
)

# Circulation
circulation = EquationNode(
    id="circulation",
    name="Circulation",
    domain="fluid_dynamics",
    latex=r"\Gamma = \oint_C \vec{v} \cdot d\vec{l} = \int_S \vec{\omega} \cdot d\vec{A}",
    sympy="Gamma = integral(v . dl, C)",
    variables=(("Gamma", "Circulation", "m²/s"), ("v", "Velocity", "m/s"), ("omega", "Vorticity", "s⁻¹")),
    description="Line integral of velocity. Equals flux of vorticity through surface (Stokes theorem).",
    status=NodeStatus.FUNDAMENTAL,
    tags=("circulation", "vorticity"),
)

# Kutta-Joukowski Theorem
kutta_joukowski = EquationNode(
    id="kutta_joukowski",
    name="Kutta-Joukowski Theorem",
    domain="fluid_dynamics",
    latex=r"L' = \rho v_\infty \Gamma",
    sympy="L_prime = rho*v_inf*Gamma",
    variables=(("L_prime", "Lift per unit span", "N/m"), ("rho", "Density", "kg/m³"), ("v_inf", "Freestream velocity", "m/s"), ("Gamma", "Circulation", "m²/s")),
    description="Lift on 2D airfoil from circulation.",
    derives_from=("circulation",),
    status=NodeStatus.PROVEN,
    tags=("lift", "airfoil"),
)

# Hydrostatic Pressure
hydrostatic = EquationNode(
    id="hydrostatic_pressure",
    name="Hydrostatic Pressure",
    domain="fluid_dynamics",
    latex=r"p = p_0 + \rho g h",
    sympy="p = p0 + rho*g*h",
    variables=(("p", "Pressure at depth", "Pa"), ("p0", "Surface pressure", "Pa"), ("rho", "Density", "kg/m³"), ("h", "Depth", "m")),
    description="Pressure increases linearly with depth in incompressible fluid.",
    status=NodeStatus.PROVEN,
    tags=("hydrostatics", "pressure"),
)

# Archimedes Principle
archimedes = EquationNode(
    id="archimedes_principle",
    name="Archimedes' Principle",
    domain="fluid_dynamics",
    latex=r"F_b = \rho_f g V_{disp}",
    sympy="F_b = rho_f*g*V_disp",
    variables=(("F_b", "Buoyant force", "N"), ("rho_f", "Fluid density", "kg/m³"), ("V_disp", "Displaced volume", "m³")),
    description="Buoyant force equals weight of displaced fluid.",
    derives_from=("hydrostatic_pressure",),
    status=NodeStatus.PROVEN,
    tags=("buoyancy", "archimedes"),
)

# Surface Tension Pressure
surface_tension_pressure = EquationNode(
    id="young_laplace",
    name="Young-Laplace Equation",
    domain="fluid_dynamics",
    latex=r"\Delta p = \gamma\left(\frac{1}{R_1} + \frac{1}{R_2}\right)",
    sympy="dp = gamma*(1/R1 + 1/R2)",
    variables=(("dp", "Pressure difference", "Pa"), ("gamma", "Surface tension", "N/m"), ("R1", "Principal radius 1", "m"), ("R2", "Principal radius 2", "m")),
    description="Pressure jump across curved interface due to surface tension.",
    status=NodeStatus.PROVEN,
    tags=("surface_tension", "interface"),
)

# Capillary Rise
capillary_rise = EquationNode(
    id="capillary_rise",
    name="Capillary Rise",
    domain="fluid_dynamics",
    latex=r"h = \frac{2\gamma\cos\theta}{\rho g r}",
    sympy="h = 2*gamma*cos(theta)/(rho*g*r)",
    variables=(("h", "Rise height", "m"), ("gamma", "Surface tension", "N/m"), ("theta", "Contact angle", "rad"), ("r", "Tube radius", "m")),
    description="Height liquid rises in capillary tube.",
    derives_from=("young_laplace",),
    status=NodeStatus.PROVEN,
    tags=("capillary", "surface_tension"),
)

# Torricelli's Law
torricelli = EquationNode(
    id="torricelli_law",
    name="Torricelli's Law",
    domain="fluid_dynamics",
    latex=r"v = \sqrt{2gh}",
    sympy="v = sqrt(2*g*h)",
    variables=(("v", "Exit velocity", "m/s"), ("g", "Gravity", "m/s²"), ("h", "Height above opening", "m")),
    description="Speed of fluid exiting hole in tank. From Bernoulli.",
    derives_from=("bernoulli_equation",),
    status=NodeStatus.PROVEN,
    tags=("flow", "tank"),
)

# Darcy's Law
darcy = EquationNode(
    id="darcy_law",
    name="Darcy's Law",
    domain="fluid_dynamics",
    latex=r"Q = -\frac{kA}{\mu}\frac{dp}{dx}",
    sympy="Q = -k*A*dp/dx / mu",
    variables=(("Q", "Flow rate", "m³/s"), ("k", "Permeability", "m²"), ("A", "Cross-sectional area", "m²"), ("mu", "Viscosity", "Pa⋅s"), ("dp/dx", "Pressure gradient", "Pa/m")),
    description="Flow through porous medium. Foundation of groundwater hydrology.",
    status=NodeStatus.EMPIRICAL,
    tags=("porous", "permeability"),
)

NODES = [
    continuity, navier_stokes, euler_fluid, bernoulli, reynolds_number,
    stokes_flow, stokes_drag, drag_force, lift_force, poiseuille,
    vorticity_eq, circulation, kutta_joukowski, hydrostatic, archimedes,
    surface_tension_pressure, capillary_rise, torricelli, darcy
]
