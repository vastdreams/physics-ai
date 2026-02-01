"""
PATH: physics/knowledge/equations/optics/wave_optics.py
PURPOSE: Wave optics - interference, diffraction, polarization
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Young's Double Slit
young_double_slit = EquationNode(
    id="young_double_slit",
    name="Young's Double Slit Interference",
    domain="optics",
    latex=r"d\sin\theta = m\lambda \quad y_m = \frac{m\lambda L}{d}",
    sympy="d*sin(theta) = m*lambda",
    variables=(("d", "Slit separation", "m"), ("theta", "Angle to maximum", "rad"), ("m", "Order", "dimensionless"), ("lambda", "Wavelength", "m"), ("y_m", "Position on screen", "m"), ("L", "Screen distance", "m")),
    description="Constructive interference condition for double slit.",
    status=NodeStatus.PROVEN,
    tags=("interference", "double_slit"),
)

# Single Slit Diffraction
single_slit = EquationNode(
    id="single_slit_diffraction",
    name="Single Slit Diffraction Minima",
    domain="optics",
    latex=r"a\sin\theta = m\lambda \quad (m = \pm 1, \pm 2, ...)",
    sympy="a*sin(theta) = m*lambda",
    variables=(("a", "Slit width", "m"), ("theta", "Angle to minimum", "rad"), ("m", "Order", "dimensionless")),
    description="Dark fringe positions for single slit diffraction.",
    status=NodeStatus.PROVEN,
    tags=("diffraction", "single_slit"),
)

# Diffraction Grating
diffraction_grating = EquationNode(
    id="diffraction_grating",
    name="Diffraction Grating Equation",
    domain="optics",
    latex=r"d\sin\theta = m\lambda",
    sympy="d*sin(theta) = m*lambda",
    variables=(("d", "Grating spacing", "m"), ("theta", "Diffraction angle", "rad"), ("m", "Order", "dimensionless"), ("lambda", "Wavelength", "m")),
    description="Maxima positions for grating. Same form as double slit but sharper peaks.",
    status=NodeStatus.PROVEN,
    tags=("diffraction", "grating", "spectroscopy"),
)

# Resolving Power of Grating
grating_resolution = EquationNode(
    id="grating_resolving_power",
    name="Grating Resolving Power",
    domain="optics",
    latex=r"R = \frac{\lambda}{\Delta\lambda} = mN",
    sympy="R = m*N",
    variables=(("R", "Resolving power", "dimensionless"), ("m", "Order", "dimensionless"), ("N", "Total grooves illuminated", "dimensionless")),
    description="Ability to distinguish nearby wavelengths.",
    status=NodeStatus.PROVEN,
    tags=("grating", "resolution"),
)

# Rayleigh Criterion
rayleigh_criterion = EquationNode(
    id="rayleigh_criterion",
    name="Rayleigh Criterion",
    domain="optics",
    latex=r"\theta_{min} = 1.22\frac{\lambda}{D}",
    sympy="theta_min = 1.22*lambda/D",
    variables=(("theta_min", "Minimum resolvable angle", "rad"), ("lambda", "Wavelength", "m"), ("D", "Aperture diameter", "m")),
    description="Angular resolution limit for circular aperture.",
    status=NodeStatus.PROVEN,
    tags=("resolution", "diffraction"),
)

# Airy Disk
airy_disk = EquationNode(
    id="airy_disk",
    name="Airy Disk Radius",
    domain="optics",
    latex=r"r_{Airy} = 1.22\frac{\lambda f}{D}",
    sympy="r_airy = 1.22*lambda*f/D",
    variables=(("r_airy", "Airy disk radius", "m"), ("lambda", "Wavelength", "m"), ("f", "Focal length", "m"), ("D", "Aperture", "m")),
    description="Radius of central diffraction spot from circular aperture.",
    derives_from=("rayleigh_criterion",),
    status=NodeStatus.PROVEN,
    tags=("diffraction", "aperture"),
)

# Thin Film Interference
thin_film = EquationNode(
    id="thin_film_interference",
    name="Thin Film Interference",
    domain="optics",
    latex=r"2nt\cos\theta_r = (m + \frac{1}{2})\lambda \text{ (destructive with phase shift)}",
    sympy="2*n*t*cos(theta_r) = (m + 1/2)*lambda",
    variables=(("n", "Film index", "dimensionless"), ("t", "Film thickness", "m"), ("theta_r", "Refracted angle", "rad")),
    description="Interference from reflections at film surfaces. Phase shift at higher-n interface.",
    status=NodeStatus.PROVEN,
    tags=("interference", "thin_film"),
)

# Newton's Rings
newton_rings = EquationNode(
    id="newton_rings",
    name="Newton's Rings",
    domain="optics",
    latex=r"r_m = \sqrt{m\lambda R}",
    sympy="r_m = sqrt(m*lambda*R)",
    variables=(("r_m", "Ring radius", "m"), ("m", "Ring number", "dimensionless"), ("R", "Lens radius of curvature", "m")),
    description="Interference pattern from air gap between lens and flat surface.",
    derives_from=("thin_film_interference",),
    status=NodeStatus.PROVEN,
    tags=("interference", "newton"),
)

# Michelson Interferometer
michelson_fringe = EquationNode(
    id="michelson_interferometer",
    name="Michelson Interferometer Fringe Shift",
    domain="optics",
    latex=r"\Delta N = \frac{2\Delta d}{\lambda}",
    sympy="delta_N = 2*delta_d/lambda",
    variables=(("delta_N", "Fringe shift", "dimensionless"), ("delta_d", "Path difference change", "m"), ("lambda", "Wavelength", "m")),
    description="Number of fringes shifted when mirror moves.",
    status=NodeStatus.PROVEN,
    tags=("interferometer", "measurement"),
)

# Fabry-Perot Finesse
fabry_perot = EquationNode(
    id="fabry_perot_finesse",
    name="Fabry-Pérot Finesse",
    domain="optics",
    latex=r"\mathcal{F} = \frac{\pi\sqrt{R}}{1-R}",
    sympy="F = pi*sqrt(R)/(1-R)",
    variables=(("F", "Finesse", "dimensionless"), ("R", "Mirror reflectance", "dimensionless")),
    description="Sharpness of Fabry-Pérot transmission peaks.",
    status=NodeStatus.PROVEN,
    tags=("interferometer", "cavity"),
)

# Coherence Length
coherence_length = EquationNode(
    id="coherence_length",
    name="Coherence Length",
    domain="optics",
    latex=r"l_c = \frac{\lambda^2}{\Delta\lambda} = c\tau_c",
    sympy="l_c = lambda**2/delta_lambda",
    variables=(("l_c", "Coherence length", "m"), ("lambda", "Wavelength", "m"), ("delta_lambda", "Spectral width", "m"), ("tau_c", "Coherence time", "s")),
    description="Maximum path difference for interference. Laser has large l_c.",
    status=NodeStatus.PROVEN,
    tags=("coherence", "interference"),
)

# Malus's Law
malus_law = EquationNode(
    id="malus_law",
    name="Malus's Law",
    domain="optics",
    latex=r"I = I_0 \cos^2\theta",
    sympy="I = I_0 * cos(theta)**2",
    variables=(("I", "Transmitted intensity", "W/m²"), ("I_0", "Incident intensity", "W/m²"), ("theta", "Angle between polarizer axes", "rad")),
    description="Intensity through polarizer when polarized light incident.",
    status=NodeStatus.PROVEN,
    tags=("polarization", "intensity"),
)

# Circular Birefringence
optical_rotation = EquationNode(
    id="optical_rotation",
    name="Optical Rotation",
    domain="optics",
    latex=r"\theta = [\alpha] \cdot c \cdot l",
    sympy="theta = alpha * c * l",
    variables=(("theta", "Rotation angle", "rad"), ("alpha", "Specific rotation", "rad⋅m²/kg"), ("c", "Concentration", "kg/m³"), ("l", "Path length", "m")),
    description="Rotation of polarization in optically active medium.",
    status=NodeStatus.EMPIRICAL,
    tags=("polarization", "birefringence"),
)

# Jones Vector (Polarization State)
jones_vector = EquationNode(
    id="jones_vector",
    name="Jones Vector",
    domain="optics",
    latex=r"\vec{E} = \begin{pmatrix} E_x \\ E_y e^{i\phi} \end{pmatrix}",
    sympy="E = [E_x, E_y*exp(i*phi)]",
    variables=(("E_x", "x-component amplitude", "V/m"), ("E_y", "y-component amplitude", "V/m"), ("phi", "Phase difference", "rad")),
    description="Complex vector representation of polarization state.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("polarization", "jones"),
)

# Stokes Parameters
stokes_parameters = EquationNode(
    id="stokes_parameters",
    name="Stokes Parameters",
    domain="optics",
    latex=r"S_0 = I, \; S_1 = I_x - I_y, \; S_2 = I_{45°} - I_{-45°}, \; S_3 = I_R - I_L",
    sympy="S = [I, Ix-Iy, I45-I_45, IR-IL]",
    variables=(("S_0", "Total intensity", "W/m²"), ("S_1", "Linear horizontal polarization", "W/m²"), ("S_2", "Linear 45° polarization", "W/m²"), ("S_3", "Circular polarization", "W/m²")),
    description="Complete description of polarization including partially polarized light.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("polarization", "stokes"),
)

NODES = [
    young_double_slit, single_slit, diffraction_grating, grating_resolution,
    rayleigh_criterion, airy_disk, thin_film, newton_rings, michelson_fringe,
    fabry_perot, coherence_length, malus_law, optical_rotation, jones_vector, stokes_parameters
]
