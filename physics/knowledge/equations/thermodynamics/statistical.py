"""
PATH: physics/knowledge/equations/thermodynamics/statistical.py
PURPOSE: Statistical mechanics equations
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Boltzmann Distribution
boltzmann_distribution = EquationNode(
    id="boltzmann_distribution",
    name="Boltzmann Distribution",
    domain="statistical_mechanics",
    latex=r"P_i = \frac{e^{-E_i/k_BT}}{Z} \quad Z = \sum_i e^{-E_i/k_BT}",
    sympy="P_i = exp(-E_i / (k_B * T)) / Z",
    variables=(
        ("P_i", "Probability of state i", "(dimensionless)"),
        ("E_i", "Energy of state i", "J"),
        ("k_B", "Boltzmann constant", "J/K"),
        ("T", "Temperature", "K"),
        ("Z", "Partition function", "(dimensionless)"),
    ),
    description="Probability of microstate at thermal equilibrium. "
                "Foundation of statistical mechanics.",
    uses=("k_B",),
    leads_to=("partition_function", "free_energy_statistical"),
    discoverer="Ludwig Boltzmann",
    year=1877,
    status=NodeStatus.FUNDAMENTAL,
    tags=("probability", "equilibrium", "exponential"),
)

# Partition Function
partition_function = EquationNode(
    id="partition_function",
    name="Partition Function",
    domain="statistical_mechanics",
    latex=r"Z = \sum_i e^{-E_i/k_BT} \quad F = -k_BT\ln Z",
    sympy="Z = sum(exp(-E_i / (k_B * T)))",
    variables=(
        ("Z", "Partition function", "(dimensionless)"),
        ("E_i", "Energy of state i", "J"),
        ("F", "Helmholtz free energy", "J"),
    ),
    description="Central quantity in statistical mechanics. "
                "All thermodynamic quantities derivable from Z.",
    derives_from=("boltzmann_distribution",),
    uses=("k_B",),
    leads_to=("average_energy", "entropy_from_partition"),
    discoverer="J. Willard Gibbs",
    year=1902,
    status=NodeStatus.FUNDAMENTAL,
    tags=("partition", "generating_function"),
)

# Statistical Entropy
statistical_entropy = EquationNode(
    id="statistical_entropy",
    name="Boltzmann Entropy",
    domain="statistical_mechanics",
    latex=r"S = k_B \ln \Omega",
    sympy="S = k_B * ln(Omega)",
    variables=(
        ("S", "Entropy", "J/K"),
        ("k_B", "Boltzmann constant", "J/K"),
        ("Omega", "Number of microstates", "(dimensionless)"),
    ),
    description="Microscopic definition of entropy. "
                "Carved on Boltzmann's tombstone.",
    derives_from=("entropy_definition",),
    uses=("k_B",),
    discoverer="Ludwig Boltzmann",
    year=1877,
    status=NodeStatus.FUNDAMENTAL,
    tags=("entropy", "microstates", "famous"),
)

# Gibbs Entropy
gibbs_entropy = EquationNode(
    id="gibbs_entropy",
    name="Gibbs Entropy",
    domain="statistical_mechanics",
    latex=r"S = -k_B \sum_i P_i \ln P_i",
    sympy="S = -k_B * sum(P_i * ln(P_i))",
    variables=(
        ("S", "Entropy", "J/K"),
        ("k_B", "Boltzmann constant", "J/K"),
        ("P_i", "Probability of state i", "(dimensionless)"),
    ),
    description="General entropy formula. Reduces to Boltzmann for equal probabilities. "
                "Foundation of information theory (Shannon entropy).",
    derives_from=("statistical_entropy",),
    uses=("k_B",),
    leads_to=("shannon_entropy", "maximum_entropy"),
    discoverer="J. Willard Gibbs",
    year=1902,
    status=NodeStatus.FUNDAMENTAL,
    tags=("entropy", "probability", "information"),
)

# Equipartition Theorem
equipartition = EquationNode(
    id="equipartition_theorem",
    name="Equipartition Theorem",
    domain="statistical_mechanics",
    latex=r"\langle E \rangle = \frac{1}{2}k_BT \text{ per quadratic degree of freedom}",
    sympy="E_avg = (1/2) * k_B * T * f",
    variables=(
        ("E_avg", "Average energy", "J"),
        ("k_B", "Boltzmann constant", "J/K"),
        ("T", "Temperature", "K"),
        ("f", "Degrees of freedom", "(dimensionless)"),
    ),
    description="Each quadratic term in energy contributes (1/2)kT. "
                "Explains ideal gas heat capacity. Fails at low T (quantum).",
    derives_from=("boltzmann_distribution",),
    uses=("k_B",),
    conditions=("Classical limit, kT >> energy level spacing",),
    discoverer="James Clerk Maxwell, Ludwig Boltzmann",
    year=1860,
    status=NodeStatus.APPROXIMATE,
    tags=("classical", "heat_capacity", "degrees_of_freedom"),
)

# Maxwell-Boltzmann Distribution
maxwell_boltzmann = EquationNode(
    id="maxwell_boltzmann_distribution",
    name="Maxwell-Boltzmann Speed Distribution",
    domain="statistical_mechanics",
    latex=r"f(v) = 4\pi n \left(\frac{m}{2\pi k_BT}\right)^{3/2} v^2 e^{-mv^2/2k_BT}",
    sympy="f_v = 4*pi*n * (m/(2*pi*k_B*T))**(3/2) * v**2 * exp(-m*v**2/(2*k_B*T))",
    variables=(
        ("f_v", "Speed distribution", "s/m"),
        ("v", "Speed", "m/s"),
        ("n", "Number density", "m⁻³"),
        ("m", "Particle mass", "kg"),
        ("T", "Temperature", "K"),
    ),
    description="Distribution of molecular speeds in ideal gas. "
                "Most probable speed: v_p = √(2kT/m).",
    derives_from=("boltzmann_distribution",),
    uses=("k_B",),
    discoverer="James Clerk Maxwell",
    year=1860,
    status=NodeStatus.PROVEN,
    tags=("distribution", "kinetic_theory", "gas"),
)

# Export all nodes
NODES = [
    boltzmann_distribution,
    partition_function,
    statistical_entropy,
    gibbs_entropy,
    equipartition,
    maxwell_boltzmann,
]
