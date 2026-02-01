"""
PATH: physics/knowledge/equations/condensed/solid_state.py
PURPOSE: Solid state physics - band theory, semiconductors, lattice
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Bloch's Theorem
bloch_theorem = EquationNode(
    id="bloch_theorem",
    name="Bloch's Theorem",
    domain="condensed_matter",
    latex=r"\psi_{n\vec{k}}(\vec{r}) = e^{i\vec{k}\cdot\vec{r}} u_{n\vec{k}}(\vec{r})",
    sympy="psi_nk = exp(i*k*r) * u_nk(r)",
    variables=(("psi_nk", "Bloch wave function", "m^(-3/2)"), ("k", "Crystal momentum", "m⁻¹"), ("u_nk", "Periodic function", "m^(-3/2)")),
    description="Electrons in periodic potential have wave functions: plane wave × periodic part.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("band_theory", "periodic"),
)

# Free Electron Density of States
dos_free = EquationNode(
    id="dos_free_electron",
    name="Free Electron Density of States",
    domain="condensed_matter",
    latex=r"g(E) = \frac{V}{2\pi^2}\left(\frac{2m}{\hbar^2}\right)^{3/2}\sqrt{E}",
    sympy="g_E = V/(2*pi**2) * (2*m/hbar**2)**(3/2) * sqrt(E)",
    variables=(("g_E", "Density of states", "J⁻¹"), ("V", "Volume", "m³"), ("E", "Energy", "J")),
    description="Number of states per unit energy ∝ √E in 3D.",
    uses=("hbar",),
    status=NodeStatus.PROVEN,
    tags=("dos", "free_electron"),
)

# Fermi Energy
fermi_energy = EquationNode(
    id="fermi_energy",
    name="Fermi Energy",
    domain="condensed_matter",
    latex=r"E_F = \frac{\hbar^2}{2m}\left(\frac{3\pi^2 n}{}\right)^{2/3}",
    sympy="E_F = hbar**2/(2*m) * (3*pi**2*n)**(2/3)",
    variables=(("E_F", "Fermi energy", "J"), ("n", "Electron density", "m⁻³")),
    description="Highest occupied energy at T=0. For metals, E_F ~ few eV.",
    uses=("hbar",),
    status=NodeStatus.PROVEN,
    tags=("fermi", "metal"),
)

# Fermi-Dirac Distribution
fermi_dirac = EquationNode(
    id="fermi_dirac_distribution",
    name="Fermi-Dirac Distribution",
    domain="condensed_matter",
    latex=r"f(E) = \frac{1}{e^{(E-\mu)/k_B T} + 1}",
    sympy="f_E = 1/(exp((E - mu)/(k_B*T)) + 1)",
    variables=(("f_E", "Occupation probability", "dimensionless"), ("E", "Energy", "J"), ("mu", "Chemical potential", "J"), ("T", "Temperature", "K")),
    description="Probability of fermion state being occupied. Step function at T→0.",
    uses=("k_B",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("statistics", "fermion"),
)

# Bose-Einstein Distribution
bose_einstein = EquationNode(
    id="bose_einstein_distribution",
    name="Bose-Einstein Distribution",
    domain="condensed_matter",
    latex=r"n(E) = \frac{1}{e^{(E-\mu)/k_B T} - 1}",
    sympy="n_E = 1/(exp((E - mu)/(k_B*T)) - 1)",
    variables=(("n_E", "Mean occupation number", "dimensionless"), ("E", "Energy", "J"), ("mu", "Chemical potential", "J")),
    description="Boson occupation. For photons and phonons, μ=0.",
    uses=("k_B",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("statistics", "boson"),
)

# Drude Conductivity
drude_conductivity = EquationNode(
    id="drude_conductivity",
    name="Drude Conductivity",
    domain="condensed_matter",
    latex=r"\sigma = \frac{ne^2\tau}{m}",
    sympy="sigma = n*e**2*tau/m",
    variables=(("sigma", "Conductivity", "S/m"), ("n", "Carrier density", "m⁻³"), ("e", "Electron charge", "C"), ("tau", "Relaxation time", "s"), ("m", "Effective mass", "kg")),
    description="Classical model of conductivity. Basis of Ohm's law.",
    uses=("e",),
    status=NodeStatus.APPROXIMATE,
    tags=("conductivity", "drude"),
)

# Hall Effect
hall_effect = EquationNode(
    id="hall_effect",
    name="Hall Effect",
    domain="condensed_matter",
    latex=r"R_H = \frac{V_H}{I \cdot B/t} = \frac{1}{ne}",
    sympy="R_H = 1/(n*e)",
    variables=(("R_H", "Hall coefficient", "m³/C"), ("V_H", "Hall voltage", "V"), ("n", "Carrier density", "m⁻³"), ("B", "Magnetic field", "T")),
    description="Voltage perpendicular to current and B-field. Determines carrier sign and density.",
    uses=("e",),
    status=NodeStatus.PROVEN,
    tags=("hall", "transport"),
)

# Semiconductor Carrier Concentration
semiconductor_ni = EquationNode(
    id="intrinsic_carrier_concentration",
    name="Intrinsic Carrier Concentration",
    domain="condensed_matter",
    latex=r"n_i = \sqrt{N_c N_v} e^{-E_g/2k_BT}",
    sympy="n_i = sqrt(N_c*N_v)*exp(-E_g/(2*k_B*T))",
    variables=(("n_i", "Intrinsic concentration", "m⁻³"), ("N_c", "Conduction band DOS", "m⁻³"), ("N_v", "Valence band DOS", "m⁻³"), ("E_g", "Band gap", "J")),
    description="Carrier concentration in undoped semiconductor.",
    uses=("k_B",),
    status=NodeStatus.PROVEN,
    tags=("semiconductor", "intrinsic"),
)

# Mass Action Law
mass_action = EquationNode(
    id="mass_action_law_semi",
    name="Mass Action Law (Semiconductors)",
    domain="condensed_matter",
    latex=r"np = n_i^2",
    sympy="n*p = n_i**2",
    variables=(("n", "Electron concentration", "m⁻³"), ("p", "Hole concentration", "m⁻³"), ("n_i", "Intrinsic concentration", "m⁻³")),
    description="Product of carrier concentrations is constant at given T.",
    derives_from=("intrinsic_carrier_concentration",),
    status=NodeStatus.PROVEN,
    tags=("semiconductor"),
)

# Effective Mass
effective_mass = EquationNode(
    id="effective_mass",
    name="Effective Mass",
    domain="condensed_matter",
    latex=r"m^* = \hbar^2 \left(\frac{d^2 E}{dk^2}\right)^{-1}",
    sympy="m_star = hbar**2 / (d2E/dk2)",
    variables=(("m_star", "Effective mass", "kg"), ("E", "Band energy", "J"), ("k", "Wave vector", "m⁻¹")),
    description="Curvature of band determines how electrons respond to forces.",
    uses=("hbar",),
    status=NodeStatus.PROVEN,
    tags=("band_theory", "mass"),
)

# Debye Temperature
debye_temperature = EquationNode(
    id="debye_temperature",
    name="Debye Temperature",
    domain="condensed_matter",
    latex=r"\Theta_D = \frac{\hbar\omega_D}{k_B}",
    sympy="Theta_D = hbar*omega_D/k_B",
    variables=(("Theta_D", "Debye temperature", "K"), ("omega_D", "Debye cutoff frequency", "rad/s")),
    description="Characteristic temperature of lattice vibrations. Above Θ_D, classical behavior.",
    uses=("hbar", "k_B"),
    status=NodeStatus.PROVEN,
    tags=("debye", "phonon"),
)

# Debye Heat Capacity
debye_cv = EquationNode(
    id="debye_heat_capacity",
    name="Debye Heat Capacity",
    domain="condensed_matter",
    latex=r"C_V = 9Nk_B\left(\frac{T}{\Theta_D}\right)^3 \int_0^{\Theta_D/T} \frac{x^4 e^x}{(e^x-1)^2}dx",
    sympy="C_V = 9*N*k_B*(T/Theta_D)**3 * integral(...)",
    variables=(("C_V", "Heat capacity", "J/K"), ("N", "Number of atoms", "dimensionless"), ("Theta_D", "Debye temperature", "K")),
    description="Low T: C_V ∝ T³ (phonons). High T: C_V → 3Nk_B (classical).",
    derives_from=("debye_temperature",),
    uses=("k_B",),
    status=NodeStatus.PROVEN,
    tags=("heat_capacity", "phonon"),
)

# Wiedemann-Franz Law
wiedemann_franz = EquationNode(
    id="wiedemann_franz",
    name="Wiedemann-Franz Law",
    domain="condensed_matter",
    latex=r"\frac{\kappa}{\sigma T} = L = \frac{\pi^2 k_B^2}{3e^2} \approx 2.44 \times 10^{-8} \text{ W⋅Ω/K}^2",
    sympy="kappa/(sigma*T) = L",
    variables=(("kappa", "Thermal conductivity", "W/(m⋅K)"), ("sigma", "Electrical conductivity", "S/m"), ("L", "Lorenz number", "W⋅Ω/K²")),
    description="Ratio of thermal to electrical conductivity. Valid for metals.",
    uses=("k_B", "e"),
    status=NodeStatus.PROVEN,
    tags=("thermal", "transport"),
)

# Phonon Dispersion (Linear Chain)
phonon_dispersion = EquationNode(
    id="phonon_dispersion_linear",
    name="Phonon Dispersion (Monatomic Chain)",
    domain="condensed_matter",
    latex=r"\omega = 2\sqrt{\frac{K}{m}}\left|\sin\frac{ka}{2}\right|",
    sympy="omega = 2*sqrt(K/m)*|sin(k*a/2)|",
    variables=(("omega", "Phonon frequency", "rad/s"), ("K", "Spring constant", "N/m"), ("m", "Atom mass", "kg"), ("a", "Lattice constant", "m"), ("k", "Wave vector", "m⁻¹")),
    description="Dispersion relation for 1D monatomic chain.",
    status=NodeStatus.PROVEN,
    tags=("phonon", "dispersion"),
)

# Bragg's Law
bragg_law = EquationNode(
    id="bragg_law",
    name="Bragg's Law",
    domain="condensed_matter",
    latex=r"2d\sin\theta = n\lambda",
    sympy="2*d*sin(theta) = n*lambda",
    variables=(("d", "Lattice plane spacing", "m"), ("theta", "Incidence angle", "rad"), ("n", "Order", "dimensionless"), ("lambda", "Wavelength", "m")),
    description="Constructive interference condition for crystal diffraction.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("diffraction", "crystal"),
)

NODES = [
    bloch_theorem, dos_free, fermi_energy, fermi_dirac, bose_einstein,
    drude_conductivity, hall_effect, semiconductor_ni, mass_action, effective_mass,
    debye_temperature, debye_cv, wiedemann_franz, phonon_dispersion, bragg_law
]
