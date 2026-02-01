"""
PATH: physics/knowledge/equations/relativity/special.py
PURPOSE: Special relativity equations
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Lorentz Factor
lorentz_factor = EquationNode(
    id="lorentz_factor",
    name="Lorentz Factor",
    domain="special_relativity",
    latex=r"\gamma = \frac{1}{\sqrt{1-v^2/c^2}} = \frac{1}{\sqrt{1-\beta^2}}",
    sympy="gamma = 1/sqrt(1 - v**2/c**2)",
    variables=(("gamma", "Lorentz factor", "dimensionless"), ("v", "Velocity", "m/s"), ("beta", "v/c", "dimensionless")),
    description="Relativistic correction factor. γ = 1 at rest, → ∞ as v → c.",
    uses=("c",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("relativity", "lorentz"),
)

# Time Dilation
time_dilation = EquationNode(
    id="time_dilation",
    name="Time Dilation",
    domain="special_relativity",
    latex=r"\Delta t = \gamma\Delta\tau = \frac{\Delta\tau}{\sqrt{1-v^2/c^2}}",
    sympy="delta_t = gamma*delta_tau",
    variables=(("delta_t", "Coordinate time interval", "s"), ("delta_tau", "Proper time interval", "s")),
    description="Moving clocks run slow. Proper time τ is shortest.",
    derives_from=("lorentz_factor",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("time", "dilation"),
)

# Length Contraction
length_contraction = EquationNode(
    id="length_contraction",
    name="Length Contraction",
    domain="special_relativity",
    latex=r"L = \frac{L_0}{\gamma} = L_0\sqrt{1-v^2/c^2}",
    sympy="L = L_0/gamma",
    variables=(("L", "Contracted length", "m"), ("L_0", "Proper length", "m")),
    description="Moving objects are shortened in direction of motion.",
    derives_from=("lorentz_factor",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("length", "contraction"),
)

# Lorentz Transformation
lorentz_transform = EquationNode(
    id="lorentz_transformation",
    name="Lorentz Transformation",
    domain="special_relativity",
    latex=r"x' = \gamma(x - vt), \quad t' = \gamma(t - vx/c^2)",
    sympy="x_prime = gamma*(x - v*t), t_prime = gamma*(t - v*x/c**2)",
    variables=(("x_prime", "Transformed position", "m"), ("t_prime", "Transformed time", "s"), ("v", "Relative velocity", "m/s")),
    description="Coordinates in moving frame. Preserves spacetime interval.",
    derives_from=("lorentz_factor",),
    uses=("c",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("transformation", "lorentz"),
)

# Velocity Addition
velocity_addition = EquationNode(
    id="velocity_addition",
    name="Relativistic Velocity Addition",
    domain="special_relativity",
    latex=r"u' = \frac{u - v}{1 - uv/c^2}",
    sympy="u_prime = (u - v)/(1 - u*v/c**2)",
    variables=(("u_prime", "Velocity in moving frame", "m/s"), ("u", "Velocity in lab frame", "m/s"), ("v", "Frame velocity", "m/s")),
    description="Velocities don't simply add. No combination exceeds c.",
    derives_from=("lorentz_transformation",),
    uses=("c",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("velocity", "addition"),
)

# Mass-Energy Equivalence
mass_energy = EquationNode(
    id="mass_energy_equivalence",
    name="Mass-Energy Equivalence",
    domain="special_relativity",
    latex=r"E = mc^2",
    sympy="E = m*c**2",
    variables=(("E", "Rest energy", "J"), ("m", "Rest mass", "kg")),
    description="Most famous equation. m = 1 kg contains 9×10¹⁶ J.",
    uses=("c",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("energy", "mass"),
)

# Relativistic Energy
relativistic_energy = EquationNode(
    id="relativistic_energy",
    name="Relativistic Total Energy",
    domain="special_relativity",
    latex=r"E = \gamma mc^2 = \frac{mc^2}{\sqrt{1-v^2/c^2}}",
    sympy="E = gamma*m*c**2",
    variables=(("E", "Total energy", "J"), ("m", "Rest mass", "kg")),
    description="Total energy = rest energy + kinetic energy.",
    derives_from=("lorentz_factor", "mass_energy_equivalence"),
    uses=("c",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("energy", "relativistic"),
)

# Relativistic Momentum
relativistic_momentum = EquationNode(
    id="relativistic_momentum",
    name="Relativistic Momentum",
    domain="special_relativity",
    latex=r"p = \gamma mv = \frac{mv}{\sqrt{1-v^2/c^2}}",
    sympy="p = gamma*m*v",
    variables=(("p", "Momentum", "kg⋅m/s"), ("m", "Rest mass", "kg"), ("v", "Velocity", "m/s")),
    description="Momentum → ∞ as v → c. Required infinite energy to accelerate to c.",
    derives_from=("lorentz_factor",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("momentum", "relativistic"),
)

# Energy-Momentum Relation
energy_momentum_relation = EquationNode(
    id="energy_momentum_relation",
    name="Energy-Momentum Relation",
    domain="special_relativity",
    latex=r"E^2 = (pc)^2 + (mc^2)^2",
    sympy="E**2 = (p*c)**2 + (m*c**2)**2",
    variables=(("E", "Total energy", "J"), ("p", "Momentum", "kg⋅m/s"), ("m", "Rest mass", "kg")),
    description="Invariant relation. For m=0 (photon): E = pc.",
    derives_from=("relativistic_energy", "relativistic_momentum"),
    uses=("c",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("energy", "momentum"),
)

# Relativistic Kinetic Energy
relativistic_ke = EquationNode(
    id="relativistic_kinetic_energy",
    name="Relativistic Kinetic Energy",
    domain="special_relativity",
    latex=r"KE = (\gamma - 1)mc^2 = mc^2\left(\frac{1}{\sqrt{1-v^2/c^2}} - 1\right)",
    sympy="KE = (gamma - 1)*m*c**2",
    variables=(("KE", "Kinetic energy", "J")),
    description="Reduces to ½mv² for v << c (Taylor expansion).",
    derives_from=("relativistic_energy", "mass_energy_equivalence"),
    uses=("c",),
    status=NodeStatus.PROVEN,
    tags=("kinetic", "relativistic"),
)

# Spacetime Interval
spacetime_interval = EquationNode(
    id="spacetime_interval",
    name="Spacetime Interval",
    domain="special_relativity",
    latex=r"(\Delta s)^2 = c^2(\Delta t)^2 - (\Delta x)^2 - (\Delta y)^2 - (\Delta z)^2",
    sympy="ds**2 = c**2*dt**2 - dx**2 - dy**2 - dz**2",
    variables=(("ds", "Spacetime interval", "m")),
    description="Invariant under Lorentz transformation. ds² > 0: timelike, < 0: spacelike, = 0: lightlike.",
    uses=("c",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("interval", "invariant"),
)

# Four-Momentum
four_momentum = EquationNode(
    id="four_momentum",
    name="Four-Momentum",
    domain="special_relativity",
    latex=r"p^\mu = (E/c, \vec{p}) = m\gamma(c, \vec{v})",
    sympy="p_mu = (E/c, p_x, p_y, p_z)",
    variables=(("p_mu", "Four-momentum", "(J/c, kg⋅m/s)")),
    description="Lorentz covariant momentum. p·p = m²c².",
    derives_from=("relativistic_energy", "relativistic_momentum"),
    uses=("c",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("four_vector", "momentum"),
)

# Doppler Effect (Relativistic)
relativistic_doppler = EquationNode(
    id="relativistic_doppler",
    name="Relativistic Doppler Effect",
    domain="special_relativity",
    latex=r"f' = f\sqrt{\frac{1-\beta}{1+\beta}} \text{ (approaching)}",
    sympy="f_prime = f*sqrt((1-beta)/(1+beta))",
    variables=(("f_prime", "Observed frequency", "Hz"), ("f", "Source frequency", "Hz"), ("beta", "v/c", "dimensionless")),
    description="Includes time dilation. Transverse Doppler: f' = f/γ.",
    derives_from=("lorentz_factor",),
    status=NodeStatus.PROVEN,
    tags=("doppler", "relativistic"),
)

# Relativistic Beaming
relativistic_beaming = EquationNode(
    id="relativistic_beaming",
    name="Relativistic Beaming",
    domain="special_relativity",
    latex=r"\theta' = \arctan\frac{\sin\theta}{\gamma(\cos\theta + \beta)}",
    sympy="theta_prime = atan(sin(theta)/(gamma*(cos(theta) + beta)))",
    variables=(("theta", "Emission angle in source frame", "rad"), ("theta_prime", "Observation angle", "rad")),
    description="Radiation beamed forward. Used in astrophysical jets.",
    derives_from=("lorentz_transformation",),
    status=NodeStatus.PROVEN,
    tags=("beaming", "jets"),
)

NODES = [
    lorentz_factor, time_dilation, length_contraction, lorentz_transform, velocity_addition,
    mass_energy, relativistic_energy, relativistic_momentum, energy_momentum_relation,
    relativistic_ke, spacetime_interval, four_momentum, relativistic_doppler, relativistic_beaming
]
