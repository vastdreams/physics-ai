"""
PATH: physics/knowledge/equations/relativity/special.py
PURPOSE: Special relativity equations

FIRST PRINCIPLES:
1. Laws of physics same in all inertial frames
2. Speed of light c is constant in all frames
These postulates lead to Lorentz transformations, time dilation,
length contraction, and E=mc².
"""

from physics.knowledge.base.node import EquationNode, PrincipleNode, NodeStatus

# Principle of Relativity
relativity_principle = PrincipleNode(
    id="principle_of_relativity",
    name="Principle of Relativity",
    domain="special_relativity",
    statement="The laws of physics are the same in all inertial reference frames.",
    mathematical_form="Laws invariant under Lorentz transformations",
    description="First postulate of special relativity. "
                "No absolute rest frame can be detected.",
    discoverer="Albert Einstein",
    year=1905,
    leads_to=("lorentz_transformation",),
    tags=("postulate", "symmetry", "invariance"),
)

# Constancy of Light Speed
light_speed_postulate = PrincipleNode(
    id="light_speed_postulate",
    name="Constancy of Speed of Light",
    domain="special_relativity",
    statement="The speed of light in vacuum is the same for all observers, "
              "regardless of the motion of the source or observer.",
    mathematical_form="c = constant",
    description="Second postulate of special relativity. "
                "Leads to breakdown of Newtonian absolute time.",
    discoverer="Albert Einstein",
    year=1905,
    leads_to=("lorentz_transformation", "time_dilation"),
    tags=("postulate", "light", "invariance"),
)

# Lorentz Factor
lorentz_factor = EquationNode(
    id="lorentz_factor",
    name="Lorentz Factor",
    domain="special_relativity",
    latex=r"\gamma = \frac{1}{\sqrt{1 - v^2/c^2}} = \frac{1}{\sqrt{1 - \beta^2}}",
    sympy="gamma = 1 / sqrt(1 - v**2 / c**2)",
    variables=(
        ("gamma", "Lorentz factor", "(dimensionless)"),
        ("v", "Relative velocity", "m/s"),
        ("c", "Speed of light", "m/s"),
        ("beta", "v/c", "(dimensionless)"),
    ),
    description="Appears in all relativistic equations. γ → 1 as v → 0, "
                "γ → ∞ as v → c.",
    uses=("c",),
    leads_to=("time_dilation", "length_contraction", "relativistic_momentum"),
    discoverer="Hendrik Lorentz",
    year=1904,
    status=NodeStatus.PROVEN,
    tags=("factor", "transformation"),
)

# Time Dilation
time_dilation = EquationNode(
    id="time_dilation",
    name="Time Dilation",
    domain="special_relativity",
    latex=r"\Delta t = \gamma \Delta t_0 = \frac{\Delta t_0}{\sqrt{1 - v^2/c^2}}",
    sympy="delta_t = gamma * delta_t_0",
    variables=(
        ("delta_t", "Dilated time interval", "s"),
        ("delta_t_0", "Proper time", "s"),
        ("gamma", "Lorentz factor", "(dimensionless)"),
    ),
    description="Moving clocks run slow. Proper time is in rest frame. "
                "Confirmed by muon decay, GPS satellites.",
    derives_from=("lorentz_factor",),
    discoverer="Albert Einstein",
    year=1905,
    status=NodeStatus.EXPERIMENTAL,
    tags=("time", "dilation", "muon"),
)

# Length Contraction
length_contraction = EquationNode(
    id="length_contraction",
    name="Length Contraction",
    domain="special_relativity",
    latex=r"L = \frac{L_0}{\gamma} = L_0\sqrt{1 - v^2/c^2}",
    sympy="L = L_0 / gamma",
    variables=(
        ("L", "Contracted length", "m"),
        ("L_0", "Proper length", "m"),
        ("gamma", "Lorentz factor", "(dimensionless)"),
    ),
    description="Moving objects contract in direction of motion. "
                "Proper length is in rest frame.",
    derives_from=("lorentz_factor",),
    discoverer="Hendrik Lorentz, George FitzGerald",
    year=1892,
    status=NodeStatus.PROVEN,
    tags=("length", "contraction", "fitzgerald"),
)

# Mass-Energy Equivalence
mass_energy = EquationNode(
    id="mass_energy_equivalence",
    name="Mass-Energy Equivalence",
    domain="special_relativity",
    latex=r"E = mc^2 \quad E_0 = m_0 c^2 \quad E = \gamma m_0 c^2",
    sympy="E = m * c**2",
    variables=(
        ("E", "Total energy", "J"),
        ("E_0", "Rest energy", "J"),
        ("m_0", "Rest mass", "kg"),
        ("c", "Speed of light", "m/s"),
    ),
    description="Mass and energy are equivalent. Rest energy E₀ = m₀c². "
                "Basis of nuclear energy.",
    derivation_steps=(
        "From relativistic momentum p = γm₀v",
        "Work-energy: dE = v⋅dp",
        "Integrate to get E = γm₀c²",
        "At rest (γ=1): E₀ = m₀c²",
    ),
    derives_from=("lorentz_factor", "relativistic_momentum"),
    uses=("c",),
    leads_to=("nuclear_binding_energy", "pair_production"),
    discoverer="Albert Einstein",
    year=1905,
    status=NodeStatus.FUNDAMENTAL,
    tags=("energy", "mass", "famous"),
)

# Relativistic Momentum
relativistic_momentum = EquationNode(
    id="relativistic_momentum",
    name="Relativistic Momentum",
    domain="special_relativity",
    latex=r"\vec{p} = \gamma m_0 \vec{v}",
    sympy="p = gamma * m_0 * v",
    variables=(
        ("p", "Momentum", "kg⋅m/s"),
        ("gamma", "Lorentz factor", "(dimensionless)"),
        ("m_0", "Rest mass", "kg"),
        ("v", "Velocity", "m/s"),
    ),
    description="Momentum increases without bound as v → c. "
                "Reduces to p = mv at low speeds.",
    derives_from=("lorentz_factor",),
    leads_to=("mass_energy_equivalence",),
    discoverer="Albert Einstein",
    year=1905,
    status=NodeStatus.PROVEN,
    tags=("momentum", "relativistic"),
)

# Energy-Momentum Relation
energy_momentum = EquationNode(
    id="energy_momentum_relation",
    name="Energy-Momentum Relation",
    domain="special_relativity",
    latex=r"E^2 = (pc)^2 + (m_0 c^2)^2",
    sympy="E**2 = (p*c)**2 + (m_0*c**2)**2",
    variables=(
        ("E", "Total energy", "J"),
        ("p", "Momentum", "kg⋅m/s"),
        ("m_0", "Rest mass", "kg"),
        ("c", "Speed of light", "m/s"),
    ),
    description="Invariant mass-energy relation. For photons (m₀=0): E = pc. "
                "For rest (p=0): E = m₀c².",
    derives_from=("mass_energy_equivalence", "relativistic_momentum"),
    uses=("c",),
    discoverer="Albert Einstein",
    year=1905,
    status=NodeStatus.PROVEN,
    tags=("invariant", "energy", "momentum"),
)

# Export all nodes
NODES = [
    relativity_principle,
    light_speed_postulate,
    lorentz_factor,
    time_dilation,
    length_contraction,
    mass_energy,
    relativistic_momentum,
    energy_momentum,
]
