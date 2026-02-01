"""
PATH: physics/knowledge/equations/quantum/quantum_field.py
PURPOSE: Quantum Field Theory equations
"""

from physics.knowledge.base import EquationNode

NODES = [
    # Klein-Gordon Equation
    EquationNode(
        id="klein_gordon",
        name="Klein-Gordon Equation",
        description="Relativistic wave equation for spin-0 particles",
        latex=r"\left(\partial_\mu \partial^\mu + \frac{m^2c^2}{\hbar^2}\right)\phi = 0",
        sympy="(d2_phi/dt2 - c**2 * nabla2_phi) + (m*c/hbar)**2 * phi = 0",
        variables=[
            ("phi", "Scalar field", "varies"),
            ("m", "Mass", "kg"),
            ("c", "Speed of light", "m/s"),
            ("hbar", "Reduced Planck constant", "J s"),
        ],
        domain="quantum_mechanics",
        tags=["QFT", "relativistic", "scalar_field"],
    ),
    
    # Dirac Equation
    EquationNode(
        id="dirac_equation",
        name="Dirac Equation",
        description="Relativistic wave equation for spin-1/2 particles",
        latex=r"(i\hbar\gamma^\mu\partial_\mu - mc)\psi = 0",
        sympy="(i * hbar * gamma_mu * d_mu - m * c) * psi = 0",
        variables=[
            ("psi", "Dirac spinor", "varies"),
            ("gamma_mu", "Gamma matrices", "dimensionless"),
            ("m", "Mass", "kg"),
            ("c", "Speed of light", "m/s"),
            ("hbar", "Reduced Planck constant", "J s"),
        ],
        domain="quantum_mechanics",
        tags=["QFT", "relativistic", "spinor", "fermion"],
    ),
    
    # QED Lagrangian
    EquationNode(
        id="qed_lagrangian",
        name="QED Lagrangian",
        description="Lagrangian density for Quantum Electrodynamics",
        latex=r"\mathcal{L} = \bar{\psi}(i\gamma^\mu D_\mu - m)\psi - \frac{1}{4}F_{\mu\nu}F^{\mu\nu}",
        sympy="L = psi_bar * (i * gamma_mu * D_mu - m) * psi - F_munu * F^munu / 4",
        variables=[
            ("L", "Lagrangian density", "J/m^3"),
            ("psi", "Electron field", "varies"),
            ("D_mu", "Covariant derivative", "1/m"),
            ("F_munu", "EM field tensor", "V/m"),
            ("m", "Electron mass", "kg"),
        ],
        domain="quantum_mechanics",
        tags=["QFT", "QED", "lagrangian"],
    ),
    
    # Feynman Propagator (Scalar)
    EquationNode(
        id="feynman_propagator_scalar",
        name="Feynman Propagator (Scalar)",
        description="Propagator for scalar fields in momentum space",
        latex=r"D_F(p) = \frac{i}{p^2 - m^2c^2 + i\epsilon}",
        sympy="D_F = i / (p**2 - m**2 * c**2 + i * epsilon)",
        variables=[
            ("D_F", "Feynman propagator", "1/GeV^2"),
            ("p", "Four-momentum", "GeV/c"),
            ("m", "Mass", "GeV/c^2"),
            ("epsilon", "Infinitesimal", "GeV^2"),
        ],
        domain="quantum_mechanics",
        tags=["QFT", "propagator", "scalar"],
    ),
    
    # Fermion Propagator
    EquationNode(
        id="fermion_propagator",
        name="Fermion Propagator",
        description="Propagator for spin-1/2 fermions",
        latex=r"S_F(p) = \frac{i(\gamma^\mu p_\mu + mc)}{p^2 - m^2c^2 + i\epsilon}",
        sympy="S_F = i * (gamma_mu * p_mu + m * c) / (p**2 - m**2 * c**2 + i * epsilon)",
        variables=[
            ("S_F", "Fermion propagator", "varies"),
            ("p_mu", "Four-momentum", "GeV/c"),
            ("m", "Mass", "GeV/c^2"),
            ("gamma_mu", "Gamma matrices", "dimensionless"),
        ],
        domain="quantum_mechanics",
        tags=["QFT", "propagator", "fermion"],
    ),
    
    # Photon Propagator
    EquationNode(
        id="photon_propagator",
        name="Photon Propagator",
        description="Propagator for photons in Feynman gauge",
        latex=r"D^{\mu\nu}_F(k) = \frac{-ig^{\mu\nu}}{k^2 + i\epsilon}",
        sympy="D_F_munu = -i * g_munu / (k**2 + i * epsilon)",
        variables=[
            ("D_F_munu", "Photon propagator", "1/GeV^2"),
            ("g_munu", "Metric tensor", "dimensionless"),
            ("k", "Four-momentum", "GeV/c"),
        ],
        domain="quantum_mechanics",
        tags=["QFT", "propagator", "photon", "gauge"],
    ),
    
    # Running Coupling (QED)
    EquationNode(
        id="qed_running_coupling",
        name="QED Running Coupling",
        description="Energy dependence of fine structure constant",
        latex=r"\alpha(Q^2) = \frac{\alpha}{1 - \frac{\alpha}{3\pi}\ln\frac{Q^2}{m_e^2}}",
        sympy="alpha_Q = alpha / (1 - alpha / (3 * pi) * ln(Q**2 / m_e**2))",
        variables=[
            ("alpha_Q", "Running coupling", "dimensionless"),
            ("alpha", "Fine structure constant at Q=0", "dimensionless"),
            ("Q", "Momentum transfer", "GeV/c"),
            ("m_e", "Electron mass", "GeV/c^2"),
        ],
        domain="quantum_mechanics",
        tags=["QFT", "QED", "running_coupling"],
    ),
    
    # Vacuum Energy (Casimir Effect)
    EquationNode(
        id="casimir_force",
        name="Casimir Force",
        description="Force between parallel conducting plates due to vacuum fluctuations",
        latex=r"F = -\frac{\pi^2 \hbar c}{240 d^4} A",
        sympy="F = -pi**2 * hbar * c / (240 * d**4) * A",
        variables=[
            ("F", "Casimir force", "N"),
            ("hbar", "Reduced Planck constant", "J s"),
            ("c", "Speed of light", "m/s"),
            ("d", "Plate separation", "m"),
            ("A", "Plate area", "m^2"),
        ],
        domain="quantum_mechanics",
        tags=["QFT", "vacuum", "casimir"],
    ),
    
    # Lamb Shift
    EquationNode(
        id="lamb_shift",
        name="Lamb Shift",
        description="QED correction to hydrogen energy levels",
        latex=r"\Delta E_{Lamb} \approx \frac{\alpha^5 m_e c^2}{6\pi n^3}",
        sympy="Delta_E = alpha**5 * m_e * c**2 / (6 * pi * n**3)",
        variables=[
            ("Delta_E", "Energy shift", "J"),
            ("alpha", "Fine structure constant", "dimensionless"),
            ("m_e", "Electron mass", "kg"),
            ("c", "Speed of light", "m/s"),
            ("n", "Principal quantum number", "dimensionless"),
        ],
        domain="quantum_mechanics",
        tags=["QFT", "QED", "lamb_shift", "hydrogen"],
    ),
    
    # Anomalous Magnetic Moment
    EquationNode(
        id="anomalous_magnetic_moment",
        name="Anomalous Magnetic Moment",
        description="QED correction to electron g-factor",
        latex=r"a_e = \frac{g-2}{2} = \frac{\alpha}{2\pi} + \mathcal{O}(\alpha^2)",
        sympy="a_e = alpha / (2 * pi)",
        variables=[
            ("a_e", "Anomalous magnetic moment", "dimensionless"),
            ("g", "g-factor", "dimensionless"),
            ("alpha", "Fine structure constant", "dimensionless"),
        ],
        domain="quantum_mechanics",
        tags=["QFT", "QED", "g_factor"],
    ),
    
    # Second Quantization (Creation/Annihilation)
    EquationNode(
        id="creation_annihilation_commutator",
        name="Boson Creation/Annihilation Commutator",
        description="Commutation relation for bosonic field operators",
        latex=r"[a_k, a_{k'}^\dagger] = \delta_{kk'}",
        sympy="[a_k, a_k_dag] = delta_kk",
        variables=[
            ("a_k", "Annihilation operator", "dimensionless"),
            ("a_k_dag", "Creation operator", "dimensionless"),
            ("delta_kk", "Kronecker delta", "dimensionless"),
        ],
        domain="quantum_mechanics",
        tags=["QFT", "second_quantization", "boson"],
    ),
    
    # Fermion Anticommutator
    EquationNode(
        id="fermion_anticommutator",
        name="Fermion Anticommutation",
        description="Anticommutation relation for fermionic field operators",
        latex=r"\{c_k, c_{k'}^\dagger\} = \delta_{kk'}",
        sympy="{c_k, c_k_dag} = delta_kk",
        variables=[
            ("c_k", "Annihilation operator", "dimensionless"),
            ("c_k_dag", "Creation operator", "dimensionless"),
        ],
        domain="quantum_mechanics",
        tags=["QFT", "second_quantization", "fermion"],
    ),
    
    # Wick's Theorem
    EquationNode(
        id="wick_theorem",
        name="Wick's Theorem",
        description="Time-ordered products as sum of normal-ordered contractions",
        latex=r"T[\phi_1\phi_2\cdots\phi_n] = N[\phi_1\phi_2\cdots\phi_n + \text{all contractions}]",
        sympy="T[phi_1 * phi_2 * ... * phi_n] = N[sum of contractions]",
        variables=[
            ("T", "Time-ordering operator", "dimensionless"),
            ("N", "Normal-ordering operator", "dimensionless"),
            ("phi", "Field operators", "varies"),
        ],
        domain="quantum_mechanics",
        tags=["QFT", "wick", "perturbation"],
    ),
    
    # LSZ Reduction Formula
    EquationNode(
        id="lsz_reduction",
        name="LSZ Reduction Formula",
        description="Relates S-matrix elements to Green's functions",
        latex=r"\langle f|S|i\rangle = \prod_j (i\int d^4x_j e^{ip_j\cdot x_j}(\Box_j + m^2))\langle 0|T[\phi(x_1)\cdots]|0\rangle",
        sympy="S_fi = product of (i * integral * (Box + m**2)) * vacuum_expectation",
        variables=[
            ("S", "S-matrix element", "dimensionless"),
            ("phi", "Field", "varies"),
            ("m", "Mass", "kg"),
        ],
        domain="quantum_mechanics",
        tags=["QFT", "scattering", "S_matrix"],
    ),
    
    # Optical Theorem
    EquationNode(
        id="optical_theorem",
        name="Optical Theorem",
        description="Total cross section from forward scattering amplitude",
        latex=r"\sigma_{total} = \frac{4\pi}{k} \text{Im}[f(0)]",
        sympy="sigma_total = 4 * pi / k * Im(f_0)",
        variables=[
            ("sigma_total", "Total cross section", "m^2"),
            ("k", "Wave number", "1/m"),
            ("f_0", "Forward scattering amplitude", "m"),
        ],
        domain="quantum_mechanics",
        tags=["QFT", "scattering", "cross_section"],
    ),
]
