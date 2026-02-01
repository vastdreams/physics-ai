"""
PATH: physics/knowledge/equations/classical/energy.py
PURPOSE: Energy equations in classical mechanics

FIRST PRINCIPLES DERIVATION:
Energy concepts derive from Newton's laws through integration.
Work is defined as force times displacement, leading to
kinetic and potential energy through the work-energy theorem.
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Kinetic Energy
kinetic_energy = EquationNode(
    id="kinetic_energy",
    name="Kinetic Energy",
    domain="classical_mechanics",
    latex=r"KE = \frac{1}{2}mv^2",
    sympy="KE = (1/2) * m * v**2",
    variables=(
        ("KE", "Kinetic energy", "J"),
        ("m", "Mass", "kg"),
        ("v", "Speed", "m/s"),
    ),
    description="Energy of motion. Scalar quantity that depends on "
                "speed squared, not velocity direction.",
    derivation_steps=(
        "Start from Newton's second law: F = ma = m(dv/dt)",
        "Work done: W = ∫F⋅dx = ∫m(dv/dt)⋅dx",
        "Using v = dx/dt: W = ∫mv⋅dv",
        "Integrate: W = (1/2)mv² - (1/2)mv₀²",
        "Define KE = (1/2)mv²",
    ),
    assumptions=(
        "Non-relativistic speeds (v << c)",
        "Point mass or rigid body",
    ),
    derives_from=("newton_second_law",),
    leads_to=("work_energy_theorem", "mechanical_energy_conservation"),
    discoverer="Gottfried Leibniz",
    year=1686,
    status=NodeStatus.PROVEN,
    tags=("energy", "motion", "scalar"),
)

# Gravitational Potential Energy
gravitational_pe = EquationNode(
    id="gravitational_potential_energy",
    name="Gravitational Potential Energy",
    domain="classical_mechanics",
    latex=r"PE = mgh \quad \text{(near surface)} \quad PE = -\frac{GMm}{r}",
    sympy="PE = m * g * h",
    variables=(
        ("PE", "Potential energy", "J"),
        ("m", "Mass", "kg"),
        ("g", "Gravitational acceleration", "m/s²"),
        ("h", "Height above reference", "m"),
        ("G", "Gravitational constant", "m³/(kg⋅s²)"),
        ("M", "Central mass", "kg"),
        ("r", "Distance from center", "m"),
    ),
    description="Energy stored in gravitational field. Near Earth's surface "
                "PE ≈ mgh. General form PE = -GMm/r (zero at infinity).",
    derivation_steps=(
        "Work against gravity: W = ∫F⋅dr",
        "Near surface: F = mg constant, W = mgh",
        "General: F = GMm/r², W = -∫(GMm/r²)dr = -GMm/r",
        "Potential energy is negative work: PE = -W",
    ),
    derives_from=("newton_gravity",),
    leads_to=("mechanical_energy_conservation", "escape_velocity"),
    uses=("G",),
    discoverer="(classical mechanics)",
    year=1750,
    status=NodeStatus.PROVEN,
    tags=("energy", "potential", "gravity"),
)

# Elastic Potential Energy
elastic_pe = EquationNode(
    id="elastic_potential_energy",
    name="Elastic Potential Energy",
    domain="classical_mechanics",
    latex=r"PE = \frac{1}{2}kx^2",
    sympy="PE = (1/2) * k * x**2",
    variables=(
        ("PE", "Potential energy", "J"),
        ("k", "Spring constant", "N/m"),
        ("x", "Displacement from equilibrium", "m"),
    ),
    description="Energy stored in a deformed elastic object. "
                "Basis of simple harmonic motion.",
    derivation_steps=(
        "Hooke's law: F = -kx",
        "Work to compress/stretch: W = ∫F⋅dx = ∫kx⋅dx",
        "PE = (1/2)kx²",
    ),
    derives_from=("hooke_law",),
    leads_to=("harmonic_oscillator",),
    discoverer="Robert Hooke",
    year=1678,
    status=NodeStatus.PROVEN,
    tags=("energy", "potential", "elastic", "spring"),
)

# Work-Energy Theorem
work_energy = EquationNode(
    id="work_energy_theorem",
    name="Work-Energy Theorem",
    domain="classical_mechanics",
    latex=r"W_{net} = \Delta KE = \frac{1}{2}mv_f^2 - \frac{1}{2}mv_i^2",
    sympy="W = KE_f - KE_i",
    variables=(
        ("W", "Net work done", "J"),
        ("KE", "Kinetic energy", "J"),
        ("m", "Mass", "kg"),
        ("v_f", "Final velocity", "m/s"),
        ("v_i", "Initial velocity", "m/s"),
    ),
    description="Net work equals change in kinetic energy. "
                "Connects forces (dynamics) to energy (scalar) description.",
    derivation_steps=(
        "From F = ma and a = dv/dt",
        "W = ∫F⋅dx = ∫ma⋅dx = ∫m(dv/dt)(dx)",
        "dx/dt = v, so W = ∫mv⋅dv = (1/2)mv² |_{v_i}^{v_f}",
        "W = (1/2)mv_f² - (1/2)mv_i² = ΔKE",
    ),
    derives_from=("newton_second_law", "kinetic_energy"),
    leads_to=("mechanical_energy_conservation",),
    discoverer="Gaspard-Gustave de Coriolis",
    year=1829,
    status=NodeStatus.PROVEN,
    tags=("energy", "work", "theorem"),
)

# Conservation of Mechanical Energy
mechanical_energy = EquationNode(
    id="mechanical_energy_conservation",
    name="Conservation of Mechanical Energy",
    domain="classical_mechanics",
    latex=r"E = KE + PE = \text{constant (conservative forces)}",
    sympy="E = KE + PE",
    variables=(
        ("E", "Total mechanical energy", "J"),
        ("KE", "Kinetic energy", "J"),
        ("PE", "Potential energy", "J"),
    ),
    description="Total mechanical energy is conserved when only "
                "conservative forces do work. Foundation of many solutions.",
    derivation_steps=(
        "Work-energy theorem: W_net = ΔKE",
        "For conservative force: W_conservative = -ΔPE",
        "If only conservative forces: ΔKE = -ΔPE",
        "Therefore: Δ(KE + PE) = 0, so E = KE + PE = const",
    ),
    assumptions=(
        "Only conservative forces (no friction, drag)",
        "Isolated system",
    ),
    derives_from=("work_energy_theorem", "kinetic_energy"),
    leads_to=("escape_velocity", "orbital_energy"),
    discoverer="(classical mechanics)",
    year=1850,
    status=NodeStatus.PROVEN,
    tags=("conservation", "energy", "fundamental"),
)

# Power
power = EquationNode(
    id="power",
    name="Power",
    domain="classical_mechanics",
    latex=r"P = \frac{dW}{dt} = \vec{F} \cdot \vec{v}",
    sympy="P = F * v",
    variables=(
        ("P", "Power", "W"),
        ("W", "Work", "J"),
        ("t", "Time", "s"),
        ("F", "Force", "N"),
        ("v", "Velocity", "m/s"),
    ),
    description="Rate of doing work or energy transfer. "
                "P = F⋅v for constant force.",
    derivation_steps=(
        "Power is rate of work: P = dW/dt",
        "W = F⋅x, so dW = F⋅dx",
        "P = F⋅(dx/dt) = F⋅v",
    ),
    derives_from=("work_energy_theorem",),
    discoverer="James Watt",
    year=1782,
    status=NodeStatus.PROVEN,
    tags=("power", "rate", "energy_transfer"),
)

# Escape Velocity
escape_velocity = EquationNode(
    id="escape_velocity",
    name="Escape Velocity",
    domain="classical_mechanics",
    latex=r"v_{escape} = \sqrt{\frac{2GM}{r}}",
    sympy="v_esc = sqrt(2 * G * M / r)",
    variables=(
        ("v_esc", "Escape velocity", "m/s"),
        ("G", "Gravitational constant", "m³/(kg⋅s²)"),
        ("M", "Central mass", "kg"),
        ("r", "Distance from center", "m"),
    ),
    description="Minimum velocity to escape gravitational field "
                "from distance r. For Earth surface: ~11.2 km/s.",
    derivation_steps=(
        "Use energy conservation: KE + PE = 0 (escape to infinity)",
        "(1/2)mv² - GMm/r = 0",
        "v² = 2GM/r",
        "v_escape = √(2GM/r)",
    ),
    derives_from=("mechanical_energy_conservation", "gravitational_potential_energy"),
    uses=("G",),
    discoverer="(derived)",
    year=1728,
    status=NodeStatus.PROVEN,
    tags=("orbital", "escape", "gravity"),
)

# Export all nodes
NODES = [
    kinetic_energy,
    gravitational_pe,
    elastic_pe,
    work_energy,
    mechanical_energy,
    power,
    escape_velocity,
]
