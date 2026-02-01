"""
PATH: physics/knowledge/equations/thermodynamics/laws.py
PURPOSE: Laws of thermodynamics

FIRST PRINCIPLES:
The laws of thermodynamics govern energy, heat, and entropy.
They emerge from statistical mechanics but were discovered
empirically and stand as fundamental principles.
"""

from physics.knowledge.base.node import EquationNode, PrincipleNode, NodeStatus

# Zeroth Law
zeroth_law = PrincipleNode(
    id="zeroth_law",
    name="Zeroth Law of Thermodynamics",
    domain="thermodynamics",
    statement="If A is in thermal equilibrium with B, and B is in thermal "
              "equilibrium with C, then A is in equilibrium with C.",
    mathematical_form="T_A = T_B and T_B = T_C implies T_A = T_C",
    description="Defines temperature. Allows construction of thermometers. "
                "Equivalence relation for thermal equilibrium.",
    discoverer="Ralph Fowler",
    year=1931,
    leads_to=("temperature_definition",),
    tags=("equilibrium", "temperature", "foundation"),
)

# First Law
first_law = EquationNode(
    id="first_law",
    name="First Law of Thermodynamics",
    domain="thermodynamics",
    latex=r"dU = \delta Q - \delta W \quad \Delta U = Q - W",
    sympy="dU = Q - W",
    variables=(
        ("U", "Internal energy", "J"),
        ("Q", "Heat added to system", "J"),
        ("W", "Work done by system", "J"),
    ),
    description="Energy conservation. Energy can change form but total is conserved. "
                "Heat and work are path-dependent, U is state function.",
    leads_to=("enthalpy_definition", "heat_capacity"),
    discoverer="Julius Robert von Mayer, James Joule",
    year=1843,
    status=NodeStatus.FUNDAMENTAL,
    tags=("energy_conservation", "heat", "work"),
)

# Second Law (Clausius)
second_law_clausius = PrincipleNode(
    id="second_law_clausius",
    name="Second Law (Clausius Statement)",
    domain="thermodynamics",
    statement="Heat cannot spontaneously flow from a colder body to a hotter body.",
    mathematical_form="dS >= delta_Q / T",
    description="Irreversibility of natural processes. "
                "Entropy of isolated system never decreases.",
    discoverer="Rudolf Clausius",
    year=1850,
    leads_to=("entropy_definition", "carnot_efficiency"),
    tags=("entropy", "irreversibility", "direction"),
)

# Entropy
entropy = EquationNode(
    id="entropy_definition",
    name="Entropy",
    domain="thermodynamics",
    latex=r"dS = \frac{\delta Q_{rev}}{T} \quad S = k_B \ln \Omega",
    sympy="dS = Q_rev / T",
    variables=(
        ("S", "Entropy", "J/K"),
        ("Q_rev", "Reversible heat", "J"),
        ("T", "Temperature", "K"),
        ("k_B", "Boltzmann constant", "J/K"),
        ("Omega", "Number of microstates", "(dimensionless)"),
    ),
    description="Measure of disorder/uncertainty. Clausius (macroscopic) and "
                "Boltzmann (microscopic) definitions are equivalent.",
    derives_from=("second_law_clausius",),
    uses=("k_B",),
    leads_to=("gibbs_free_energy", "statistical_entropy"),
    discoverer="Rudolf Clausius, Ludwig Boltzmann",
    year=1865,
    status=NodeStatus.FUNDAMENTAL,
    tags=("entropy", "disorder", "state_function"),
)

# Third Law
third_law = PrincipleNode(
    id="third_law",
    name="Third Law of Thermodynamics",
    domain="thermodynamics",
    statement="The entropy of a perfect crystal at absolute zero is exactly zero.",
    mathematical_form="lim_{T->0} S = 0",
    description="Establishes absolute entropy scale. "
                "Implies absolute zero is unattainable in finite steps.",
    discoverer="Walther Nernst",
    year=1906,
    tags=("entropy", "absolute_zero", "limit"),
)

# Ideal Gas Law
ideal_gas = EquationNode(
    id="ideal_gas_law",
    name="Ideal Gas Law",
    domain="thermodynamics",
    latex=r"PV = nRT = Nk_BT",
    sympy="P * V = n * R * T",
    variables=(
        ("P", "Pressure", "Pa"),
        ("V", "Volume", "m³"),
        ("n", "Number of moles", "mol"),
        ("R", "Gas constant", "J/(mol⋅K)"),
        ("N", "Number of particles", "(dimensionless)"),
        ("k_B", "Boltzmann constant", "J/K"),
        ("T", "Temperature", "K"),
    ),
    description="Equation of state for ideal gas. Derived from kinetic theory. "
                "Valid at low pressure, high temperature.",
    uses=("R", "k_B"),
    leads_to=("kinetic_theory", "thermodynamic_processes"),
    discoverer="Émile Clapeyron",
    year=1834,
    status=NodeStatus.APPROXIMATE,
    tags=("gas", "equation_of_state"),
)

# Carnot Efficiency
carnot = EquationNode(
    id="carnot_efficiency",
    name="Carnot Efficiency",
    domain="thermodynamics",
    latex=r"\eta_{Carnot} = 1 - \frac{T_C}{T_H}",
    sympy="eta = 1 - T_C / T_H",
    variables=(
        ("eta", "Efficiency", "(dimensionless)"),
        ("T_C", "Cold reservoir temperature", "K"),
        ("T_H", "Hot reservoir temperature", "K"),
    ),
    description="Maximum efficiency of heat engine operating between two temperatures. "
                "No real engine can exceed this.",
    derives_from=("second_law_clausius",),
    discoverer="Sadi Carnot",
    year=1824,
    status=NodeStatus.PROVEN,
    tags=("efficiency", "engine", "limit"),
)

# Heat Capacity
heat_capacity = EquationNode(
    id="heat_capacity",
    name="Heat Capacity",
    domain="thermodynamics",
    latex=r"C = \frac{\delta Q}{dT} \quad C_V = \left(\frac{\partial U}{\partial T}\right)_V \quad C_P = \left(\frac{\partial H}{\partial T}\right)_P",
    sympy="C = Q / dT",
    variables=(
        ("C", "Heat capacity", "J/K"),
        ("C_V", "Heat capacity at constant V", "J/K"),
        ("C_P", "Heat capacity at constant P", "J/K"),
        ("U", "Internal energy", "J"),
        ("H", "Enthalpy", "J"),
        ("T", "Temperature", "K"),
    ),
    description="Heat needed to raise temperature by 1K. "
                "C_P - C_V = nR for ideal gas.",
    derives_from=("first_law",),
    discoverer="Joseph Black",
    year=1760,
    status=NodeStatus.PROVEN,
    tags=("heat", "temperature", "specific"),
)

# Export all nodes
NODES = [
    zeroth_law,
    first_law,
    second_law_clausius,
    entropy,
    third_law,
    ideal_gas,
    carnot,
    heat_capacity,
]
