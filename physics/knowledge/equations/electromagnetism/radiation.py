"""
PATH: physics/knowledge/equations/electromagnetism/radiation.py
PURPOSE: Electromagnetic radiation and antenna equations
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Poynting Vector
poynting_vector = EquationNode(
    id="poynting_vector",
    name="Poynting Vector",
    domain="electromagnetism",
    latex=r"\vec{S} = \frac{1}{\mu_0}\vec{E} \times \vec{B} = \vec{E} \times \vec{H}",
    sympy="S = (1/mu_0)*E cross B",
    variables=(("S", "Poynting vector (power flux)", "W/m²"), ("E", "Electric field", "V/m"), ("B", "Magnetic field", "T")),
    description="Energy flow per unit area per unit time. Direction is wave propagation.",
    uses=("mu_0",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("energy", "radiation"),
)

# Radiation Intensity
radiation_intensity = EquationNode(
    id="radiation_intensity",
    name="Average Radiation Intensity",
    domain="electromagnetism",
    latex=r"\langle S \rangle = \frac{1}{2}\epsilon_0 c E_0^2 = \frac{cB_0^2}{2\mu_0}",
    sympy="S_avg = (1/2)*epsilon_0*c*E_0**2",
    variables=(("S_avg", "Time-averaged intensity", "W/m²"), ("E_0", "Electric field amplitude", "V/m")),
    description="Average power for sinusoidal EM wave.",
    derives_from=("poynting_vector",),
    uses=("epsilon_0", "c", "mu_0"),
    status=NodeStatus.PROVEN,
    tags=("intensity", "average"),
)

# Larmor Formula
larmor_formula = EquationNode(
    id="larmor_formula",
    name="Larmor Formula",
    domain="electromagnetism",
    latex=r"P = \frac{q^2 a^2}{6\pi\epsilon_0 c^3} = \frac{\mu_0 q^2 a^2}{6\pi c}",
    sympy="P = q**2*a**2/(6*pi*epsilon_0*c**3)",
    variables=(("P", "Radiated power", "W"), ("q", "Charge", "C"), ("a", "Acceleration", "m/s²")),
    description="Power radiated by accelerating charge. Basis of synchrotron radiation.",
    uses=("epsilon_0", "c", "mu_0"),
    status=NodeStatus.PROVEN,
    tags=("radiation", "acceleration"),
)

# Radiation Resistance
radiation_resistance = EquationNode(
    id="radiation_resistance",
    name="Radiation Resistance (Short Dipole)",
    domain="electromagnetism",
    latex=r"R_r = 80\pi^2\left(\frac{l}{\lambda}\right)^2 \approx 790\left(\frac{l}{\lambda}\right)^2 \; \Omega",
    sympy="R_r = 80*pi**2*(l/lambda)**2",
    variables=(("R_r", "Radiation resistance", "Ω"), ("l", "Dipole length", "m"), ("lambda", "Wavelength", "m")),
    description="Resistance that accounts for power radiated. P = I²R_r/2.",
    conditions=("l << λ",),
    status=NodeStatus.PROVEN,
    tags=("antenna", "dipole"),
)

# Antenna Gain
antenna_gain = EquationNode(
    id="antenna_gain",
    name="Antenna Gain",
    domain="electromagnetism",
    latex=r"G = \frac{4\pi U(\theta,\phi)}{P_{in}} = \eta_r D",
    sympy="G = 4*pi*U/(P_in)",
    variables=(("G", "Gain", "dimensionless"), ("U", "Radiation intensity", "W/sr"), ("P_in", "Input power", "W"), ("D", "Directivity", "dimensionless"), ("eta_r", "Radiation efficiency", "dimensionless")),
    description="Gain relative to isotropic radiator. Half-wave dipole: G = 1.64 (2.15 dBi).",
    status=NodeStatus.FUNDAMENTAL,
    tags=("antenna", "gain"),
)

# Effective Aperture
effective_aperture = EquationNode(
    id="effective_aperture",
    name="Effective Aperture",
    domain="electromagnetism",
    latex=r"A_e = \frac{G\lambda^2}{4\pi}",
    sympy="A_e = G*lambda**2/(4*pi)",
    variables=(("A_e", "Effective aperture", "m²"), ("G", "Gain", "dimensionless"), ("lambda", "Wavelength", "m")),
    description="Captures power P_r = S × A_e. Relates gain to physical size.",
    derives_from=("antenna_gain",),
    status=NodeStatus.PROVEN,
    tags=("antenna", "aperture"),
)

# Friis Transmission Equation
friis_equation = EquationNode(
    id="friis_equation",
    name="Friis Transmission Equation",
    domain="electromagnetism",
    latex=r"\frac{P_r}{P_t} = G_t G_r\left(\frac{\lambda}{4\pi d}\right)^2",
    sympy="P_r/P_t = G_t*G_r*(lambda/(4*pi*d))**2",
    variables=(("P_r", "Received power", "W"), ("P_t", "Transmitted power", "W"), ("G_t", "Transmit gain", "dimensionless"), ("G_r", "Receive gain", "dimensionless"), ("d", "Distance", "m")),
    description="Free-space radio link. (λ/4πd)² is free-space path loss.",
    status=NodeStatus.PROVEN,
    tags=("link_budget", "communication"),
)

# Radar Equation
radar_equation = EquationNode(
    id="radar_equation",
    name="Radar Range Equation",
    domain="electromagnetism",
    latex=r"P_r = \frac{P_t G^2 \lambda^2 \sigma}{(4\pi)^3 R^4}",
    sympy="P_r = P_t*G**2*lambda**2*sigma/((4*pi)**3*R**4)",
    variables=(("P_r", "Received power", "W"), ("P_t", "Transmitted power", "W"), ("G", "Antenna gain", "dimensionless"), ("sigma", "Radar cross section", "m²"), ("R", "Range", "m")),
    description="Two-way propagation gives R⁴ dependence.",
    status=NodeStatus.PROVEN,
    tags=("radar", "detection"),
)

# Electric Dipole Radiation
dipole_radiation = EquationNode(
    id="electric_dipole_radiation",
    name="Electric Dipole Radiation Pattern",
    domain="electromagnetism",
    latex=r"E_\theta = \frac{\mu_0 c k^2 p_0}{4\pi r}\sin\theta, \quad P \propto \sin^2\theta",
    sympy="E_theta = mu_0*c*k**2*p_0*sin(theta)/(4*pi*r)",
    variables=(("E_theta", "Electric field", "V/m"), ("p_0", "Dipole moment amplitude", "C⋅m"), ("k", "Wave number", "m⁻¹"), ("theta", "Angle from axis", "rad")),
    description="Donut pattern. Zero radiation along dipole axis.",
    uses=("mu_0", "c"),
    status=NodeStatus.PROVEN,
    tags=("dipole", "pattern"),
)

# Antenna Array Factor
array_factor = EquationNode(
    id="array_factor",
    name="Antenna Array Factor",
    domain="electromagnetism",
    latex=r"AF = \sum_{n=0}^{N-1} e^{jn(kd\cos\theta + \beta)}",
    sympy="AF = sum(exp(j*n*(k*d*cos(theta) + beta)))",
    variables=(("AF", "Array factor", "dimensionless"), ("N", "Number of elements", "dimensionless"), ("d", "Element spacing", "m"), ("beta", "Progressive phase shift", "rad")),
    description="Pattern multiplication: E_total = Element × Array Factor.",
    status=NodeStatus.PROVEN,
    tags=("antenna", "array"),
)

# Skin Depth
skin_depth = EquationNode(
    id="skin_depth",
    name="Skin Depth",
    domain="electromagnetism",
    latex=r"\delta = \sqrt{\frac{2}{\omega\mu\sigma}} = \frac{1}{\sqrt{\pi f \mu\sigma}}",
    sympy="delta = sqrt(2/(omega*mu*sigma))",
    variables=(("delta", "Skin depth", "m"), ("omega", "Angular frequency", "rad/s"), ("mu", "Permeability", "H/m"), ("sigma", "Conductivity", "S/m")),
    description="Penetration depth of EM wave in conductor. Copper at 60 Hz: δ ~ 8.5 mm.",
    status=NodeStatus.PROVEN,
    tags=("conductor", "penetration"),
)

# Characteristic Impedance of Free Space
free_space_impedance = EquationNode(
    id="free_space_impedance",
    name="Impedance of Free Space",
    domain="electromagnetism",
    latex=r"\eta_0 = \sqrt{\frac{\mu_0}{\epsilon_0}} = \mu_0 c \approx 377 \; \Omega",
    sympy="eta_0 = sqrt(mu_0/epsilon_0) = 377",
    variables=(("eta_0", "Free space impedance", "Ω")),
    description="Ratio E/H for plane wave in vacuum.",
    uses=("mu_0", "epsilon_0", "c"),
    status=NodeStatus.PROVEN,
    tags=("impedance", "wave"),
)

NODES = [
    poynting_vector, radiation_intensity, larmor_formula, radiation_resistance,
    antenna_gain, effective_aperture, friis_equation, radar_equation,
    dipole_radiation, array_factor, skin_depth, free_space_impedance
]
