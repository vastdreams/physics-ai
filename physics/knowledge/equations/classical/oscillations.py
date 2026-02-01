"""
PATH: physics/knowledge/equations/classical/oscillations.py
PURPOSE: Oscillatory motion equations (SHM, damped, driven)

FIRST PRINCIPLES:
Simple harmonic motion arises from linear restoring forces (F ∝ -x).
The solution is sinusoidal. Real oscillators include damping
(energy dissipation) and can be driven (energy input).
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Hooke's Law
hooke_law = EquationNode(
    id="hooke_law",
    name="Hooke's Law",
    domain="classical_mechanics",
    latex=r"F = -kx",
    sympy="F = -k * x",
    variables=(
        ("F", "Restoring force", "N"),
        ("k", "Spring constant", "N/m"),
        ("x", "Displacement", "m"),
    ),
    description="Linear restoring force for small deformations. "
                "Basis of simple harmonic motion. Valid for elastic limit.",
    derivation_steps=(
        "Empirical law for elastic materials",
        "Force proportional to displacement: F ∝ x",
        "Negative sign: force opposes displacement",
        "Constant of proportionality k is stiffness",
    ),
    assumptions=("Small displacements", "Elastic limit not exceeded"),
    leads_to=("harmonic_oscillator", "elastic_potential_energy"),
    discoverer="Robert Hooke",
    year=1678,
    status=NodeStatus.EMPIRICAL,
    tags=("spring", "elastic", "restoring"),
)

# Simple Harmonic Oscillator
harmonic_oscillator = EquationNode(
    id="harmonic_oscillator",
    name="Simple Harmonic Oscillator",
    domain="classical_mechanics",
    latex=r"\frac{d^2x}{dt^2} + \omega_0^2 x = 0 \quad \text{solution: } x(t) = A\cos(\omega_0 t + \phi)",
    sympy="x = A * cos(omega_0 * t + phi)",
    variables=(
        ("x", "Displacement", "m"),
        ("t", "Time", "s"),
        ("omega_0", "Natural frequency", "rad/s"),
        ("A", "Amplitude", "m"),
        ("phi", "Phase", "rad"),
    ),
    description="Fundamental oscillator model. Natural frequency ω₀ = √(k/m). "
                "Ubiquitous in physics: springs, pendula, atoms, circuits, fields.",
    derivation_steps=(
        "From Newton II and Hooke's law: ma = -kx",
        "m(d²x/dt²) = -kx",
        "d²x/dt² + (k/m)x = 0, define ω₀² = k/m",
        "Solution: x(t) = A cos(ω₀t + φ)",
    ),
    derives_from=("newton_second_law", "hooke_law"),
    leads_to=(
        "damped_oscillator",
        "quantum_harmonic_oscillator",
        "coupled_oscillators",
    ),
    discoverer="(classical mechanics)",
    year=1700,
    status=NodeStatus.PROVEN,
    tags=("oscillator", "periodic", "fundamental"),
)

# Period of SHM
shm_period = EquationNode(
    id="shm_period",
    name="Period of Simple Harmonic Motion",
    domain="classical_mechanics",
    latex=r"T = \frac{2\pi}{\omega_0} = 2\pi\sqrt{\frac{m}{k}}",
    sympy="T = 2 * pi * sqrt(m / k)",
    variables=(
        ("T", "Period", "s"),
        ("omega_0", "Angular frequency", "rad/s"),
        ("m", "Mass", "kg"),
        ("k", "Spring constant", "N/m"),
    ),
    description="Period is independent of amplitude (isochronism). "
                "Frequency f = 1/T = ω₀/(2π).",
    derivation_steps=(
        "Period is time for one cycle: ω₀T = 2π",
        "T = 2π/ω₀",
        "ω₀ = √(k/m), so T = 2π√(m/k)",
    ),
    derives_from=("harmonic_oscillator",),
    discoverer="Galileo Galilei (pendulum)",
    year=1602,
    status=NodeStatus.PROVEN,
    tags=("period", "frequency", "oscillator"),
)

# Simple Pendulum
simple_pendulum = EquationNode(
    id="simple_pendulum",
    name="Simple Pendulum",
    domain="classical_mechanics",
    latex=r"T = 2\pi\sqrt{\frac{L}{g}}",
    sympy="T = 2 * pi * sqrt(L / g)",
    variables=(
        ("T", "Period", "s"),
        ("L", "Pendulum length", "m"),
        ("g", "Gravitational acceleration", "m/s²"),
    ),
    description="Period of simple pendulum for small angles (θ < 15°). "
                "Independent of mass and amplitude (Galileo).",
    derivation_steps=(
        "Restoring force: F = -mg sin(θ) ≈ -mgθ (small angle)",
        "For arc length s = Lθ: F = -(mg/L)s",
        "Effective spring constant: k_eff = mg/L",
        "ω₀ = √(k/m) = √(g/L), T = 2π√(L/g)",
    ),
    assumptions=("Small angle approximation: θ ≪ 1 rad",),
    derives_from=("harmonic_oscillator",),
    discoverer="Galileo Galilei",
    year=1602,
    status=NodeStatus.APPROXIMATE,
    tags=("pendulum", "gravity", "timekeeping"),
)

# Damped Oscillator
damped_oscillator = EquationNode(
    id="damped_oscillator",
    name="Damped Harmonic Oscillator",
    domain="classical_mechanics",
    latex=r"\frac{d^2x}{dt^2} + 2\gamma\frac{dx}{dt} + \omega_0^2 x = 0",
    sympy="x = A * exp(-gamma * t) * cos(omega_d * t + phi)",
    variables=(
        ("x", "Displacement", "m"),
        ("gamma", "Damping coefficient", "s⁻¹"),
        ("omega_0", "Natural frequency", "rad/s"),
        ("omega_d", "Damped frequency", "rad/s"),
    ),
    description="Oscillator with energy dissipation. Three regimes: "
                "underdamped (γ < ω₀), critically damped (γ = ω₀), overdamped (γ > ω₀).",
    derivation_steps=(
        "Add damping force F_d = -bv = -b(dx/dt)",
        "Equation: m(d²x/dt²) + b(dx/dt) + kx = 0",
        "Define 2γ = b/m, ω₀² = k/m",
        "Solution depends on γ vs ω₀",
    ),
    derives_from=("harmonic_oscillator",),
    leads_to=("driven_oscillator", "q_factor"),
    discoverer="(mechanics)",
    year=1750,
    status=NodeStatus.PROVEN,
    tags=("damping", "dissipation", "oscillator"),
)

# Driven Oscillator
driven_oscillator = EquationNode(
    id="driven_oscillator",
    name="Driven Harmonic Oscillator",
    domain="classical_mechanics",
    latex=r"\frac{d^2x}{dt^2} + 2\gamma\frac{dx}{dt} + \omega_0^2 x = \frac{F_0}{m}\cos(\omega t)",
    sympy="x_steady = (F_0/m) / sqrt((omega_0**2 - omega**2)**2 + (2*gamma*omega)**2)",
    variables=(
        ("F_0", "Driving force amplitude", "N"),
        ("omega", "Driving frequency", "rad/s"),
    ),
    description="Damped oscillator with periodic driving force. "
                "Exhibits resonance when ω ≈ ω₀.",
    derivation_steps=(
        "Add driving force F(t) = F₀cos(ωt)",
        "Steady state: x(t) = A(ω)cos(ωt - δ)",
        "Amplitude A(ω) = (F₀/m)/√[(ω₀²-ω²)² + (2γω)²]",
        "Resonance peak near ω = ω₀",
    ),
    derives_from=("damped_oscillator",),
    leads_to=("resonance_condition",),
    discoverer="(mechanics)",
    year=1800,
    status=NodeStatus.PROVEN,
    tags=("driven", "resonance", "forced"),
)

# Export all nodes
NODES = [
    hooke_law,
    harmonic_oscillator,
    shm_period,
    simple_pendulum,
    damped_oscillator,
    driven_oscillator,
]
