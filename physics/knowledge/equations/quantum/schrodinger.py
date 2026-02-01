"""
PATH: physics/knowledge/equations/quantum/schrodinger.py
PURPOSE: Schrödinger equation and quantum wave mechanics

FIRST PRINCIPLES:
Quantum mechanics postulates: state = wave function, observables = operators,
measurement = eigenvalues. The Schrödinger equation is the dynamical law
(analog of Newton's second law).
"""

from physics.knowledge.base.node import EquationNode, PrincipleNode, NodeStatus

# Time-Dependent Schrödinger Equation
schrodinger_td = EquationNode(
    id="schrodinger_time_dependent",
    name="Time-Dependent Schrödinger Equation",
    domain="quantum_mechanics",
    latex=r"i\hbar\frac{\partial \Psi}{\partial t} = \hat{H}\Psi = \left[-\frac{\hbar^2}{2m}\nabla^2 + V(\vec{r})\right]\Psi",
    sympy="i * hbar * dPsi/dt = H * Psi",
    variables=(
        ("Psi", "Wave function", "m^(-3/2)"),
        ("H", "Hamiltonian operator", "J"),
        ("hbar", "Reduced Planck constant", "J⋅s"),
        ("m", "Mass", "kg"),
        ("V", "Potential energy", "J"),
    ),
    description="Fundamental equation of quantum mechanics. Determines "
                "time evolution of quantum states. Linear, deterministic for |Ψ|.",
    uses=("hbar",),
    leads_to=(
        "schrodinger_time_independent",
        "quantum_harmonic_oscillator",
        "hydrogen_atom_qm",
    ),
    discoverer="Erwin Schrödinger",
    year=1926,
    status=NodeStatus.FUNDAMENTAL,
    tags=("dynamics", "wave_function", "evolution"),
)

# Time-Independent Schrödinger Equation
schrodinger_ti = EquationNode(
    id="schrodinger_time_independent",
    name="Time-Independent Schrödinger Equation",
    domain="quantum_mechanics",
    latex=r"\hat{H}\psi = E\psi \quad \left[-\frac{\hbar^2}{2m}\nabla^2 + V\right]\psi = E\psi",
    sympy="H * psi = E * psi",
    variables=(
        ("psi", "Spatial wave function", "m^(-3/2)"),
        ("E", "Energy eigenvalue", "J"),
        ("H", "Hamiltonian", "J"),
    ),
    description="Eigenvalue equation for energy. Solutions are stationary states. "
                "Separable when H is time-independent.",
    derivation_steps=(
        "Assume Ψ(r,t) = ψ(r)φ(t) (separation of variables)",
        "Substitute into time-dependent equation",
        "Get φ(t) = exp(-iEt/ℏ) and Hψ = Eψ",
    ),
    derives_from=("schrodinger_time_dependent",),
    uses=("hbar",),
    discoverer="Erwin Schrödinger",
    year=1926,
    status=NodeStatus.PROVEN,
    tags=("eigenvalue", "stationary_state", "energy"),
)

# Planck-Einstein Relation
planck_einstein = EquationNode(
    id="planck_einstein_relation",
    name="Planck-Einstein Relation",
    domain="quantum_mechanics",
    latex=r"E = h\nu = \hbar\omega",
    sympy="E = h * nu",
    variables=(
        ("E", "Energy", "J"),
        ("h", "Planck constant", "J⋅s"),
        ("nu", "Frequency", "Hz"),
        ("hbar", "Reduced Planck constant", "J⋅s"),
        ("omega", "Angular frequency", "rad/s"),
    ),
    description="Energy of a quantum is proportional to frequency. "
                "Foundation of quantum theory (Planck for blackbody, Einstein for photoelectric).",
    uses=("h", "hbar"),
    leads_to=("photoelectric_effect", "schrodinger_time_dependent"),
    discoverer="Max Planck, Albert Einstein",
    year=1905,
    status=NodeStatus.FUNDAMENTAL,
    tags=("quantization", "photon", "energy"),
)

# de Broglie Relation
de_broglie = EquationNode(
    id="de_broglie_relation",
    name="de Broglie Relation",
    domain="quantum_mechanics",
    latex=r"\lambda = \frac{h}{p} = \frac{h}{mv}",
    sympy="lambda = h / p",
    variables=(
        ("lambda", "de Broglie wavelength", "m"),
        ("h", "Planck constant", "J⋅s"),
        ("p", "Momentum", "kg⋅m/s"),
        ("m", "Mass", "kg"),
        ("v", "Velocity", "m/s"),
    ),
    description="Matter has wave properties. Wavelength inversely proportional "
                "to momentum. Basis for electron microscopy, diffraction.",
    uses=("h",),
    leads_to=("schrodinger_time_dependent",),
    discoverer="Louis de Broglie",
    year=1924,
    status=NodeStatus.EXPERIMENTAL,
    tags=("wave-particle", "matter_waves"),
)

# Born Rule
born_rule = PrincipleNode(
    id="born_rule",
    name="Born Rule",
    domain="quantum_mechanics",
    statement="The probability density of finding a particle at position r "
              "is given by |Ψ(r,t)|².",
    mathematical_form=r"P(\vec{r},t) = |\Psi(\vec{r},t)|^2",
    description="Connects wave function to physical measurement. |Ψ|² is "
                "probability density, not the particle itself.",
    discoverer="Max Born",
    year=1926,
    leads_to=("normalization_condition",),
    tags=("probability", "measurement", "interpretation"),
)

# Normalization Condition
normalization = EquationNode(
    id="normalization_condition",
    name="Normalization Condition",
    domain="quantum_mechanics",
    latex=r"\int_{-\infty}^{\infty} |\Psi|^2 d^3r = 1",
    sympy="integral(|Psi|**2, r) = 1",
    variables=(
        ("Psi", "Wave function", "m^(-3/2)"),
    ),
    description="Total probability of finding particle somewhere must be 1. "
                "Constrains allowed wave functions.",
    derives_from=("born_rule",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("probability", "normalization"),
)

# Quantum Harmonic Oscillator
qho = EquationNode(
    id="quantum_harmonic_oscillator",
    name="Quantum Harmonic Oscillator",
    domain="quantum_mechanics",
    latex=r"E_n = \hbar\omega\left(n + \frac{1}{2}\right) \quad n = 0, 1, 2, ...",
    sympy="E_n = hbar * omega * (n + 1/2)",
    variables=(
        ("E_n", "Energy level", "J"),
        ("hbar", "Reduced Planck constant", "J⋅s"),
        ("omega", "Angular frequency", "rad/s"),
        ("n", "Quantum number", "(dimensionless)"),
    ),
    description="Quantized energy levels equally spaced. Zero-point energy E₀ = ℏω/2. "
                "Model for molecular vibrations, photons, phonons.",
    derivation_steps=(
        "Hamiltonian: H = p²/(2m) + (1/2)mω²x²",
        "Solve eigenvalue problem using ladder operators",
        "Get E_n = ℏω(n + 1/2)",
    ),
    derives_from=("schrodinger_time_independent", "harmonic_oscillator"),
    uses=("hbar",),
    leads_to=("creation_annihilation_operators", "phonon_theory"),
    discoverer="(quantum mechanics)",
    year=1926,
    status=NodeStatus.PROVEN,
    tags=("oscillator", "quantization", "model"),
)

# Export all nodes
NODES = [
    schrodinger_td,
    schrodinger_ti,
    planck_einstein,
    de_broglie,
    born_rule,
    normalization,
    qho,
]
