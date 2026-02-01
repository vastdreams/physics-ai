"""
PATH: physics/knowledge/equations/classical/newton.py
PURPOSE: Newton's laws of motion and gravitation

FIRST PRINCIPLES DERIVATION:
Newton's laws form the axiomatic basis of classical mechanics.
They are postulates, not derived from anything more fundamental
(within classical physics). Relativistic and quantum mechanics
reduce to these in appropriate limits.
"""

from physics.knowledge.base.node import EquationNode, PrincipleNode, NodeStatus

# Newton's First Law (Inertia)
newton_first = PrincipleNode(
    id="newton_first_law",
    name="Newton's First Law",
    domain="classical_mechanics",
    statement="A body remains at rest or in uniform motion unless acted upon "
              "by a net external force.",
    mathematical_form="d\\vec{v}/dt = 0 \\text{ when } \\sum\\vec{F} = 0",
    description="Law of inertia. Defines inertial reference frames. "
                "Galileo's principle of relativity follows from this.",
    discoverer="Isaac Newton, Galileo Galilei",
    year=1687,
    leads_to=("newton_second_law", "inertial_frame"),
    tags=("foundation", "inertia", "reference_frame"),
)

# Newton's Second Law
newton_second = EquationNode(
    id="newton_second_law",
    name="Newton's Second Law",
    domain="classical_mechanics",
    latex=r"\vec{F} = m\vec{a} = m\frac{d\vec{v}}{dt} = \frac{d\vec{p}}{dt}",
    sympy="F = m * a",
    variables=(
        ("F", "Net force", "N"),
        ("m", "Mass", "kg"),
        ("a", "Acceleration", "m/s²"),
        ("p", "Momentum", "kg⋅m/s"),
    ),
    description="Relates force to rate of change of momentum. "
                "Defines force operationally. Central equation of mechanics.",
    derivation_steps=(
        "Postulate: Force is proportional to rate of change of motion",
        "Define momentum p = mv for constant mass",
        "F = dp/dt = m(dv/dt) = ma",
    ),
    assumptions=(
        "Constant mass (non-relativistic)",
        "Inertial reference frame",
        "Point particle or rigid body",
    ),
    derives_from=("newton_first_law",),
    leads_to=(
        "kinetic_energy",
        "work_energy_theorem",
        "momentum_conservation",
        "harmonic_oscillator",
    ),
    discoverer="Isaac Newton",
    year=1687,
    status=NodeStatus.FUNDAMENTAL,
    tags=("foundation", "dynamics", "force"),
)

# Newton's Third Law
newton_third = PrincipleNode(
    id="newton_third_law",
    name="Newton's Third Law",
    domain="classical_mechanics",
    statement="For every action, there is an equal and opposite reaction.",
    mathematical_form=r"\vec{F}_{12} = -\vec{F}_{21}",
    description="Forces come in pairs. Guarantees momentum conservation "
                "in isolated systems. Defines the nature of interactions.",
    discoverer="Isaac Newton",
    year=1687,
    leads_to=("momentum_conservation", "center_of_mass"),
    tags=("foundation", "interaction", "symmetry"),
)

# Newton's Law of Gravitation
newton_gravity = EquationNode(
    id="newton_gravity",
    name="Newton's Law of Universal Gravitation",
    domain="classical_mechanics",
    latex=r"F = G\frac{m_1 m_2}{r^2}",
    sympy="F = G * m1 * m2 / r**2",
    variables=(
        ("F", "Gravitational force", "N"),
        ("G", "Gravitational constant", "m³/(kg⋅s²)"),
        ("m1", "Mass 1", "kg"),
        ("m2", "Mass 2", "kg"),
        ("r", "Distance between centers", "m"),
    ),
    description="Inverse-square law for gravitational attraction. "
                "First unified terrestrial and celestial mechanics.",
    derivation_steps=(
        "Empirical: Kepler's third law T² ∝ a³ suggests inverse-square",
        "Newton showed inverse-square gives elliptical orbits",
        "Cavendish measured G experimentally",
    ),
    assumptions=(
        "Point masses or spherically symmetric",
        "Instantaneous action at distance",
        "Weak gravitational fields (v << c)",
    ),
    uses=("G",),
    leads_to=(
        "gravitational_potential_energy",
        "orbital_mechanics",
        "escape_velocity",
    ),
    conditions=("Non-relativistic limit of general relativity",),
    discoverer="Isaac Newton",
    year=1687,
    status=NodeStatus.APPROXIMATE,
    tags=("gravity", "inverse_square", "universal"),
)

# Gravitational acceleration
gravitational_acceleration = EquationNode(
    id="gravitational_acceleration",
    name="Gravitational Acceleration",
    domain="classical_mechanics",
    latex=r"g = \frac{GM}{r^2}",
    sympy="g = G * M / r**2",
    variables=(
        ("g", "Gravitational acceleration", "m/s²"),
        ("G", "Gravitational constant", "m³/(kg⋅s²)"),
        ("M", "Central mass", "kg"),
        ("r", "Distance from center", "m"),
    ),
    description="Acceleration due to gravity at distance r from mass M. "
                "At Earth's surface, g ≈ 9.81 m/s².",
    derivation_steps=(
        "From Newton's second law: F = ma",
        "Gravitational force: F = GMm/r²",
        "Therefore: a = g = GM/r²",
    ),
    derives_from=("newton_gravity", "newton_second_law"),
    uses=("G",),
    discoverer="Isaac Newton",
    year=1687,
    status=NodeStatus.PROVEN,
    tags=("gravity", "acceleration", "free_fall"),
)

# Export all nodes
NODES = [newton_first, newton_second, newton_third, newton_gravity, gravitational_acceleration]
