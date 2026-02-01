"""
PATH: physics/knowledge/equations/quantum/uncertainty.py
PURPOSE: Uncertainty relations and quantum limits
"""

from physics.knowledge.base.node import EquationNode, PrincipleNode, NodeStatus

# Heisenberg Uncertainty Principle
heisenberg = EquationNode(
    id="heisenberg_uncertainty",
    name="Heisenberg Uncertainty Principle",
    domain="quantum_mechanics",
    latex=r"\Delta x \cdot \Delta p \geq \frac{\hbar}{2}",
    sympy="delta_x * delta_p >= hbar / 2",
    variables=(
        ("delta_x", "Position uncertainty", "m"),
        ("delta_p", "Momentum uncertainty", "kg⋅m/s"),
        ("hbar", "Reduced Planck constant", "J⋅s"),
    ),
    description="Cannot simultaneously know position and momentum with "
                "arbitrary precision. Fundamental limit, not measurement error.",
    derivation_steps=(
        "From commutator [x, p] = iℏ",
        "General uncertainty: ΔA⋅ΔB ≥ |⟨[A,B]⟩|/2",
        "For x, p: ΔxΔp ≥ ℏ/2",
    ),
    uses=("hbar",),
    leads_to=("zero_point_energy", "quantum_tunneling"),
    discoverer="Werner Heisenberg",
    year=1927,
    status=NodeStatus.PROVEN,
    tags=("uncertainty", "fundamental_limit", "complementarity"),
)

# Energy-Time Uncertainty
energy_time = EquationNode(
    id="energy_time_uncertainty",
    name="Energy-Time Uncertainty",
    domain="quantum_mechanics",
    latex=r"\Delta E \cdot \Delta t \geq \frac{\hbar}{2}",
    sympy="delta_E * delta_t >= hbar / 2",
    variables=(
        ("delta_E", "Energy uncertainty", "J"),
        ("delta_t", "Time uncertainty", "s"),
        ("hbar", "Reduced Planck constant", "J⋅s"),
    ),
    description="Short-lived states have uncertain energies. "
                "Basis of virtual particles and spectral line widths.",
    uses=("hbar",),
    leads_to=("virtual_particles", "spectral_broadening"),
    discoverer="Werner Heisenberg",
    year=1927,
    status=NodeStatus.PROVEN,
    tags=("uncertainty", "lifetime", "spectroscopy"),
)

# Canonical Commutation Relation
commutation = EquationNode(
    id="canonical_commutation",
    name="Canonical Commutation Relation",
    domain="quantum_mechanics",
    latex=r"[\hat{x}, \hat{p}] = i\hbar",
    sympy="[x, p] = i * hbar",
    variables=(
        ("x", "Position operator", "m"),
        ("p", "Momentum operator", "kg⋅m/s"),
        ("hbar", "Reduced Planck constant", "J⋅s"),
    ),
    description="Position and momentum operators do not commute. "
                "Core structure of quantum mechanics. Implies uncertainty.",
    uses=("hbar",),
    leads_to=("heisenberg_uncertainty",),
    discoverer="Werner Heisenberg, Paul Dirac",
    year=1926,
    status=NodeStatus.FUNDAMENTAL,
    tags=("commutator", "operators", "algebra"),
)

# Superposition Principle
superposition = PrincipleNode(
    id="superposition_principle",
    name="Quantum Superposition Principle",
    domain="quantum_mechanics",
    statement="If |ψ₁⟩ and |ψ₂⟩ are valid states, then c₁|ψ₁⟩ + c₂|ψ₂⟩ "
              "is also a valid state for any complex coefficients.",
    mathematical_form=r"|\Psi\rangle = \sum_i c_i |\psi_i\rangle",
    description="Linear combinations of states are valid states. "
                "Basis of quantum interference and entanglement.",
    discoverer="(quantum mechanics)",
    year=1926,
    leads_to=("quantum_interference", "entanglement"),
    tags=("linearity", "superposition", "coherence"),
)

# Export all nodes
NODES = [heisenberg, energy_time, commutation, superposition]
