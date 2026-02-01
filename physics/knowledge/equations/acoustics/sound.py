"""
PATH: physics/knowledge/equations/acoustics/sound.py
PURPOSE: Sound and acoustics equations
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Sound Speed in Gas
sound_speed_gas = EquationNode(
    id="sound_speed_gas",
    name="Speed of Sound in Gas",
    domain="acoustics",
    latex=r"v = \sqrt{\frac{\gamma RT}{M}} = \sqrt{\gamma \frac{P}{\rho}}",
    sympy="v = sqrt(gamma*R*T/M)",
    variables=(("v", "Sound speed", "m/s"), ("gamma", "Heat capacity ratio", "dimensionless"), ("R", "Gas constant", "J/(mol⋅K)"), ("T", "Temperature", "K"), ("M", "Molar mass", "kg/mol")),
    description="Sound speed in ideal gas. ~343 m/s in air at 20°C.",
    uses=("R",),
    status=NodeStatus.PROVEN,
    tags=("sound", "gas"),
)

# Sound Intensity Level
sound_intensity_level = EquationNode(
    id="sound_intensity_level",
    name="Sound Intensity Level (Decibels)",
    domain="acoustics",
    latex=r"L_I = 10 \log_{10}\frac{I}{I_0} \text{ dB}, \quad I_0 = 10^{-12} \text{ W/m}^2",
    sympy="L_I = 10*log10(I/I_0)",
    variables=(("L_I", "Intensity level", "dB"), ("I", "Intensity", "W/m²"), ("I_0", "Reference intensity", "W/m²")),
    description="Logarithmic scale for sound. 0 dB = hearing threshold.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("decibel", "intensity"),
)

# Sound Pressure Level
sound_pressure_level = EquationNode(
    id="sound_pressure_level",
    name="Sound Pressure Level",
    domain="acoustics",
    latex=r"L_p = 20 \log_{10}\frac{p}{p_0} \text{ dB}, \quad p_0 = 20 \text{ μPa}",
    sympy="L_p = 20*log10(p/p_0)",
    variables=(("L_p", "Sound pressure level", "dB"), ("p", "Pressure amplitude", "Pa"), ("p_0", "Reference pressure", "Pa")),
    description="SPL in decibels. 20 μPa ≈ hearing threshold at 1 kHz.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("decibel", "pressure"),
)

# Acoustic Impedance
acoustic_impedance = EquationNode(
    id="acoustic_impedance",
    name="Acoustic Impedance",
    domain="acoustics",
    latex=r"Z = \rho v",
    sympy="Z = rho*v",
    variables=(("Z", "Acoustic impedance", "Pa⋅s/m = rayl"), ("rho", "Density", "kg/m³"), ("v", "Sound speed", "m/s")),
    description="Product of density and sound speed. Air: ~415 rayl. Water: ~1.5 Mrayl.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("impedance", "acoustic"),
)

# Resonance (Open Pipe)
open_pipe = EquationNode(
    id="open_pipe_resonance",
    name="Open Pipe Resonance",
    domain="acoustics",
    latex=r"f_n = \frac{nv}{2L}, \quad n = 1, 2, 3, ...",
    sympy="f_n = n*v/(2*L)",
    variables=(("f_n", "Resonant frequency", "Hz"), ("n", "Harmonic number", "dimensionless"), ("v", "Sound speed", "m/s"), ("L", "Pipe length", "m")),
    description="Both ends open: all harmonics present.",
    status=NodeStatus.PROVEN,
    tags=("resonance", "pipe"),
)

# Resonance (Closed Pipe)
closed_pipe = EquationNode(
    id="closed_pipe_resonance",
    name="Closed Pipe Resonance",
    domain="acoustics",
    latex=r"f_n = \frac{nv}{4L}, \quad n = 1, 3, 5, ... \text{ (odd only)}",
    sympy="f_n = n*v/(4*L)",
    variables=(("f_n", "Resonant frequency", "Hz"), ("n", "Harmonic number (odd)", "dimensionless"), ("v", "Sound speed", "m/s"), ("L", "Pipe length", "m")),
    description="One end closed: only odd harmonics present.",
    status=NodeStatus.PROVEN,
    tags=("resonance", "pipe"),
)

# Helmholtz Resonator
helmholtz_resonator = EquationNode(
    id="helmholtz_resonator",
    name="Helmholtz Resonator Frequency",
    domain="acoustics",
    latex=r"f_0 = \frac{v}{2\pi}\sqrt{\frac{A}{V L_{eff}}}",
    sympy="f_0 = v/(2*pi)*sqrt(A/(V*L_eff))",
    variables=(("f_0", "Resonant frequency", "Hz"), ("v", "Sound speed", "m/s"), ("A", "Neck cross-section", "m²"), ("V", "Cavity volume", "m³"), ("L_eff", "Effective neck length", "m")),
    description="Frequency of air cavity resonator (bottle, room with window).",
    status=NodeStatus.PROVEN,
    tags=("resonance", "helmholtz"),
)

# Sabine Reverberation
sabine = EquationNode(
    id="sabine_reverberation",
    name="Sabine Reverberation Time",
    domain="acoustics",
    latex=r"T_{60} = \frac{0.161 V}{A} = \frac{0.161 V}{\sum_i S_i \alpha_i}",
    sympy="T_60 = 0.161*V/A",
    variables=(("T_60", "Reverberation time", "s"), ("V", "Room volume", "m³"), ("A", "Total absorption", "m²"), ("S_i", "Surface area", "m²"), ("alpha_i", "Absorption coefficient", "dimensionless")),
    description="Time for sound to decay by 60 dB. Optimal ~0.5-2s for concert halls.",
    status=NodeStatus.EMPIRICAL,
    tags=("room", "reverberation"),
)

# Absorption Coefficient
absorption = EquationNode(
    id="absorption_coefficient",
    name="Sound Absorption Coefficient",
    domain="acoustics",
    latex=r"\alpha = 1 - \frac{I_r}{I_i} = 1 - |R|^2",
    sympy="alpha = 1 - I_r/I_i",
    variables=(("alpha", "Absorption coefficient", "dimensionless"), ("I_r", "Reflected intensity", "W/m²"), ("I_i", "Incident intensity", "W/m²")),
    description="Fraction of energy absorbed. 0 = perfect reflection, 1 = perfect absorption.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("absorption", "material"),
)

# Ultrasound Attenuation
ultrasound_attenuation = EquationNode(
    id="ultrasound_attenuation",
    name="Ultrasound Attenuation",
    domain="acoustics",
    latex=r"I = I_0 e^{-2\alpha x}",
    sympy="I = I_0*exp(-2*alpha*x)",
    variables=(("I", "Intensity", "W/m²"), ("I_0", "Initial intensity", "W/m²"), ("alpha", "Attenuation coefficient", "m⁻¹"), ("x", "Distance", "m")),
    description="Exponential decay of ultrasound in tissue. α increases with frequency.",
    status=NodeStatus.PROVEN,
    tags=("ultrasound", "medical"),
)

# Doppler Ultrasound
doppler_ultrasound = EquationNode(
    id="doppler_ultrasound",
    name="Doppler Ultrasound Shift",
    domain="acoustics",
    latex=r"\Delta f = \frac{2f_0 v \cos\theta}{c}",
    sympy="delta_f = 2*f_0*v*cos(theta)/c",
    variables=(("delta_f", "Frequency shift", "Hz"), ("f_0", "Transmitted frequency", "Hz"), ("v", "Blood velocity", "m/s"), ("theta", "Beam angle", "rad"), ("c", "Sound speed in tissue ~1540 m/s", "m/s")),
    description="Frequency shift used to measure blood flow.",
    derives_from=("doppler_effect",),
    status=NodeStatus.PROVEN,
    tags=("doppler", "medical"),
)

# Noise Addition
noise_addition = EquationNode(
    id="noise_addition",
    name="Adding Sound Levels",
    domain="acoustics",
    latex=r"L_{total} = 10 \log_{10}\left(\sum_i 10^{L_i/10}\right) \text{ dB}",
    sympy="L_total = 10*log10(sum(10**(L_i/10)))",
    variables=(("L_total", "Total level", "dB"), ("L_i", "Individual levels", "dB")),
    description="Adding intensities, not dB directly. Two 90 dB sources = 93 dB.",
    derives_from=("sound_intensity_level",),
    status=NodeStatus.PROVEN,
    tags=("decibel", "addition"),
)

NODES = [
    sound_speed_gas, sound_intensity_level, sound_pressure_level, acoustic_impedance,
    open_pipe, closed_pipe, helmholtz_resonator, sabine, absorption,
    ultrasound_attenuation, doppler_ultrasound, noise_addition
]
