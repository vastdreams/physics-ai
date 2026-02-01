"""
PATH: physics/knowledge/equations/nuclear/particle.py
PURPOSE: Particle physics - Standard Model, scattering, interactions
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Dirac Equation
dirac_equation = EquationNode(
    id="dirac_equation",
    name="Dirac Equation",
    domain="quantum_mechanics",
    latex=r"(i\gamma^\mu\partial_\mu - m)\psi = 0 \quad \text{or} \quad i\hbar\frac{\partial\psi}{\partial t} = (\vec{\alpha}\cdot\vec{p}c + \beta mc^2)\psi",
    sympy="(i*gamma_mu*d_mu - m)*psi = 0",
    variables=(("psi", "Dirac spinor", "m^(-3/2)"), ("gamma_mu", "Gamma matrices", "dimensionless"), ("m", "Mass", "kg")),
    description="Relativistic equation for spin-1/2 particles. Predicted antimatter.",
    derives_from=("schrodinger_time_dependent", "energy_momentum_relation"),
    uses=("hbar", "c"),
    status=NodeStatus.FUNDAMENTAL,
    tags=("relativistic", "spinor", "antimatter"),
)

# Klein-Gordon Equation
klein_gordon = EquationNode(
    id="klein_gordon",
    name="Klein-Gordon Equation",
    domain="quantum_mechanics",
    latex=r"(\partial_\mu\partial^\mu + m^2)\phi = 0 \quad \text{or} \quad \frac{1}{c^2}\frac{\partial^2\phi}{\partial t^2} - \nabla^2\phi + \frac{m^2c^2}{\hbar^2}\phi = 0",
    sympy="(d_mu*d^mu + m**2)*phi = 0",
    variables=(("phi", "Scalar field", "varies"), ("m", "Mass", "kg")),
    description="Relativistic wave equation for spin-0 particles (mesons).",
    derives_from=("energy_momentum_relation",),
    uses=("hbar", "c"),
    status=NodeStatus.FUNDAMENTAL,
    tags=("relativistic", "scalar"),
)

# Rutherford Scattering
rutherford_scattering = EquationNode(
    id="rutherford_scattering",
    name="Rutherford Scattering Formula",
    domain="nuclear_physics",
    latex=r"\frac{d\sigma}{d\Omega} = \left(\frac{Z_1 Z_2 e^2}{16\pi\epsilon_0 E}\right)^2 \frac{1}{\sin^4(\theta/2)}",
    sympy="dsigma/dOmega = (Z1*Z2*e**2/(16*pi*epsilon_0*E))**2 / sin(theta/2)**4",
    variables=(("dsigma/dOmega", "Differential cross section", "m²/sr"), ("Z1", "Projectile Z", "dimensionless"), ("Z2", "Target Z", "dimensionless"), ("E", "Kinetic energy", "J"), ("theta", "Scattering angle", "rad")),
    description="Classical Coulomb scattering. Discovered nucleus.",
    derives_from=("coulomb_law",),
    uses=("e", "epsilon_0"),
    status=NodeStatus.PROVEN,
    tags=("scattering", "coulomb"),
)

# Mandelstam Variables
mandelstam = EquationNode(
    id="mandelstam_variables",
    name="Mandelstam Variables",
    domain="particle_physics",
    latex=r"s = (p_1 + p_2)^2, \quad t = (p_1 - p_3)^2, \quad u = (p_1 - p_4)^2",
    sympy="s = (p1 + p2)**2",
    variables=(("s", "Center-of-mass energy squared", "GeV²"), ("t", "Momentum transfer squared", "GeV²"), ("u", "Cross momentum transfer", "GeV²")),
    description="Lorentz invariant kinematic variables. s + t + u = Σm².",
    status=NodeStatus.FUNDAMENTAL,
    tags=("kinematics", "invariant"),
)

# QED Vertex Factor
qed_vertex = EquationNode(
    id="qed_vertex",
    name="QED Vertex Factor",
    domain="particle_physics",
    latex=r"-ie\gamma^\mu",
    sympy="-i*e*gamma_mu",
    variables=(("e", "Elementary charge", "C"), ("gamma_mu", "Gamma matrix", "dimensionless")),
    description="Electron-photon coupling in Feynman diagrams.",
    uses=("e",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("qed", "feynman"),
)

# QED Running Coupling
running_coupling = EquationNode(
    id="running_coupling_qed",
    name="QED Running Coupling",
    domain="particle_physics",
    latex=r"\alpha(Q^2) = \frac{\alpha_0}{1 - \frac{\alpha_0}{3\pi}\ln(Q^2/m_e^2)}",
    sympy="alpha_Q = alpha_0/(1 - alpha_0/(3*pi)*ln(Q**2/m_e**2))",
    variables=(("alpha_Q", "Running coupling", "dimensionless"), ("alpha_0", "Fine structure constant", "dimensionless"), ("Q", "Momentum transfer", "GeV")),
    description="Effective coupling increases at high energy (screening).",
    uses=("alpha",),
    status=NodeStatus.PROVEN,
    tags=("qed", "renormalization"),
)

# QCD Running Coupling
running_coupling_qcd = EquationNode(
    id="running_coupling_qcd",
    name="QCD Running Coupling",
    domain="particle_physics",
    latex=r"\alpha_s(Q^2) = \frac{12\pi}{(33-2n_f)\ln(Q^2/\Lambda_{QCD}^2)}",
    sympy="alpha_s = 12*pi/((33-2*n_f)*ln(Q**2/Lambda_QCD**2))",
    variables=(("alpha_s", "Strong coupling", "dimensionless"), ("Q", "Momentum scale", "GeV"), ("n_f", "Number of quark flavors", "dimensionless"), ("Lambda_QCD", "QCD scale ~200 MeV", "GeV")),
    description="Asymptotic freedom: coupling decreases at high energy.",
    status=NodeStatus.PROVEN,
    tags=("qcd", "asymptotic_freedom"),
)

# Breit-Wigner Resonance
breit_wigner = EquationNode(
    id="breit_wigner",
    name="Breit-Wigner Resonance",
    domain="particle_physics",
    latex=r"\sigma(E) = \frac{g\pi}{k^2}\frac{\Gamma^2/4}{(E-E_0)^2 + \Gamma^2/4}",
    sympy="sigma = g*pi/k**2 * (Gamma**2/4)/((E-E_0)**2 + Gamma**2/4)",
    variables=(("sigma", "Cross section", "m²"), ("E_0", "Resonance energy", "J"), ("Gamma", "Width", "J"), ("g", "Statistical factor", "dimensionless")),
    description="Cross section near resonance. FWHM = Γ.",
    status=NodeStatus.PROVEN,
    tags=("resonance", "scattering"),
)

# CKM Matrix
ckm_matrix = EquationNode(
    id="ckm_matrix",
    name="CKM Matrix (Magnitude)",
    domain="particle_physics",
    latex=r"|V_{CKM}| \approx \begin{pmatrix} 0.97 & 0.22 & 0.004 \\ 0.22 & 0.97 & 0.04 \\ 0.008 & 0.04 & 1.0 \end{pmatrix}",
    sympy="V_CKM = [[0.97, 0.22, 0.004], [0.22, 0.97, 0.04], [0.008, 0.04, 1.0]]",
    variables=(("V_CKM", "CKM matrix elements", "dimensionless")),
    description="Quark mixing matrix. Off-diagonal elements allow flavor-changing weak decays.",
    status=NodeStatus.EXPERIMENTAL,
    tags=("weak", "mixing", "quarks"),
)

# Neutrino Oscillation
neutrino_oscillation = EquationNode(
    id="neutrino_oscillation",
    name="Neutrino Oscillation Probability",
    domain="particle_physics",
    latex=r"P(\nu_\alpha \to \nu_\beta) = \sin^2(2\theta)\sin^2\left(\frac{\Delta m^2 L}{4E}\right)",
    sympy="P = sin(2*theta)**2 * sin(delta_m2 * L / (4*E))**2",
    variables=(("P", "Oscillation probability", "dimensionless"), ("theta", "Mixing angle", "rad"), ("delta_m2", "Mass-squared difference", "eV²"), ("L", "Distance traveled", "m"), ("E", "Neutrino energy", "eV")),
    description="Two-flavor approximation. Proves neutrinos have mass.",
    status=NodeStatus.EXPERIMENTAL,
    tags=("neutrino", "oscillation", "mass"),
)

# Higgs Mechanism (Mass)
higgs_mass = EquationNode(
    id="higgs_mass_generation",
    name="Higgs Mass Generation",
    domain="particle_physics",
    latex=r"m_f = \frac{y_f v}{\sqrt{2}}, \quad m_W = \frac{gv}{2}, \quad m_Z = \frac{v\sqrt{g^2+g'^2}}{2}",
    sympy="m_f = y_f*v/sqrt(2)",
    variables=(("m_f", "Fermion mass", "GeV"), ("y_f", "Yukawa coupling", "dimensionless"), ("v", "Higgs VEV ~246 GeV", "GeV"), ("m_W", "W boson mass", "GeV"), ("m_Z", "Z boson mass", "GeV")),
    description="Masses from coupling to Higgs field. v = 246 GeV.",
    status=NodeStatus.PROVEN,
    tags=("higgs", "mass", "electroweak"),
)

# Decay Width (General)
decay_width = EquationNode(
    id="particle_decay_width",
    name="Particle Decay Width",
    domain="particle_physics",
    latex=r"\Gamma = \frac{\hbar}{\tau}, \quad \Delta E \cdot \tau \geq \hbar",
    sympy="Gamma = hbar/tau",
    variables=(("Gamma", "Decay width", "GeV"), ("tau", "Lifetime", "s"), ("hbar", "Reduced Planck constant", "J⋅s")),
    description="Width-lifetime relation. Short τ = broad resonance.",
    derives_from=("energy_time_uncertainty",),
    uses=("hbar",),
    status=NodeStatus.PROVEN,
    tags=("decay", "width"),
)

# PDG Naming Convention
particle_naming = EquationNode(
    id="particle_quantum_numbers",
    name="Particle Quantum Numbers",
    domain="particle_physics",
    latex=r"J^{PC}, \quad Q = I_3 + \frac{Y}{2}, \quad Y = B + S + C + B' + T",
    sympy="Q = I3 + Y/2",
    variables=(("J", "Total angular momentum", "dimensionless"), ("P", "Parity", "±1"), ("C", "Charge conjugation", "±1"), ("Q", "Charge", "dimensionless"), ("I3", "Isospin 3rd component", "dimensionless"), ("Y", "Hypercharge", "dimensionless")),
    description="Quantum numbers characterizing particles.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("quantum_numbers", "classification"),
)

NODES = [
    dirac_equation, klein_gordon, rutherford_scattering, mandelstam,
    qed_vertex, running_coupling, running_coupling_qcd, breit_wigner,
    ckm_matrix, neutrino_oscillation, higgs_mass, decay_width, particle_naming
]
