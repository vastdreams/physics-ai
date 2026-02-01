"""
PATH: physics/knowledge/equations/thermodynamics/entropy.py
PURPOSE: Entropy and information theory equations
"""

from physics.knowledge.base import EquationNode

NODES = [
    # Boltzmann Entropy
    EquationNode(
        id="boltzmann_entropy",
        name="Boltzmann Entropy",
        description="Entropy in terms of number of microstates",
        latex=r"S = k_B \ln \Omega",
        sympy="S = k_B * ln(Omega)",
        variables=[
            ("S", "Entropy", "J/K"),
            ("k_B", "Boltzmann constant", "J/K"),
            ("Omega", "Number of microstates", "dimensionless"),
        ],
        domain="thermodynamics",
        tags=["entropy", "statistical", "fundamental"],
    ),
    
    # Gibbs Entropy
    EquationNode(
        id="gibbs_entropy",
        name="Gibbs Entropy",
        description="Entropy in terms of probability distribution",
        latex=r"S = -k_B \sum_i p_i \ln p_i",
        sympy="S = -k_B * sum(p_i * ln(p_i))",
        variables=[
            ("S", "Entropy", "J/K"),
            ("k_B", "Boltzmann constant", "J/K"),
            ("p_i", "Probability of microstate i", "dimensionless"),
        ],
        domain="thermodynamics",
        tags=["entropy", "statistical", "gibbs"],
    ),
    
    # Shannon Entropy
    EquationNode(
        id="shannon_entropy",
        name="Shannon Entropy",
        description="Information entropy in bits",
        latex=r"H = -\sum_i p_i \log_2 p_i",
        sympy="H = -sum(p_i * log2(p_i))",
        variables=[
            ("H", "Shannon entropy", "bits"),
            ("p_i", "Probability of state i", "dimensionless"),
        ],
        domain="thermodynamics",
        tags=["entropy", "information"],
    ),
    
    # Clausius Inequality
    EquationNode(
        id="clausius_inequality",
        name="Clausius Inequality",
        description="Entropy change is greater than or equal to heat over temperature",
        latex=r"dS \geq \frac{\delta Q}{T}",
        sympy="dS >= delta_Q / T",
        variables=[
            ("dS", "Change in entropy", "J/K"),
            ("delta_Q", "Heat transferred", "J"),
            ("T", "Temperature", "K"),
        ],
        domain="thermodynamics",
        tags=["entropy", "second_law"],
    ),
    
    # Entropy of Ideal Gas
    EquationNode(
        id="ideal_gas_entropy",
        name="Ideal Gas Entropy (Sackur-Tetrode)",
        description="Absolute entropy of monatomic ideal gas",
        latex=r"S = Nk_B\left[\ln\left(\frac{V}{N}\left(\frac{4\pi m U}{3Nh^2}\right)^{3/2}\right) + \frac{5}{2}\right]",
        sympy="S = N * k_B * (ln(V/N * (4*pi*m*U/(3*N*h**2))**(3/2)) + 5/2)",
        variables=[
            ("S", "Entropy", "J/K"),
            ("N", "Number of particles", "dimensionless"),
            ("k_B", "Boltzmann constant", "J/K"),
            ("V", "Volume", "m^3"),
            ("m", "Particle mass", "kg"),
            ("U", "Internal energy", "J"),
            ("h", "Planck constant", "J s"),
        ],
        domain="thermodynamics",
        tags=["entropy", "ideal_gas", "sackur_tetrode"],
    ),
    
    # Third Law (Nernst Theorem)
    EquationNode(
        id="third_law",
        name="Third Law of Thermodynamics",
        description="Entropy approaches constant as temperature approaches zero",
        latex=r"\lim_{T \to 0} S = 0",
        sympy="lim(S, T, 0) = 0",
        variables=[
            ("S", "Entropy", "J/K"),
            ("T", "Temperature", "K"),
        ],
        domain="thermodynamics",
        tags=["entropy", "third_law", "fundamental"],
    ),
    
    # Entropy Production
    EquationNode(
        id="entropy_production",
        name="Entropy Production Rate",
        description="Rate of entropy generation in irreversible process",
        latex=r"\dot{S}_{gen} = \frac{\dot{Q}}{T_{cold}} - \frac{\dot{Q}}{T_{hot}}",
        sympy="S_dot_gen = Q_dot / T_cold - Q_dot / T_hot",
        variables=[
            ("S_dot_gen", "Entropy production rate", "W/K"),
            ("Q_dot", "Heat transfer rate", "W"),
            ("T_cold", "Cold temperature", "K"),
            ("T_hot", "Hot temperature", "K"),
        ],
        domain="thermodynamics",
        tags=["entropy", "irreversible"],
    ),
    
    # Free Energy Minimum
    EquationNode(
        id="free_energy_minimum",
        name="Free Energy Minimum Principle",
        description="System at constant T,V minimizes Helmholtz free energy",
        latex=r"dF = dU - TdS \leq 0",
        sympy="dF = dU - T * dS <= 0",
        variables=[
            ("dF", "Change in Helmholtz free energy", "J"),
            ("dU", "Change in internal energy", "J"),
            ("T", "Temperature", "K"),
            ("dS", "Change in entropy", "J/K"),
        ],
        domain="thermodynamics",
        tags=["free_energy", "equilibrium"],
    ),
    
    # Gibbs Free Energy
    EquationNode(
        id="gibbs_free_energy",
        name="Gibbs Free Energy",
        description="Thermodynamic potential for constant T, P processes",
        latex=r"G = H - TS = U + PV - TS",
        sympy="G = H - T * S",
        variables=[
            ("G", "Gibbs free energy", "J"),
            ("H", "Enthalpy", "J"),
            ("T", "Temperature", "K"),
            ("S", "Entropy", "J/K"),
            ("U", "Internal energy", "J"),
            ("P", "Pressure", "Pa"),
            ("V", "Volume", "m^3"),
        ],
        domain="thermodynamics",
        tags=["free_energy", "gibbs"],
    ),
    
    # Chemical Potential
    EquationNode(
        id="chemical_potential",
        name="Chemical Potential",
        description="Change in Gibbs energy with particle number",
        latex=r"\mu = \left(\frac{\partial G}{\partial N}\right)_{T,P}",
        sympy="mu = dG/dN at constant T, P",
        variables=[
            ("mu", "Chemical potential", "J"),
            ("G", "Gibbs free energy", "J"),
            ("N", "Number of particles", "dimensionless"),
        ],
        domain="thermodynamics",
        tags=["chemical_potential", "gibbs"],
    ),
    
    # Maxwell Relations
    EquationNode(
        id="maxwell_relation_1",
        name="Maxwell Relation (S, V)",
        description="Relation between entropy and volume derivatives",
        latex=r"\left(\frac{\partial T}{\partial V}\right)_S = -\left(\frac{\partial P}{\partial S}\right)_V",
        sympy="dT/dV_S = -dP/dS_V",
        variables=[
            ("T", "Temperature", "K"),
            ("V", "Volume", "m^3"),
            ("P", "Pressure", "Pa"),
            ("S", "Entropy", "J/K"),
        ],
        domain="thermodynamics",
        tags=["maxwell", "thermodynamic_relations"],
    ),
    
    # Landauer's Principle
    EquationNode(
        id="landauer_principle",
        name="Landauer's Principle",
        description="Minimum energy to erase one bit of information",
        latex=r"E_{min} = k_B T \ln 2",
        sympy="E_min = k_B * T * ln(2)",
        variables=[
            ("E_min", "Minimum energy", "J"),
            ("k_B", "Boltzmann constant", "J/K"),
            ("T", "Temperature", "K"),
        ],
        domain="thermodynamics",
        tags=["information", "entropy", "computing"],
    ),
    
    # von Neumann Entropy
    EquationNode(
        id="von_neumann_entropy",
        name="von Neumann Entropy",
        description="Quantum mechanical entropy",
        latex=r"S = -k_B \text{Tr}(\rho \ln \rho)",
        sympy="S = -k_B * Tr(rho * ln(rho))",
        variables=[
            ("S", "von Neumann entropy", "J/K"),
            ("k_B", "Boltzmann constant", "J/K"),
            ("rho", "Density matrix", "dimensionless"),
        ],
        domain="thermodynamics",
        tags=["entropy", "quantum", "von_neumann"],
    ),
    
    # Entanglement Entropy
    EquationNode(
        id="entanglement_entropy",
        name="Entanglement Entropy",
        description="Entropy of reduced density matrix",
        latex=r"S_A = -\text{Tr}(\rho_A \ln \rho_A)",
        sympy="S_A = -Tr(rho_A * ln(rho_A))",
        variables=[
            ("S_A", "Entanglement entropy", "dimensionless"),
            ("rho_A", "Reduced density matrix", "dimensionless"),
        ],
        domain="thermodynamics",
        tags=["entropy", "quantum", "entanglement"],
    ),
    
    # Bekenstein-Hawking Entropy
    EquationNode(
        id="bekenstein_hawking_entropy",
        name="Bekenstein-Hawking Entropy",
        description="Black hole entropy proportional to horizon area",
        latex=r"S_{BH} = \frac{k_B c^3 A}{4 G \hbar}",
        sympy="S_BH = k_B * c**3 * A / (4 * G * hbar)",
        variables=[
            ("S_BH", "Black hole entropy", "J/K"),
            ("k_B", "Boltzmann constant", "J/K"),
            ("c", "Speed of light", "m/s"),
            ("A", "Horizon area", "m^2"),
            ("G", "Gravitational constant", "N m^2/kg^2"),
            ("hbar", "Reduced Planck constant", "J s"),
        ],
        domain="thermodynamics",
        tags=["entropy", "black_hole", "quantum_gravity"],
    ),
]
