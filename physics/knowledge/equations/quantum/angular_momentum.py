"""
PATH: physics/knowledge/equations/quantum/angular_momentum.py
PURPOSE: Quantum angular momentum equations
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Angular Momentum Commutators
angular_commutator = EquationNode(
    id="angular_momentum_commutator",
    name="Angular Momentum Commutators",
    domain="quantum_mechanics",
    latex=r"[L_i, L_j] = i\hbar\epsilon_{ijk}L_k \quad \text{e.g., } [L_x, L_y] = i\hbar L_z",
    sympy="[L_x, L_y] = i*hbar*L_z",
    variables=(("L_i", "Angular momentum component", "J⋅s")),
    description="Fundamental commutation relations for angular momentum.",
    uses=("hbar",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("angular_momentum", "commutator"),
)

# L² and Lz Eigenvalues
angular_eigenvalues = EquationNode(
    id="angular_momentum_eigenvalues",
    name="Angular Momentum Eigenvalues",
    domain="quantum_mechanics",
    latex=r"L^2|l,m\rangle = \hbar^2 l(l+1)|l,m\rangle, \quad L_z|l,m\rangle = \hbar m|l,m\rangle",
    sympy="L2*|l,m> = hbar**2*l*(l+1)*|l,m>",
    variables=(("l", "Angular momentum quantum number", "0, 1, 2, ..."), ("m", "Magnetic quantum number", "-l to +l")),
    description="L² gives l(l+1)ℏ², Lz gives mℏ. m = -l, -l+1, ..., l-1, l.",
    derives_from=("angular_momentum_commutator",),
    uses=("hbar",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("angular_momentum", "eigenvalue"),
)

# Spin Angular Momentum
spin_half = EquationNode(
    id="spin_half_eigenvalues",
    name="Spin-1/2 Eigenvalues",
    domain="quantum_mechanics",
    latex=r"S^2|s,m_s\rangle = \frac{3}{4}\hbar^2|s,m_s\rangle, \quad S_z|s,m_s\rangle = \pm\frac{\hbar}{2}|s,m_s\rangle",
    sympy="S2*|1/2,ms> = (3/4)*hbar**2*|1/2,ms>",
    variables=(("s", "Spin quantum number = 1/2", "dimensionless"), ("m_s", "Spin projection = ±1/2", "dimensionless")),
    description="Electrons, protons, neutrons are spin-1/2 fermions.",
    derives_from=("angular_momentum_eigenvalues",),
    uses=("hbar",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("spin", "fermion"),
)

# Pauli Matrices
pauli_matrices = EquationNode(
    id="pauli_matrices",
    name="Pauli Matrices",
    domain="quantum_mechanics",
    latex=r"\sigma_x = \begin{pmatrix} 0 & 1 \\ 1 & 0 \end{pmatrix}, \sigma_y = \begin{pmatrix} 0 & -i \\ i & 0 \end{pmatrix}, \sigma_z = \begin{pmatrix} 1 & 0 \\ 0 & -1 \end{pmatrix}",
    sympy="sigma_x = [[0,1],[1,0]]",
    variables=(("sigma_i", "Pauli matrices", "dimensionless")),
    description="2×2 matrices for spin-1/2. S = ℏσ/2. Also used in SU(2), quantum computing.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("spin", "matrix"),
)

# Addition of Angular Momentum
angular_addition = EquationNode(
    id="angular_momentum_addition",
    name="Addition of Angular Momenta",
    domain="quantum_mechanics",
    latex=r"J = L + S, \quad |l-s| \leq j \leq l+s",
    sympy="J = L + S",
    variables=(("J", "Total angular momentum", "J⋅s"), ("L", "Orbital angular momentum", "J⋅s"), ("S", "Spin angular momentum", "J⋅s")),
    description="Total J ranges from |l-s| to l+s in integer steps.",
    derives_from=("angular_momentum_eigenvalues",),
    status=NodeStatus.PROVEN,
    tags=("angular_momentum", "addition"),
)

# Clebsch-Gordan Coefficients
clebsch_gordan = EquationNode(
    id="clebsch_gordan",
    name="Clebsch-Gordan Expansion",
    domain="quantum_mechanics",
    latex=r"|j,m\rangle = \sum_{m_1,m_2} C_{l_1 m_1 l_2 m_2}^{j m} |l_1,m_1\rangle|l_2,m_2\rangle",
    sympy="|j,m> = sum(C*|l1,m1>|l2,m2>)",
    variables=(("C", "Clebsch-Gordan coefficient", "dimensionless")),
    description="Coefficients for combining angular momenta into total J states.",
    derives_from=("angular_momentum_addition",),
    status=NodeStatus.PROVEN,
    tags=("angular_momentum", "coupling"),
)

# Wigner-Eckart Theorem
wigner_eckart = EquationNode(
    id="wigner_eckart",
    name="Wigner-Eckart Theorem",
    domain="quantum_mechanics",
    latex=r"\langle j'm'|T_q^{(k)}|jm\rangle = \frac{\langle j'||T^{(k)}||j\rangle}{\sqrt{2j'+1}} C_{jm kq}^{j'm'}",
    sympy="<j'm'|T|jm> ~ <j'||T||j>*C",
    variables=(("T_q", "Tensor operator", "varies")),
    description="Matrix elements of tensor operators factorize into reduced element × CG coefficient.",
    derives_from=("clebsch_gordan",),
    status=NodeStatus.PROVEN,
    tags=("tensor", "symmetry"),
)

# Spherical Harmonics
spherical_harmonics = EquationNode(
    id="spherical_harmonics",
    name="Spherical Harmonics",
    domain="quantum_mechanics",
    latex=r"Y_l^m(\theta,\phi) = \sqrt{\frac{2l+1}{4\pi}\frac{(l-m)!}{(l+m)!}} P_l^m(\cos\theta) e^{im\phi}",
    sympy="Y_lm = sqrt(...)*P_lm(cos(theta))*exp(i*m*phi)",
    variables=(("Y_lm", "Spherical harmonic", "dimensionless"), ("P_lm", "Associated Legendre polynomial", "dimensionless")),
    description="Angular part of orbital wave functions. Eigenfunctions of L², Lz.",
    derives_from=("angular_momentum_eigenvalues",),
    status=NodeStatus.PROVEN,
    tags=("angular_momentum", "eigenfunctions"),
)

# Selection Rules
selection_rules = EquationNode(
    id="selection_rules",
    name="Electric Dipole Selection Rules",
    domain="quantum_mechanics",
    latex=r"\Delta l = \pm 1, \quad \Delta m = 0, \pm 1, \quad \Delta s = 0",
    sympy="delta_l = +-1, delta_m = 0, +-1",
    variables=(),
    description="Rules for allowed electric dipole transitions.",
    derives_from=("wigner_eckart",),
    status=NodeStatus.PROVEN,
    tags=("transition", "selection"),
)

# Zeeman Effect
zeeman_effect = EquationNode(
    id="zeeman_effect",
    name="Zeeman Effect",
    domain="quantum_mechanics",
    latex=r"\Delta E = m_j g_J \mu_B B",
    sympy="delta_E = m_j*g_J*mu_B*B",
    variables=(("delta_E", "Energy shift", "J"), ("m_j", "Magnetic quantum number", "dimensionless"), ("g_J", "Landé g-factor", "dimensionless"), ("mu_B", "Bohr magneton", "J/T"), ("B", "Magnetic field", "T")),
    description="Energy level splitting in magnetic field.",
    derives_from=("angular_momentum_eigenvalues",),
    uses=("mu_B",),
    status=NodeStatus.EXPERIMENTAL,
    tags=("magnetic", "splitting"),
)

# Landé g-factor
lande_g = EquationNode(
    id="lande_g_factor",
    name="Landé g-factor",
    domain="quantum_mechanics",
    latex=r"g_J = 1 + \frac{J(J+1) + S(S+1) - L(L+1)}{2J(J+1)}",
    sympy="g_J = 1 + (J*(J+1) + S*(S+1) - L*(L+1))/(2*J*(J+1))",
    variables=(("g_J", "Landé g-factor", "dimensionless"), ("J", "Total angular momentum", "dimensionless"), ("S", "Spin", "dimensionless"), ("L", "Orbital", "dimensionless")),
    description="Effective g-factor for spin-orbit coupled state.",
    derives_from=("angular_addition",),
    status=NodeStatus.PROVEN,
    tags=("magnetic", "g_factor"),
)

NODES = [
    angular_commutator, angular_eigenvalues, spin_half, pauli_matrices,
    angular_addition, clebsch_gordan, wigner_eckart, spherical_harmonics,
    selection_rules, zeeman_effect, lande_g
]
