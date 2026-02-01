"""
PATH: physics/knowledge/equations/acoustics/waves.py
PURPOSE: General wave physics equations
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Wave Equation
wave_equation = EquationNode(
    id="wave_equation",
    name="Wave Equation",
    domain="waves",
    latex=r"\frac{\partial^2 u}{\partial t^2} = v^2 \nabla^2 u",
    sympy="d2u/dt2 = v**2 * laplacian(u)",
    variables=(("u", "Wave displacement", "m"), ("v", "Wave speed", "m/s")),
    description="Fundamental PDE for wave propagation. Solutions: u = f(x-vt) + g(x+vt).",
    status=NodeStatus.FUNDAMENTAL,
    tags=("wave", "pde"),
)

# Wave Speed (String)
wave_speed_string = EquationNode(
    id="wave_speed_string",
    name="Wave Speed on String",
    domain="waves",
    latex=r"v = \sqrt{\frac{T}{\mu}}",
    sympy="v = sqrt(T/mu)",
    variables=(("v", "Wave speed", "m/s"), ("T", "Tension", "N"), ("mu", "Linear mass density", "kg/m")),
    description="Speed of transverse waves on stretched string.",
    status=NodeStatus.PROVEN,
    tags=("wave", "string"),
)

# Wave Speed (Solid Rod)
wave_speed_solid = EquationNode(
    id="wave_speed_solid",
    name="Wave Speed in Solid",
    domain="waves",
    latex=r"v = \sqrt{\frac{E}{\rho}}",
    sympy="v = sqrt(E/rho)",
    variables=(("v", "Wave speed", "m/s"), ("E", "Young's modulus", "Pa"), ("rho", "Density", "kg/m³")),
    description="Speed of longitudinal waves in solid rod.",
    status=NodeStatus.PROVEN,
    tags=("wave", "solid"),
)

# Dispersion Relation
dispersion_relation = EquationNode(
    id="dispersion_relation",
    name="Dispersion Relation",
    domain="waves",
    latex=r"\omega = \omega(k), \quad v_p = \frac{\omega}{k}, \quad v_g = \frac{d\omega}{dk}",
    sympy="omega = omega(k)",
    variables=(("omega", "Angular frequency", "rad/s"), ("k", "Wave number", "m⁻¹"), ("v_p", "Phase velocity", "m/s"), ("v_g", "Group velocity", "m/s")),
    description="Relation between frequency and wavelength. Determines dispersion.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("wave", "dispersion"),
)

# Standing Wave
standing_wave = EquationNode(
    id="standing_wave",
    name="Standing Wave (Fixed Ends)",
    domain="waves",
    latex=r"f_n = \frac{nv}{2L}, \quad n = 1, 2, 3, ...",
    sympy="f_n = n*v/(2*L)",
    variables=(("f_n", "Natural frequency", "Hz"), ("n", "Mode number", "dimensionless"), ("v", "Wave speed", "m/s"), ("L", "Length", "m")),
    description="Resonant frequencies of string fixed at both ends.",
    status=NodeStatus.PROVEN,
    tags=("resonance", "standing"),
)

# Beat Frequency
beat_frequency = EquationNode(
    id="beat_frequency",
    name="Beat Frequency",
    domain="waves",
    latex=r"f_{beat} = |f_1 - f_2|",
    sympy="f_beat = |f1 - f2|",
    variables=(("f_beat", "Beat frequency", "Hz"), ("f1", "Frequency 1", "Hz"), ("f2", "Frequency 2", "Hz")),
    description="Amplitude modulation from superposition of nearby frequencies.",
    status=NodeStatus.PROVEN,
    tags=("interference", "beat"),
)

# Doppler Effect
doppler_effect = EquationNode(
    id="doppler_effect",
    name="Doppler Effect",
    domain="waves",
    latex=r"f' = f\frac{v + v_o}{v - v_s}",
    sympy="f_prime = f*(v + v_o)/(v - v_s)",
    variables=(("f_prime", "Observed frequency", "Hz"), ("f", "Source frequency", "Hz"), ("v", "Wave speed", "m/s"), ("v_o", "Observer velocity", "m/s"), ("v_s", "Source velocity", "m/s")),
    description="Frequency shift due to relative motion. + toward, - away.",
    status=NodeStatus.PROVEN,
    tags=("doppler", "frequency"),
)

# Mach Cone
mach_cone = EquationNode(
    id="mach_cone",
    name="Mach Cone Angle",
    domain="waves",
    latex=r"\sin\theta = \frac{v}{v_s} = \frac{1}{Ma}",
    sympy="sin(theta) = v/v_s = 1/Ma",
    variables=(("theta", "Mach angle", "rad"), ("v", "Wave speed", "m/s"), ("v_s", "Source speed", "m/s"), ("Ma", "Mach number", "dimensionless")),
    description="Half-angle of shock cone for supersonic source.",
    derives_from=("doppler_effect",),
    conditions=("Ma > 1",),
    status=NodeStatus.PROVEN,
    tags=("supersonic", "shock"),
)

# Reflection Coefficient
reflection_coefficient = EquationNode(
    id="reflection_coefficient_wave",
    name="Wave Reflection Coefficient",
    domain="waves",
    latex=r"R = \frac{Z_2 - Z_1}{Z_2 + Z_1}, \quad T = \frac{2Z_2}{Z_2 + Z_1}",
    sympy="R = (Z2 - Z1)/(Z2 + Z1)",
    variables=(("R", "Reflection coefficient", "dimensionless"), ("T", "Transmission coefficient", "dimensionless"), ("Z1", "Impedance 1", "varies"), ("Z2", "Impedance 2", "varies")),
    description="Wave reflection at impedance mismatch. |R| = 1 at fixed/free ends.",
    status=NodeStatus.PROVEN,
    tags=("reflection", "impedance"),
)

# Wave Intensity
wave_intensity = EquationNode(
    id="wave_intensity",
    name="Wave Intensity",
    domain="waves",
    latex=r"I = \frac{1}{2}\rho v \omega^2 A^2 \propto A^2",
    sympy="I = (1/2)*rho*v*omega**2*A**2",
    variables=(("I", "Intensity", "W/m²"), ("rho", "Medium density", "kg/m³"), ("v", "Wave speed", "m/s"), ("omega", "Angular frequency", "rad/s"), ("A", "Amplitude", "m")),
    description="Power per unit area. Proportional to amplitude squared.",
    status=NodeStatus.PROVEN,
    tags=("intensity", "power"),
)

# Inverse Square Law
inverse_square = EquationNode(
    id="inverse_square_intensity",
    name="Inverse Square Law (Intensity)",
    domain="waves",
    latex=r"I = \frac{P}{4\pi r^2}",
    sympy="I = P/(4*pi*r**2)",
    variables=(("I", "Intensity", "W/m²"), ("P", "Source power", "W"), ("r", "Distance", "m")),
    description="Intensity decreases as 1/r² for spherical wave.",
    status=NodeStatus.PROVEN,
    tags=("intensity", "spherical"),
)

# Wave Superposition
wave_superposition = EquationNode(
    id="wave_superposition",
    name="Principle of Superposition",
    domain="waves",
    latex=r"u_{total} = \sum_i u_i",
    sympy="u_total = sum(u_i)",
    variables=(("u_total", "Total displacement", "m"), ("u_i", "Individual wave", "m")),
    description="Waves add linearly. Basis for interference and Fourier analysis.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("superposition", "linear"),
)

NODES = [
    wave_equation, wave_speed_string, wave_speed_solid, dispersion_relation,
    standing_wave, beat_frequency, doppler_effect, mach_cone,
    reflection_coefficient, wave_intensity, inverse_square, wave_superposition
]
