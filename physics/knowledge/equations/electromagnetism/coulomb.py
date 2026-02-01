"""
PATH: physics/knowledge/equations/electromagnetism/coulomb.py
PURPOSE: Electrostatic equations (Coulomb, electric potential, capacitance)
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Coulomb's Law
coulomb_law = EquationNode(
    id="coulomb_law",
    name="Coulomb's Law",
    domain="electromagnetism",
    latex=r"F = k_e\frac{q_1 q_2}{r^2} = \frac{1}{4\pi\varepsilon_0}\frac{q_1 q_2}{r^2}",
    sympy="F = k_e * q1 * q2 / r**2",
    variables=(
        ("F", "Force", "N"),
        ("k_e", "Coulomb constant", "N⋅m²/C²"),
        ("q1", "Charge 1", "C"),
        ("q2", "Charge 2", "C"),
        ("r", "Distance", "m"),
    ),
    description="Inverse-square law for electrostatic force. "
                "Like charges repel, opposites attract.",
    derives_from=("gauss_law_electric",),
    uses=("k_e", "epsilon_0"),
    discoverer="Charles-Augustin de Coulomb",
    year=1785,
    status=NodeStatus.PROVEN,
    tags=("electrostatics", "force", "inverse_square"),
)

# Electric Field
electric_field = EquationNode(
    id="electric_field",
    name="Electric Field",
    domain="electromagnetism",
    latex=r"\vec{E} = \frac{\vec{F}}{q} = k_e\frac{Q}{r^2}\hat{r}",
    sympy="E = k_e * Q / r**2",
    variables=(
        ("E", "Electric field", "V/m"),
        ("F", "Force on test charge", "N"),
        ("q", "Test charge", "C"),
        ("Q", "Source charge", "C"),
        ("r", "Distance", "m"),
    ),
    description="Force per unit charge. Field exists in space whether "
                "test charge present or not.",
    derives_from=("coulomb_law",),
    leads_to=("electric_potential",),
    discoverer="Michael Faraday",
    year=1832,
    status=NodeStatus.PROVEN,
    tags=("field", "electrostatics"),
)

# Electric Potential
electric_potential = EquationNode(
    id="electric_potential",
    name="Electric Potential",
    domain="electromagnetism",
    latex=r"V = k_e\frac{Q}{r} \quad \vec{E} = -\nabla V",
    sympy="V = k_e * Q / r",
    variables=(
        ("V", "Electric potential", "V"),
        ("Q", "Source charge", "C"),
        ("r", "Distance", "m"),
        ("E", "Electric field", "V/m"),
    ),
    description="Potential energy per unit charge. E is negative gradient of V. "
                "Scalar field simplifies many calculations.",
    derives_from=("electric_field",),
    uses=("k_e",),
    discoverer="Alessandro Volta",
    year=1800,
    status=NodeStatus.PROVEN,
    tags=("potential", "voltage", "scalar"),
)

# Capacitance
capacitance = EquationNode(
    id="capacitance",
    name="Capacitance",
    domain="electromagnetism",
    latex=r"C = \frac{Q}{V} \quad E_{stored} = \frac{1}{2}CV^2",
    sympy="C = Q / V",
    variables=(
        ("C", "Capacitance", "F"),
        ("Q", "Stored charge", "C"),
        ("V", "Voltage", "V"),
        ("E", "Stored energy", "J"),
    ),
    description="Charge storage ability. Depends on geometry and dielectric. "
                "Energy stored in electric field.",
    derives_from=("electric_potential",),
    discoverer="Michael Faraday",
    year=1836,
    status=NodeStatus.PROVEN,
    tags=("capacitor", "energy_storage"),
)

# Ohm's Law
ohm_law = EquationNode(
    id="ohm_law",
    name="Ohm's Law",
    domain="electromagnetism",
    latex=r"V = IR \quad \vec{J} = \sigma\vec{E}",
    sympy="V = I * R",
    variables=(
        ("V", "Voltage", "V"),
        ("I", "Current", "A"),
        ("R", "Resistance", "Ω"),
        ("J", "Current density", "A/m²"),
        ("sigma", "Conductivity", "S/m"),
    ),
    description="Linear relationship for ohmic materials. Microscopic form: J = σE. "
                "R depends on material and geometry.",
    discoverer="Georg Ohm",
    year=1827,
    status=NodeStatus.EMPIRICAL,
    tags=("circuits", "resistance", "conductivity"),
)

# Lorentz Force
lorentz_force = EquationNode(
    id="lorentz_force",
    name="Lorentz Force",
    domain="electromagnetism",
    latex=r"\vec{F} = q(\vec{E} + \vec{v} \times \vec{B})",
    sympy="F = q * (E + v cross B)",
    variables=(
        ("F", "Force", "N"),
        ("q", "Charge", "C"),
        ("E", "Electric field", "V/m"),
        ("v", "Velocity", "m/s"),
        ("B", "Magnetic field", "T"),
    ),
    description="Complete force on charged particle in EM field. "
                "Electric part does work, magnetic part deflects without doing work.",
    uses=("e",),
    leads_to=("cyclotron_frequency", "hall_effect"),
    discoverer="Hendrik Lorentz",
    year=1895,
    status=NodeStatus.FUNDAMENTAL,
    tags=("force", "motion", "deflection"),
)

# Export all nodes
NODES = [coulomb_law, electric_field, electric_potential, capacitance, ohm_law, lorentz_force]
