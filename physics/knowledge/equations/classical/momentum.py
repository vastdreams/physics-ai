"""
PATH: physics/knowledge/equations/classical/momentum.py
PURPOSE: Momentum equations in classical mechanics

FIRST PRINCIPLES:
Momentum is the fundamental quantity in mechanics, more fundamental
than velocity. Newton's laws are really about momentum, not acceleration.
Conservation of momentum follows from translational symmetry (Noether).
"""

from physics.knowledge.base.node import EquationNode, PrincipleNode, NodeStatus

# Linear Momentum Definition
linear_momentum = EquationNode(
    id="linear_momentum",
    name="Linear Momentum",
    domain="classical_mechanics",
    latex=r"\vec{p} = m\vec{v}",
    sympy="p = m * v",
    variables=(
        ("p", "Linear momentum", "kg⋅m/s"),
        ("m", "Mass", "kg"),
        ("v", "Velocity", "m/s"),
    ),
    description="Momentum measures 'quantity of motion'. Vector quantity. "
                "More fundamental than velocity in mechanics.",
    derivation_steps=(
        "Definition: p = mv",
        "Newton's second law is really F = dp/dt",
        "For constant mass: dp/dt = m(dv/dt) = ma",
    ),
    leads_to=("momentum_conservation", "newton_second_law"),
    discoverer="Isaac Newton",
    year=1687,
    status=NodeStatus.FUNDAMENTAL,
    tags=("momentum", "motion", "vector"),
)

# Conservation of Momentum
momentum_conservation = PrincipleNode(
    id="momentum_conservation",
    name="Conservation of Linear Momentum",
    domain="classical_mechanics",
    statement="Total momentum of an isolated system remains constant.",
    mathematical_form=r"\sum\vec{p}_i = \text{constant when } \sum\vec{F}_{ext} = 0",
    description="Follows from Newton's third law. Also from Noether's theorem "
                "as consequence of space translation symmetry.",
    discoverer="Isaac Newton",
    year=1687,
    leads_to=("collision_equations", "rocket_equation"),
    tags=("conservation", "symmetry", "fundamental"),
)

# Impulse-Momentum Theorem
impulse_momentum = EquationNode(
    id="impulse_momentum",
    name="Impulse-Momentum Theorem",
    domain="classical_mechanics",
    latex=r"\vec{J} = \int \vec{F} dt = \Delta\vec{p}",
    sympy="J = delta_p",
    variables=(
        ("J", "Impulse", "N⋅s"),
        ("F", "Force", "N"),
        ("t", "Time", "s"),
        ("p", "Momentum", "kg⋅m/s"),
    ),
    description="Impulse equals change in momentum. Useful for collisions "
                "where force varies rapidly over short time.",
    derivation_steps=(
        "From Newton's second law: F = dp/dt",
        "Integrate: ∫F dt = ∫dp = Δp",
        "Define impulse J = ∫F dt",
        "Therefore J = Δp",
    ),
    derives_from=("newton_second_law", "linear_momentum"),
    leads_to=("collision_equations",),
    discoverer="(classical mechanics)",
    year=1750,
    status=NodeStatus.PROVEN,
    tags=("impulse", "momentum", "collisions"),
)

# Angular Momentum
angular_momentum = EquationNode(
    id="angular_momentum",
    name="Angular Momentum",
    domain="classical_mechanics",
    latex=r"\vec{L} = \vec{r} \times \vec{p} = I\vec{\omega}",
    sympy="L = r * p * sin(theta)",
    variables=(
        ("L", "Angular momentum", "kg⋅m²/s"),
        ("r", "Position vector", "m"),
        ("p", "Linear momentum", "kg⋅m/s"),
        ("I", "Moment of inertia", "kg⋅m²"),
        ("omega", "Angular velocity", "rad/s"),
    ),
    description="Rotational analog of linear momentum. L = r × p for "
                "point mass, L = Iω for rigid body rotation.",
    derivation_steps=(
        "Define L = r × p for point mass",
        "For rotation: v = ω × r, so p = mω × r",
        "L = r × (mω × r) = mr²ω (for r ⊥ ω)",
        "Define I = mr², so L = Iω",
    ),
    derives_from=("linear_momentum",),
    leads_to=("angular_momentum_conservation", "torque_equation"),
    discoverer="Isaac Newton",
    year=1687,
    status=NodeStatus.PROVEN,
    tags=("rotation", "angular", "vector"),
)

