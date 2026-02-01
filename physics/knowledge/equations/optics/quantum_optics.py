"""
PATH: physics/knowledge/equations/optics/quantum_optics.py
PURPOSE: Quantum optics and photon physics
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Photon Energy
photon_energy = EquationNode(
    id="photon_energy",
    name="Photon Energy",
    domain="quantum_mechanics",
    latex=r"E = h\nu = \frac{hc}{\lambda} = \hbar\omega",
    sympy="E = h*nu = h*c/lambda",
    variables=(("E", "Photon energy", "J"), ("h", "Planck constant", "J⋅s"), ("nu", "Frequency", "Hz"), ("lambda", "Wavelength", "m")),
    description="Energy of single photon. Foundation of quantum optics.",
    derives_from=("planck_einstein_relation",),
    uses=("h", "c"),
    status=NodeStatus.FUNDAMENTAL,
    tags=("photon", "quantum"),
)

# Photon Momentum
photon_momentum = EquationNode(
    id="photon_momentum",
    name="Photon Momentum",
    domain="quantum_mechanics",
    latex=r"p = \frac{h}{\lambda} = \frac{E}{c} = \hbar k",
    sympy="p = h/lambda",
    variables=(("p", "Photon momentum", "kg⋅m/s"), ("h", "Planck constant", "J⋅s"), ("lambda", "Wavelength", "m"), ("k", "Wave number", "m⁻¹")),
    description="Momentum of massless photon. E = pc.",
    derives_from=("de_broglie_relation",),
    uses=("h",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("photon", "momentum"),
)

# Photoelectric Effect
photoelectric = EquationNode(
    id="photoelectric_effect",
    name="Photoelectric Effect",
    domain="quantum_mechanics",
    latex=r"KE_{max} = h\nu - \phi = h\nu - h\nu_0",
    sympy="KE_max = h*nu - phi",
    variables=(("KE_max", "Max kinetic energy", "J"), ("h", "Planck constant", "J⋅s"), ("nu", "Light frequency", "Hz"), ("phi", "Work function", "J"), ("nu_0", "Threshold frequency", "Hz")),
    description="Einstein's explanation: one photon ejects one electron.",
    uses=("h",),
    status=NodeStatus.EXPERIMENTAL,
    tags=("photoelectric", "quantum"),
)

# Compton Scattering
compton_scattering = EquationNode(
    id="compton_scattering",
    name="Compton Scattering",
    domain="quantum_mechanics",
    latex=r"\Delta\lambda = \frac{h}{m_e c}(1 - \cos\theta) = \lambda_C(1-\cos\theta)",
    sympy="delta_lambda = (h/(m_e*c))*(1 - cos(theta))",
    variables=(("delta_lambda", "Wavelength shift", "m"), ("h", "Planck constant", "J⋅s"), ("m_e", "Electron mass", "kg"), ("theta", "Scattering angle", "rad"), ("lambda_C", "Compton wavelength", "m")),
    description="Photon-electron scattering. Proved photon has momentum.",
    uses=("h", "m_e", "c"),
    status=NodeStatus.EXPERIMENTAL,
    tags=("scattering", "photon"),
)

# Blackbody Radiation (Planck)
planck_law = EquationNode(
    id="planck_law",
    name="Planck's Law",
    domain="quantum_mechanics",
    latex=r"B_\nu(T) = \frac{2h\nu^3}{c^2}\frac{1}{e^{h\nu/k_B T} - 1}",
    sympy="B_nu = 2*h*nu**3/c**2 * 1/(exp(h*nu/(k_B*T)) - 1)",
    variables=(("B_nu", "Spectral radiance", "W/(m²⋅sr⋅Hz)"), ("nu", "Frequency", "Hz"), ("T", "Temperature", "K")),
    description="Spectral distribution of blackbody radiation. Resolved UV catastrophe.",
    uses=("h", "c", "k_B"),
    leads_to=("stefan_boltzmann", "wien_law"),
    status=NodeStatus.PROVEN,
    tags=("blackbody", "thermal"),
)

# Wien's Displacement Law
wien_law = EquationNode(
    id="wien_displacement",
    name="Wien's Displacement Law",
    domain="quantum_mechanics",
    latex=r"\lambda_{max} T = 2.898 \times 10^{-3} \text{ m⋅K}",
    sympy="lambda_max * T = 2.898e-3",
    variables=(("lambda_max", "Peak wavelength", "m"), ("T", "Temperature", "K")),
    description="Wavelength of maximum emission. Sun ~500nm, human ~10μm.",
    derives_from=("planck_law",),
    status=NodeStatus.PROVEN,
    tags=("blackbody", "thermal"),
)

# Stefan-Boltzmann Law
stefan_boltzmann = EquationNode(
    id="stefan_boltzmann_law",
    name="Stefan-Boltzmann Law",
    domain="thermodynamics",
    latex=r"j^* = \sigma T^4",
    sympy="j_star = sigma * T**4",
    variables=(("j_star", "Radiant emittance", "W/m²"), ("sigma", "Stefan-Boltzmann constant", "W/(m²⋅K⁴)"), ("T", "Temperature", "K")),
    description="Total power radiated by blackbody ∝ T⁴.",
    derives_from=("planck_law",),
    uses=("sigma",),
    status=NodeStatus.PROVEN,
    tags=("blackbody", "thermal"),
)

# Stimulated Emission Rate
stimulated_emission = EquationNode(
    id="einstein_b_coefficient",
    name="Stimulated Emission Rate",
    domain="quantum_mechanics",
    latex=r"R_{stim} = B_{21} \rho(\nu) N_2",
    sympy="R_stim = B_21 * rho_nu * N_2",
    variables=(("R_stim", "Stimulated emission rate", "s⁻¹"), ("B_21", "Einstein B coefficient", "m³/(J⋅s²)"), ("rho_nu", "Spectral energy density", "J⋅s/m³"), ("N_2", "Upper state population", "m⁻³")),
    description="Rate of stimulated emission. Basis of laser operation.",
    status=NodeStatus.PROVEN,
    tags=("laser", "emission"),
)

# Laser Gain
laser_gain = EquationNode(
    id="laser_gain",
    name="Laser Gain Coefficient",
    domain="quantum_mechanics",
    latex=r"\gamma = \sigma_{21}(N_2 - N_1) = \frac{c^2}{8\pi\nu^2 t_{sp}}g(\nu)(N_2 - N_1)",
    sympy="gamma = sigma_21 * (N_2 - N_1)",
    variables=(("gamma", "Gain coefficient", "m⁻¹"), ("sigma_21", "Stimulated emission cross-section", "m²"), ("N_2", "Upper state population", "m⁻³"), ("N_1", "Lower state population", "m⁻³")),
    description="Optical gain when N₂ > N₁ (population inversion).",
    derives_from=("stimulated_emission",),
    status=NodeStatus.PROVEN,
    tags=("laser", "gain"),
)

# Laser Threshold
laser_threshold = EquationNode(
    id="laser_threshold",
    name="Laser Threshold Condition",
    domain="quantum_mechanics",
    latex=r"\gamma_{th} = \alpha + \frac{1}{2L}\ln\frac{1}{R_1 R_2}",
    sympy="gamma_th = alpha + (1/(2*L))*ln(1/(R1*R2))",
    variables=(("gamma_th", "Threshold gain", "m⁻¹"), ("alpha", "Cavity loss", "m⁻¹"), ("L", "Cavity length", "m"), ("R1", "Mirror 1 reflectance", "dimensionless"), ("R2", "Mirror 2 reflectance", "dimensionless")),
    description="Gain must exceed losses for laser oscillation.",
    status=NodeStatus.PROVEN,
    tags=("laser", "threshold"),
)

# Spontaneous Emission Rate
spontaneous_emission = EquationNode(
    id="spontaneous_emission_rate",
    name="Spontaneous Emission Rate",
    domain="quantum_mechanics",
    latex=r"A_{21} = \frac{8\pi h\nu^3}{c^3}B_{21} = \frac{1}{\tau_{sp}}",
    sympy="A_21 = 8*pi*h*nu**3/c**3 * B_21",
    variables=(("A_21", "Einstein A coefficient", "s⁻¹"), ("tau_sp", "Spontaneous lifetime", "s")),
    description="Spontaneous emission rate. Related to B coefficient.",
    uses=("h", "c"),
    status=NodeStatus.PROVEN,
    tags=("emission", "spontaneous"),
)

# Photon Statistics
photon_number_coherent = EquationNode(
    id="photon_number_coherent",
    name="Photon Number (Coherent State)",
    domain="quantum_mechanics",
    latex=r"P(n) = \frac{\bar{n}^n e^{-\bar{n}}}{n!}",
    sympy="P_n = nbar**n * exp(-nbar) / factorial(n)",
    variables=(("P_n", "Probability of n photons", "dimensionless"), ("nbar", "Mean photon number", "dimensionless")),
    description="Poisson distribution for coherent (laser) light.",
    status=NodeStatus.PROVEN,
    tags=("photon", "statistics"),
)

# Second-Order Coherence
g2_coherence = EquationNode(
    id="g2_coherence",
    name="Second-Order Coherence Function",
    domain="quantum_mechanics",
    latex=r"g^{(2)}(\tau) = \frac{\langle I(t)I(t+\tau) \rangle}{\langle I(t) \rangle^2}",
    sympy="g2 = <I(t)*I(t+tau)>/<I>**2",
    variables=(("g2", "Second-order coherence", "dimensionless"), ("I", "Intensity", "W/m²"), ("tau", "Time delay", "s")),
    description="Intensity correlation. g²(0)=1 coherent, g²(0)=2 thermal, g²(0)<1 antibunched.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("coherence", "quantum"),
)

# Hanbury Brown-Twiss Effect
hbt_effect = EquationNode(
    id="hbt_effect",
    name="Hanbury Brown-Twiss Effect",
    domain="quantum_mechanics",
    latex=r"g^{(2)}(0) = 2 \quad \text{(thermal light)}",
    sympy="g2_0_thermal = 2",
    variables=(),
    description="Thermal light shows photon bunching. g²(0)=2.",
    derives_from=("g2_coherence",),
    status=NodeStatus.EXPERIMENTAL,
    tags=("coherence", "bunching"),
)

NODES = [
    photon_energy, photon_momentum, photoelectric, compton_scattering, planck_law,
    wien_law, stefan_boltzmann, stimulated_emission, laser_gain, laser_threshold,
    spontaneous_emission, photon_number_coherent, g2_coherence, hbt_effect
]
