"""
PATH: physics/knowledge/equations/classical/orbital.py
PURPOSE: Orbital mechanics and Kepler's laws
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Kepler's First Law
kepler_first = EquationNode(
    id="kepler_first_law",
    name="Kepler's First Law",
    domain="classical_mechanics",
    latex=r"r = \frac{a(1-e^2)}{1 + e\cos\theta}",
    sympy="r = a*(1-e**2)/(1 + e*cos(theta))",
    variables=(("r", "Orbital radius", "m"), ("a", "Semi-major axis", "m"), ("e", "Eccentricity", "dimensionless"), ("theta", "True anomaly", "rad")),
    description="Planets move in ellipses with Sun at one focus. Conic section equation.",
    derives_from=("newton_gravity",),
    status=NodeStatus.PROVEN,
    tags=("kepler", "orbit", "ellipse"),
)

# Kepler's Second Law
kepler_second = EquationNode(
    id="kepler_second_law",
    name="Kepler's Second Law",
    domain="classical_mechanics",
    latex=r"\frac{dA}{dt} = \frac{L}{2m} = \text{const}",
    sympy="dA/dt = L/(2*m)",
    variables=(("A", "Area swept", "m²"), ("L", "Angular momentum", "kg⋅m²/s"), ("m", "Mass", "kg")),
    description="Equal areas in equal times. Consequence of angular momentum conservation.",
    derives_from=("angular_momentum_conservation",),
    status=NodeStatus.PROVEN,
    tags=("kepler", "angular_momentum"),
)

# Kepler's Third Law
kepler_third = EquationNode(
    id="kepler_third_law",
    name="Kepler's Third Law",
    domain="classical_mechanics",
    latex=r"T^2 = \frac{4\pi^2}{GM}a^3",
    sympy="T**2 = 4*pi**2 * a**3 / (G*M)",
    variables=(("T", "Orbital period", "s"), ("a", "Semi-major axis", "m"), ("G", "Gravitational constant", "m³/(kg⋅s²)"), ("M", "Central mass", "kg")),
    description="Period squared proportional to semi-major axis cubed.",
    derives_from=("newton_gravity",),
    uses=("G",),
    status=NodeStatus.PROVEN,
    tags=("kepler", "period", "orbit"),
)

# Orbital Velocity
orbital_velocity = EquationNode(
    id="orbital_velocity",
    name="Circular Orbital Velocity",
    domain="classical_mechanics",
    latex=r"v = \sqrt{\frac{GM}{r}}",
    sympy="v = sqrt(G*M/r)",
    variables=(("v", "Orbital velocity", "m/s"), ("G", "Gravitational constant", "m³/(kg⋅s²)"), ("M", "Central mass", "kg"), ("r", "Orbital radius", "m")),
    description="Speed for circular orbit at radius r.",
    derives_from=("newton_gravity", "centripetal_acceleration"),
    uses=("G",),
    status=NodeStatus.PROVEN,
    tags=("orbit", "velocity", "circular"),
)

# Vis-Viva Equation
vis_viva = EquationNode(
    id="vis_viva",
    name="Vis-Viva Equation",
    domain="classical_mechanics",
    latex=r"v^2 = GM\left(\frac{2}{r} - \frac{1}{a}\right)",
    sympy="v**2 = G*M*(2/r - 1/a)",
    variables=(("v", "Orbital speed", "m/s"), ("r", "Current radius", "m"), ("a", "Semi-major axis", "m")),
    description="Speed at any point in orbit. Fundamental orbital energy equation.",
    derives_from=("mechanical_energy_conservation", "kepler_first_law"),
    uses=("G",),
    status=NodeStatus.PROVEN,
    tags=("orbit", "energy", "vis_viva"),
)

# Orbital Energy
orbital_energy = EquationNode(
    id="orbital_energy",
    name="Orbital Energy",
    domain="classical_mechanics",
    latex=r"E = -\frac{GMm}{2a}",
    sympy="E = -G*M*m/(2*a)",
    variables=(("E", "Total orbital energy", "J"), ("a", "Semi-major axis", "m")),
    description="Total energy depends only on semi-major axis. Negative for bound orbits.",
    derives_from=("mechanical_energy_conservation",),
    uses=("G",),
    status=NodeStatus.PROVEN,
    tags=("orbit", "energy"),
)

# Orbital Angular Momentum
orbital_angular_momentum = EquationNode(
    id="orbital_angular_momentum",
    name="Orbital Angular Momentum",
    domain="classical_mechanics",
    latex=r"L = m\sqrt{GMa(1-e^2)}",
    sympy="L = m*sqrt(G*M*a*(1-e**2))",
    variables=(("L", "Angular momentum", "kg⋅m²/s"), ("a", "Semi-major axis", "m"), ("e", "Eccentricity", "dimensionless")),
    description="Angular momentum in terms of orbital elements.",
    derives_from=("angular_momentum",),
    uses=("G",),
    status=NodeStatus.PROVEN,
    tags=("orbit", "angular_momentum"),
)

# Hohmann Transfer
hohmann_transfer = EquationNode(
    id="hohmann_transfer",
    name="Hohmann Transfer Orbit",
    domain="classical_mechanics",
    latex=r"\Delta v_1 = \sqrt{\frac{GM}{r_1}}\left(\sqrt{\frac{2r_2}{r_1+r_2}} - 1\right)",
    sympy="dv1 = sqrt(G*M/r1)*(sqrt(2*r2/(r1+r2)) - 1)",
    variables=(("dv1", "First velocity change", "m/s"), ("r1", "Initial orbit radius", "m"), ("r2", "Final orbit radius", "m")),
    description="Minimum energy transfer between two circular orbits.",
    derives_from=("vis_viva",),
    uses=("G",),
    status=NodeStatus.PROVEN,
    tags=("orbit", "transfer", "delta_v"),
)

# Sphere of Influence
sphere_influence = EquationNode(
    id="sphere_of_influence",
    name="Sphere of Influence",
    domain="classical_mechanics",
    latex=r"r_{SOI} = a\left(\frac{m}{M}\right)^{2/5}",
    sympy="r_SOI = a*(m/M)**(2/5)",
    variables=(("r_SOI", "Sphere of influence radius", "m"), ("a", "Orbital semi-major axis", "m"), ("m", "Body mass", "kg"), ("M", "Central mass", "kg")),
    description="Region where body's gravity dominates over central body.",
    derives_from=("newton_gravity",),
    status=NodeStatus.APPROXIMATE,
    tags=("orbit", "perturbation"),
)

# Roche Limit
roche_limit = EquationNode(
    id="roche_limit",
    name="Roche Limit",
    domain="classical_mechanics",
    latex=r"d = R_M\left(2\frac{\rho_M}{\rho_m}\right)^{1/3} \approx 2.44 R_M\left(\frac{\rho_M}{\rho_m}\right)^{1/3}",
    sympy="d = 2.44*R_M*(rho_M/rho_m)**(1/3)",
    variables=(("d", "Roche limit", "m"), ("R_M", "Primary radius", "m"), ("rho_M", "Primary density", "kg/m³"), ("rho_m", "Satellite density", "kg/m³")),
    description="Minimum orbital radius before tidal forces disrupt satellite.",
    derives_from=("newton_gravity",),
    status=NodeStatus.PROVEN,
    tags=("orbit", "tidal", "disruption"),
)

# Hill Sphere
hill_sphere = EquationNode(
    id="hill_sphere",
    name="Hill Sphere",
    domain="classical_mechanics",
    latex=r"r_H = a\left(\frac{m}{3M}\right)^{1/3}",
    sympy="r_H = a*(m/(3*M))**(1/3)",
    variables=(("r_H", "Hill radius", "m"), ("a", "Orbital distance", "m"), ("m", "Body mass", "kg"), ("M", "Primary mass", "kg")),
    description="Region where body can retain satellites against central body's tidal forces.",
    derives_from=("newton_gravity",),
    status=NodeStatus.PROVEN,
    tags=("orbit", "stability"),
)

# Orbital Period Circular
orbital_period_circular = EquationNode(
    id="orbital_period_circular",
    name="Circular Orbit Period",
    domain="classical_mechanics",
    latex=r"T = 2\pi\sqrt{\frac{r^3}{GM}}",
    sympy="T = 2*pi*sqrt(r**3/(G*M))",
    variables=(("T", "Period", "s"), ("r", "Radius", "m")),
    description="Period of circular orbit. Special case of Kepler's third law.",
    derives_from=("kepler_third_law",),
    uses=("G",),
    status=NodeStatus.PROVEN,
    tags=("orbit", "period", "circular"),
)

# Specific Orbital Energy
specific_orbital_energy = EquationNode(
    id="specific_orbital_energy",
    name="Specific Orbital Energy",
    domain="classical_mechanics",
    latex=r"\epsilon = \frac{v^2}{2} - \frac{GM}{r} = -\frac{GM}{2a}",
    sympy="epsilon = v**2/2 - G*M/r",
    variables=(("epsilon", "Specific energy", "J/kg"), ("v", "Speed", "m/s"), ("r", "Radius", "m")),
    description="Energy per unit mass. Determines orbit type: ε<0 ellipse, ε=0 parabola, ε>0 hyperbola.",
    derives_from=("orbital_energy",),
    uses=("G",),
    status=NodeStatus.PROVEN,
    tags=("orbit", "energy", "specific"),
)

# Eccentricity Vector
eccentricity_vector = EquationNode(
    id="eccentricity_vector",
    name="Eccentricity Vector (Laplace-Runge-Lenz)",
    domain="classical_mechanics",
    latex=r"\vec{e} = \frac{\vec{v} \times \vec{L}}{GMm} - \frac{\vec{r}}{r}",
    sympy="e = (v cross L)/(G*M*m) - r/|r|",
    variables=(("e", "Eccentricity vector", "dimensionless"), ("v", "Velocity", "m/s"), ("L", "Angular momentum", "kg⋅m²/s")),
    description="Conserved vector pointing toward perihelion. Additional integral of motion for Kepler problem.",
    derives_from=("newton_gravity", "angular_momentum"),
    status=NodeStatus.PROVEN,
    tags=("orbit", "conservation", "symmetry"),
)

# Synodic Period
synodic_period = EquationNode(
    id="synodic_period",
    name="Synodic Period",
    domain="classical_mechanics",
    latex=r"\frac{1}{P_{syn}} = \left|\frac{1}{P_1} - \frac{1}{P_2}\right|",
    sympy="1/P_syn = |1/P1 - 1/P2|",
    variables=(("P_syn", "Synodic period", "s"), ("P1", "Period of body 1", "s"), ("P2", "Period of body 2", "s")),
    description="Time between successive conjunctions of two bodies.",
    derives_from=("kepler_third_law",),
    status=NodeStatus.PROVEN,
    tags=("orbit", "period", "conjunction"),
)

NODES = [
    kepler_first, kepler_second, kepler_third, orbital_velocity, vis_viva,
    orbital_energy, orbital_angular_momentum, hohmann_transfer, sphere_influence,
    roche_limit, hill_sphere, orbital_period_circular, specific_orbital_energy,
    eccentricity_vector, synodic_period
]
