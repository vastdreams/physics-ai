"""
PATH: physics/knowledge/equations/quantum/hydrogen.py
PURPOSE: Hydrogen atom and atomic physics equations
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Hydrogen Energy Levels
hydrogen_energy = EquationNode(
    id="hydrogen_energy_levels",
    name="Hydrogen Energy Levels",
    domain="quantum_mechanics",
    latex=r"E_n = -\frac{m_e e^4}{32\pi^2\epsilon_0^2\hbar^2 n^2} = -\frac{13.6 \text{ eV}}{n^2}",
    sympy="E_n = -13.6*eV/n**2",
    variables=(("E_n", "Energy of level n", "J"), ("n", "Principal quantum number", "1, 2, 3, ...")),
    description="Bohr formula for hydrogen energy levels. Exact in non-relativistic QM.",
    uses=("m_e", "e", "epsilon_0", "hbar"),
    status=NodeStatus.FUNDAMENTAL,
    tags=("hydrogen", "energy"),
)

# Bohr Radius
bohr_radius = EquationNode(
    id="bohr_radius",
    name="Bohr Radius",
    domain="quantum_mechanics",
    latex=r"a_0 = \frac{4\pi\epsilon_0\hbar^2}{m_e e^2} = 0.529 \text{ Å}",
    sympy="a_0 = 4*pi*epsilon_0*hbar**2/(m_e*e**2)",
    variables=(("a_0", "Bohr radius", "m")),
    description="Characteristic length scale for hydrogen atom.",
    uses=("epsilon_0", "hbar", "m_e", "e"),
    status=NodeStatus.FUNDAMENTAL,
    tags=("hydrogen", "length"),
)

# Hydrogen Wave Functions
hydrogen_wavefunction = EquationNode(
    id="hydrogen_wave_function",
    name="Hydrogen Wave Functions",
    domain="quantum_mechanics",
    latex=r"\psi_{nlm} = R_{nl}(r)Y_l^m(\theta,\phi)",
    sympy="psi_nlm = R_nl*Y_lm",
    variables=(("R_nl", "Radial wave function", "m^(-3/2)"), ("Y_lm", "Spherical harmonic", "dimensionless"), ("n", "Principal QN", "1,2,3,..."), ("l", "Orbital QN", "0,1,...,n-1"), ("m", "Magnetic QN", "-l,...,+l")),
    description="Separable in spherical coordinates. Degeneracy: 2n² (with spin).",
    status=NodeStatus.FUNDAMENTAL,
    tags=("hydrogen", "wavefunction"),
)

# Ground State Wave Function
hydrogen_1s = EquationNode(
    id="hydrogen_1s",
    name="Hydrogen Ground State (1s)",
    domain="quantum_mechanics",
    latex=r"\psi_{1s} = \frac{1}{\sqrt{\pi}a_0^{3/2}}e^{-r/a_0}",
    sympy="psi_1s = 1/(sqrt(pi)*a_0**(3/2))*exp(-r/a_0)",
    variables=(("psi_1s", "1s wave function", "m^(-3/2)"), ("a_0", "Bohr radius", "m")),
    description="Ground state of hydrogen. Maximum probability at r = a₀.",
    derives_from=("hydrogen_wave_function", "bohr_radius"),
    status=NodeStatus.PROVEN,
    tags=("hydrogen", "ground_state"),
)

# Rydberg Constant
rydberg_constant = EquationNode(
    id="rydberg_constant",
    name="Rydberg Constant",
    domain="quantum_mechanics",
    latex=r"R_\infty = \frac{m_e e^4}{8\epsilon_0^2 h^3 c} = 1.097 \times 10^7 \text{ m}^{-1}",
    sympy="R_inf = m_e*e**4/(8*epsilon_0**2*h**3*c)",
    variables=(("R_inf", "Rydberg constant", "m⁻¹")),
    description="Determines atomic spectra wavelengths. Rydberg energy = hcR∞ = 13.6 eV.",
    uses=("m_e", "e", "epsilon_0", "h", "c"),
    status=NodeStatus.FUNDAMENTAL,
    tags=("hydrogen", "spectroscopy"),
)

# Rydberg Formula
rydberg_formula = EquationNode(
    id="rydberg_formula",
    name="Rydberg Formula",
    domain="quantum_mechanics",
    latex=r"\frac{1}{\lambda} = R_\infty\left(\frac{1}{n_f^2} - \frac{1}{n_i^2}\right)",
    sympy="1/lambda = R_inf*(1/n_f**2 - 1/n_i**2)",
    variables=(("lambda", "Wavelength", "m"), ("n_i", "Initial level", "dimensionless"), ("n_f", "Final level", "dimensionless")),
    description="Wavelengths of hydrogen spectral lines. Lyman (nf=1), Balmer (nf=2), etc.",
    derives_from=("rydberg_constant",),
    status=NodeStatus.PROVEN,
    tags=("hydrogen", "spectroscopy"),
)

# Spin-Orbit Coupling
spin_orbit = EquationNode(
    id="spin_orbit_coupling",
    name="Spin-Orbit Coupling",
    domain="quantum_mechanics",
    latex=r"H_{SO} = \frac{1}{2m_e^2c^2}\frac{1}{r}\frac{dV}{dr}\vec{L}\cdot\vec{S}",
    sympy="H_SO = 1/(2*m_e**2*c**2) * 1/r * dV/dr * L dot S",
    variables=(("H_SO", "Spin-orbit Hamiltonian", "J")),
    description="Magnetic interaction between orbital and spin moments. Splits levels by j.",
    uses=("m_e", "c"),
    status=NodeStatus.PROVEN,
    tags=("fine_structure", "spin_orbit"),
)

# Thomas Precession Factor
thomas_precession = EquationNode(
    id="thomas_precession",
    name="Thomas Precession Factor",
    domain="quantum_mechanics",
    latex=r"\text{Thomas factor} = \frac{1}{2}",
    sympy="thomas_factor = 1/2",
    variables=(),
    description="Relativistic correction reducing spin-orbit by factor of 2.",
    status=NodeStatus.PROVEN,
    tags=("spin_orbit", "relativistic"),
)

# Hydrogen-like Atoms
hydrogen_like = EquationNode(
    id="hydrogen_like_scaling",
    name="Hydrogen-like Atom Scaling",
    domain="quantum_mechanics",
    latex=r"E_n = -\frac{Z^2 \cdot 13.6 \text{ eV}}{n^2}, \quad a = \frac{a_0}{Z}",
    sympy="E_n = -Z**2 * 13.6*eV / n**2",
    variables=(("Z", "Nuclear charge", "dimensionless")),
    description="Energy scales as Z². Size scales as 1/Z.",
    derives_from=("hydrogen_energy_levels", "bohr_radius"),
    status=NodeStatus.PROVEN,
    tags=("hydrogen_like", "scaling"),
)

# Multi-electron Atoms
shielding = EquationNode(
    id="shielding_effect",
    name="Shielding Effect",
    domain="quantum_mechanics",
    latex=r"E_n \approx -\frac{(Z-\sigma)^2 \cdot 13.6 \text{ eV}}{n^2}",
    sympy="E_n ~ -(Z-sigma)**2 * 13.6*eV / n**2",
    variables=(("sigma", "Shielding constant", "dimensionless")),
    description="Inner electrons shield nuclear charge. σ depends on n, l (Slater's rules).",
    derives_from=("hydrogen_like_scaling",),
    status=NodeStatus.APPROXIMATE,
    tags=("multi_electron", "shielding"),
)

# Aufbau Principle
aufbau = EquationNode(
    id="aufbau_principle",
    name="Aufbau Principle (n+l rule)",
    domain="quantum_mechanics",
    latex=r"\text{Fill orbitals in order of increasing } n + l",
    sympy="fill by n+l",
    variables=(),
    description="Orbital filling order: 1s, 2s, 2p, 3s, 3p, 4s, 3d, 4p, 5s, ...",
    status=NodeStatus.EMPIRICAL,
    tags=("electronic_structure", "filling"),
)

# Hund's Rules
hunds_rules = EquationNode(
    id="hunds_rules",
    name="Hund's Rules",
    domain="quantum_mechanics",
    latex=r"1.\; S_{max} \quad 2.\; L_{max} \quad 3.\; J = |L-S| \text{ (less than half full)}",
    sympy="S = max, then L = max",
    variables=(),
    description="Ground state term. Maximize S, then L, then J depends on filling.",
    status=NodeStatus.EMPIRICAL,
    tags=("electronic_structure", "ground_state"),
)

NODES = [
    hydrogen_energy, bohr_radius, hydrogen_wavefunction, hydrogen_1s, rydberg_constant,
    rydberg_formula, spin_orbit, thomas_precession, hydrogen_like, shielding, aufbau, hunds_rules
]