# Torque
torque = EquationNode(
    id="torque",
    name="Torque",
    domain="classical_mechanics",
    latex=r"\vec{\tau} = \vec{r} \times \vec{F} = I\vec{\alpha} = \frac{d\vec{L}}{dt}",
    sympy="tau = r * F * sin(theta)",
    variables=(
        ("tau", "Torque", "N⋅m"),
        ("r", "Position vector", "m"),
        ("F", "Force", "N"),
        ("I", "Moment of inertia", "kg⋅m²"),
        ("alpha", "Angular acceleration", "rad/s²"),
        ("L", "Angular momentum", "kg⋅m²/s"),
    ),
    description="Rotational analog of force. Rate of change of angular momentum. "
                "τ = Iα is rotational Newton's second law.",
    derivation_steps=(
        "From L = r × p, differentiate: dL/dt = dr/dt × p + r × dp/dt",
        "dr/dt × p = v × mv = 0 (parallel)",
        "r × dp/dt = r × F = τ",
        "Therefore τ = dL/dt",
    ),
    derives_from=("angular_momentum", "newton_second_law"),
    leads_to=("angular_momentum_conservation",),
    discoverer="(mechanics)",
    year=1750,
    status=NodeStatus.PROVEN,
    tags=("rotation", "force", "moment"),
)

# Conservation of Angular Momentum
angular_momentum_conservation = PrincipleNode(
    id="angular_momentum_conservation",
    name="Conservation of Angular Momentum",
    domain="classical_mechanics",
    statement="Angular momentum is conserved when net external torque is zero.",
    mathematical_form=r"\vec{L} = \text{constant when } \sum\vec{\tau}_{ext} = 0",
    description="Follows from rotational dynamics. Also from Noether's theorem "
                "as consequence of rotational symmetry.",
    discoverer="(mechanics)",
    year=1750,
    leads_to=("kepler_second_law", "gyroscope_dynamics"),
    tags=("conservation", "rotation", "symmetry"),
)

# Center of Mass
center_of_mass = EquationNode(
    id="center_of_mass",
    name="Center of Mass",
    domain="classical_mechanics",
    latex=r"\vec{r}_{cm} = \frac{\sum m_i \vec{r}_i}{\sum m_i}",
    sympy="r_cm = sum(m_i * r_i) / sum(m_i)",
    variables=(
        ("r_cm", "Center of mass position", "m"),
        ("m_i", "Mass of particle i", "kg"),
        ("r_i", "Position of particle i", "m"),
    ),
    description="Mass-weighted average position. System momentum equals "
                "total mass times CM velocity: P = Mv_cm.",
    derivation_steps=(
        "Define as weighted average: r_cm = Σ(m_i r_i) / Σm_i",
        "Total momentum: P = Σp_i = Σ(m_i v_i)",
        "Differentiate r_cm: v_cm = Σ(m_i v_i) / M = P/M",
        "Therefore P = Mv_cm",
    ),
    derives_from=("linear_momentum",),
    leads_to=("two_body_reduction",),
    discoverer="(mechanics)",
    year=1750,
    status=NodeStatus.PROVEN,
    tags=("system", "composite", "reduction"),
)

# Export all nodes
NODES = [
    linear_momentum,
    momentum_conservation,
    impulse_momentum,
    angular_momentum,
    torque,
    angular_momentum_conservation,
    center_of_mass,
]
