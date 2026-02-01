"""
PATH: physics/knowledge/equations/electromagnetism/maxwell.py
PURPOSE: Maxwell's equations - the foundation of electromagnetism

FIRST PRINCIPLES:
Maxwell's equations unify electricity, magnetism, and optics.
They predict electromagnetic waves propagating at speed c,
which identified light as electromagnetic radiation.
"""

from physics.knowledge.base.node import EquationNode, PrincipleNode, NodeStatus

# Gauss's Law for Electricity
gauss_electric = EquationNode(
    id="gauss_law_electric",
    name="Gauss's Law for Electricity",
    domain="electromagnetism",
    latex=r"\nabla \cdot \vec{E} = \frac{\rho}{\varepsilon_0} \quad \oint \vec{E} \cdot d\vec{A} = \frac{Q_{enc}}{\varepsilon_0}",
    sympy="div(E) = rho / epsilon_0",
    variables=(
        ("E", "Electric field", "V/m"),
        ("rho", "Charge density", "C/m³"),
        ("epsilon_0", "Vacuum permittivity", "F/m"),
        ("Q_enc", "Enclosed charge", "C"),
    ),
    description="Electric flux through closed surface equals enclosed charge / ε₀. "
                "Sources of E-field are electric charges.",
    derivation_steps=(
        "From Coulomb's law, integrate contributions from all charges",
        "For point charge: flux = q/ε₀ through any enclosing surface",
        "Generalize to charge distributions",
        "Differential form via divergence theorem",
    ),
    uses=("epsilon_0",),
    leads_to=("coulomb_law",),
    discoverer="Carl Friedrich Gauss",
    year=1835,
    status=NodeStatus.FUNDAMENTAL,
    tags=("maxwell", "divergence", "charge"),
)

# Gauss's Law for Magnetism
gauss_magnetic = EquationNode(
    id="gauss_law_magnetic",
    name="Gauss's Law for Magnetism",
    domain="electromagnetism",
    latex=r"\nabla \cdot \vec{B} = 0 \quad \oint \vec{B} \cdot d\vec{A} = 0",
    sympy="div(B) = 0",
    variables=(
        ("B", "Magnetic field", "T"),
    ),
    description="Magnetic monopoles do not exist. Magnetic field lines form "
                "closed loops. No magnetic 'charges'.",
    discoverer="(observation)",
    year=1835,
    status=NodeStatus.EXPERIMENTAL,
    tags=("maxwell", "divergence", "monopole"),
)

# Faraday's Law
faraday_law = EquationNode(
    id="faraday_law",
    name="Faraday's Law of Induction",
    domain="electromagnetism",
    latex=r"\nabla \times \vec{E} = -\frac{\partial \vec{B}}{\partial t} \quad \oint \vec{E} \cdot d\vec{l} = -\frac{d\Phi_B}{dt}",
    sympy="curl(E) = -dB/dt",
    variables=(
        ("E", "Electric field", "V/m"),
        ("B", "Magnetic field", "T"),
        ("Phi_B", "Magnetic flux", "Wb"),
    ),
    description="Changing magnetic field induces electric field. "
                "Basis of electrical generators and transformers.",
    derivation_steps=(
        "Faraday's experiments: EMF induced by changing flux",
        "EMF = -dΦ_B/dt (Lenz's law gives sign)",
        "EMF = ∮E⋅dl = -d(∫B⋅dA)/dt",
        "Stokes' theorem gives differential form",
    ),
    leads_to=("electromagnetic_induction", "em_wave_equation"),
    discoverer="Michael Faraday",
    year=1831,
    status=NodeStatus.EXPERIMENTAL,
    tags=("maxwell", "induction", "curl"),
)

# Ampère-Maxwell Law
ampere_maxwell = EquationNode(
    id="ampere_maxwell_law",
    name="Ampère-Maxwell Law",
    domain="electromagnetism",
    latex=r"\nabla \times \vec{B} = \mu_0\vec{J} + \mu_0\varepsilon_0\frac{\partial \vec{E}}{\partial t}",
    sympy="curl(B) = mu_0 * J + mu_0 * epsilon_0 * dE/dt",
    variables=(
        ("B", "Magnetic field", "T"),
        ("J", "Current density", "A/m²"),
        ("E", "Electric field", "V/m"),
        ("mu_0", "Vacuum permeability", "H/m"),
        ("epsilon_0", "Vacuum permittivity", "F/m"),
    ),
    description="Magnetic field produced by currents AND changing electric field. "
                "Maxwell's displacement current term completes the equations.",
    derivation_steps=(
        "Ampère's original: ∇×B = μ₀J",
        "Maxwell added: displacement current J_d = ε₀∂E/∂t",
        "Needed for charge conservation: ∇⋅J + ∂ρ/∂t = 0",
        "Enables electromagnetic wave solutions",
    ),
    uses=("mu_0", "epsilon_0"),
    leads_to=("em_wave_equation",),
    discoverer="André-Marie Ampère, James Clerk Maxwell",
    year=1865,
    status=NodeStatus.FUNDAMENTAL,
    tags=("maxwell", "displacement_current", "curl"),
)

# Electromagnetic Wave Equation
em_wave = EquationNode(
    id="em_wave_equation",
    name="Electromagnetic Wave Equation",
    domain="electromagnetism",
    latex=r"\nabla^2\vec{E} = \mu_0\varepsilon_0\frac{\partial^2\vec{E}}{\partial t^2} = \frac{1}{c^2}\frac{\partial^2\vec{E}}{\partial t^2}",
    sympy="del2(E) = (1/c**2) * d2E/dt2",
    variables=(
        ("E", "Electric field", "V/m"),
        ("c", "Speed of light", "m/s"),
    ),
    description="EM waves propagate at c = 1/√(μ₀ε₀). Maxwell's prediction that "
                "unified electromagnetism with optics.",
    derivation_steps=(
        "Take curl of Faraday's law: ∇×(∇×E) = -∂(∇×B)/∂t",
        "Use vector identity: ∇×(∇×E) = ∇(∇⋅E) - ∇²E",
        "In vacuum ∇⋅E = 0 and ∇×B = μ₀ε₀∂E/∂t",
        "Get wave equation with c² = 1/(μ₀ε₀)",
    ),
    derives_from=("faraday_law", "ampere_maxwell_law"),
    uses=("c", "mu_0", "epsilon_0"),
    leads_to=("light_speed_em", "electromagnetic_spectrum"),
    discoverer="James Clerk Maxwell",
    year=1865,
    status=NodeStatus.PROVEN,
    tags=("waves", "light", "propagation"),
)

# Export all nodes
NODES = [gauss_electric, gauss_magnetic, faraday_law, ampere_maxwell, em_wave]
