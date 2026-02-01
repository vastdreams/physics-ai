"""
PATH: physics/knowledge/equations/quantum/many_body.py
PURPOSE: Many-body quantum mechanics and second quantization
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Slater Determinant
slater = EquationNode(
    id="slater_determinant",
    name="Slater Determinant",
    domain="quantum_mechanics",
    latex=r"\Psi(r_1,...,r_N) = \frac{1}{\sqrt{N!}}\begin{vmatrix} \phi_1(r_1) & ... & \phi_N(r_1) \\ \vdots & \ddots & \vdots \\ \phi_1(r_N) & ... & \phi_N(r_N) \end{vmatrix}",
    sympy="Psi = (1/sqrt(N!))*det(phi)",
    variables=(("Psi", "Many-body wave function", "m^(-3N/2)"), ("phi_i", "Single-particle orbital", "m^(-3/2)")),
    description="Antisymmetric wave function for N fermions. Satisfies Pauli exclusion.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("fermion", "antisymmetric"),
)

# Pauli Exclusion Principle
pauli_exclusion = EquationNode(
    id="pauli_exclusion",
    name="Pauli Exclusion Principle",
    domain="quantum_mechanics",
    latex=r"\Psi(..., r_i, ..., r_j, ...) = -\Psi(..., r_j, ..., r_i, ...)",
    sympy="Psi(i, j) = -Psi(j, i)",
    variables=(),
    description="No two fermions can occupy same quantum state. From spin-statistics.",
    derives_from=("slater_determinant",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("fermion", "exclusion"),
)

# Creation/Annihilation Operators
creation_annihilation = EquationNode(
    id="creation_annihilation",
    name="Creation/Annihilation Operators",
    domain="quantum_mechanics",
    latex=r"a^\dagger|n\rangle = \sqrt{n+1}|n+1\rangle, \quad a|n\rangle = \sqrt{n}|n-1\rangle",
    sympy="a_dagger*|n> = sqrt(n+1)*|n+1>",
    variables=(("a", "Annihilation operator", "dimensionless"), ("a_dagger", "Creation operator", "dimensionless"), ("n", "Occupation number", "dimensionless")),
    description="Ladder operators for harmonic oscillator / bosons.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("second_quantization", "boson"),
)

# Boson Commutation
boson_commutation = EquationNode(
    id="boson_commutation",
    name="Boson Commutation Relations",
    domain="quantum_mechanics",
    latex=r"[a_i, a_j^\dagger] = \delta_{ij}, \quad [a_i, a_j] = [a_i^\dagger, a_j^\dagger] = 0",
    sympy="[a, a_dagger] = 1",
    variables=(),
    description="Canonical commutation for bosonic operators.",
    derives_from=("creation_annihilation",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("commutation", "boson"),
)

# Fermion Anticommutation
fermion_anticommutation = EquationNode(
    id="fermion_anticommutation",
    name="Fermion Anticommutation Relations",
    domain="quantum_mechanics",
    latex=r"\{c_i, c_j^\dagger\} = \delta_{ij}, \quad \{c_i, c_j\} = \{c_i^\dagger, c_j^\dagger\} = 0",
    sympy="{c, c_dagger} = 1",
    variables=(("c", "Fermion annihilation", "dimensionless"), ("c_dagger", "Fermion creation", "dimensionless")),
    description="Anticommutation ensures Pauli exclusion.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("anticommutation", "fermion"),
)

# Number Operator
number_operator = EquationNode(
    id="number_operator",
    name="Number Operator",
    domain="quantum_mechanics",
    latex=r"\hat{n} = a^\dagger a, \quad \hat{n}|n\rangle = n|n\rangle",
    sympy="n_hat = a_dagger * a",
    variables=(("n_hat", "Number operator", "dimensionless")),
    description="Counts particles in state. Eigenvalue is occupation number.",
    derives_from=("creation_annihilation",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("number", "operator"),
)

# Field Operator
field_operator = EquationNode(
    id="field_operator",
    name="Field Operator",
    domain="quantum_mechanics",
    latex=r"\hat{\psi}(\vec{r}) = \sum_k \phi_k(\vec{r}) a_k",
    sympy="psi_hat = sum(phi_k*a_k)",
    variables=(("psi_hat", "Field operator", "m^(-3/2)"), ("phi_k", "Single-particle basis", "m^(-3/2)"), ("a_k", "Annihilation operator", "dimensionless")),
    description="Annihilates particle at position r. Second quantization of wave function.",
    derives_from=("creation_annihilation",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("field", "second_quantization"),
)

# Hartree-Fock
hartree_fock = EquationNode(
    id="hartree_fock",
    name="Hartree-Fock Equation",
    domain="quantum_mechanics",
    latex=r"\left[\hat{h} + V_H + V_X\right]\phi_i = \epsilon_i\phi_i",
    sympy="(h_hat + V_H + V_X)*phi_i = epsilon_i*phi_i",
    variables=(("h", "Single-particle Hamiltonian", "J"), ("V_H", "Hartree (direct) potential", "J"), ("V_X", "Exchange potential", "J")),
    description="Self-consistent mean-field for many electrons. Includes exchange, ignores correlation.",
    derives_from=("slater_determinant",),
    status=NodeStatus.APPROXIMATE,
    tags=("mean_field", "many_body"),
)

# Exchange Energy
exchange_energy = EquationNode(
    id="exchange_energy",
    name="Exchange Energy",
    domain="quantum_mechanics",
    latex=r"E_X = -\frac{1}{2}\sum_{ij}\int\int \frac{\phi_i^*(r)\phi_j^*(r')\phi_j(r)\phi_i(r')}{|r-r'|}d^3r d^3r'",
    sympy="E_X = -(1/2)*sum(integral(...))",
    variables=(("E_X", "Exchange energy", "J")),
    description="Purely quantum effect from antisymmetry. Lowers energy for parallel spins.",
    derives_from=("hartree_fock",),
    status=NodeStatus.PROVEN,
    tags=("exchange", "correlation"),
)

# Density Functional Theory
dft = EquationNode(
    id="density_functional",
    name="Kohn-Sham DFT Equation",
    domain="quantum_mechanics",
    latex=r"\left[-\frac{\hbar^2}{2m}\nabla^2 + V_{eff}[n]\right]\phi_i = \epsilon_i\phi_i",
    sympy="(-hbar**2/(2*m)*laplacian + V_eff)*phi_i = epsilon_i*phi_i",
    variables=(("V_eff", "Effective potential", "J"), ("n", "Electron density", "m⁻³")),
    description="Exact ground state from density alone (Hohenberg-Kohn). Exchange-correlation functional approximated.",
    uses=("hbar",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("dft", "electronic_structure"),
)

# Hubbard Model
hubbard = EquationNode(
    id="hubbard_model",
    name="Hubbard Model",
    domain="quantum_mechanics",
    latex=r"H = -t\sum_{\langle i,j\rangle,\sigma}(c_{i\sigma}^\dagger c_{j\sigma} + h.c.) + U\sum_i n_{i\uparrow}n_{i\downarrow}",
    sympy="H = -t*sum(c_dagger*c + h.c.) + U*sum(n_up*n_down)",
    variables=(("t", "Hopping integral", "J"), ("U", "On-site repulsion", "J")),
    description="Minimal model for strongly correlated electrons. Describes Mott insulators.",
    status=NodeStatus.THEORETICAL,
    tags=("hubbard", "correlation"),
)

# BCS Ground State
bcs_ground_state = EquationNode(
    id="bcs_ground_state",
    name="BCS Ground State",
    domain="quantum_mechanics",
    latex=r"|\Psi_{BCS}\rangle = \prod_k (u_k + v_k c_{k\uparrow}^\dagger c_{-k\downarrow}^\dagger)|0\rangle",
    sympy="|Psi_BCS> = prod(u_k + v_k*c_up_dagger*c_down_dagger)*|0>",
    variables=(("u_k", "BCS amplitude", "dimensionless"), ("v_k", "BCS amplitude", "dimensionless")),
    description="Coherent state of Cooper pairs. |v_k|² is pair occupation probability.",
    status=NodeStatus.PROVEN,
    tags=("bcs", "superconductivity"),
)

NODES = [
    slater, pauli_exclusion, creation_annihilation, boson_commutation, fermion_anticommutation,
    number_operator, field_operator, hartree_fock, exchange_energy, dft, hubbard, bcs_ground_state
]
