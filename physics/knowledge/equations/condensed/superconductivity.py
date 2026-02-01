"""
PATH: physics/knowledge/equations/condensed/superconductivity.py
PURPOSE: Superconductivity and superfluidity equations
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Critical Temperature (BCS)
bcs_tc = EquationNode(
    id="bcs_critical_temperature",
    name="BCS Critical Temperature",
    domain="condensed_matter",
    latex=r"k_B T_c = 1.13 \hbar\omega_D e^{-1/N(0)V}",
    sympy="k_B*T_c = 1.13*hbar*omega_D*exp(-1/(N_0*V))",
    variables=(("T_c", "Critical temperature", "K"), ("omega_D", "Debye frequency", "rad/s"), ("N_0", "DOS at Fermi level", "J⁻¹⋅m⁻³"), ("V", "BCS pairing potential", "J⋅m³")),
    description="BCS theory prediction for superconducting transition temperature.",
    uses=("hbar", "k_B"),
    status=NodeStatus.PROVEN,
    tags=("superconductivity", "bcs"),
)

# Energy Gap (BCS)
bcs_gap = EquationNode(
    id="bcs_energy_gap",
    name="BCS Energy Gap",
    domain="condensed_matter",
    latex=r"\Delta(0) = 1.76 k_B T_c",
    sympy="Delta_0 = 1.76*k_B*T_c",
    variables=(("Delta_0", "Energy gap at T=0", "J"), ("T_c", "Critical temperature", "K")),
    description="Superconducting gap at zero temperature.",
    derives_from=("bcs_critical_temperature",),
    uses=("k_B",),
    status=NodeStatus.PROVEN,
    tags=("superconductivity", "gap"),
)

# London Penetration Depth
london_depth = EquationNode(
    id="london_penetration_depth",
    name="London Penetration Depth",
    domain="condensed_matter",
    latex=r"\lambda_L = \sqrt{\frac{m}{\mu_0 n_s e^2}}",
    sympy="lambda_L = sqrt(m/(mu_0*n_s*e**2))",
    variables=(("lambda_L", "Penetration depth", "m"), ("m", "Electron mass", "kg"), ("n_s", "Superfluid density", "m⁻³")),
    description="Magnetic field penetration into superconductor. ~10-100 nm.",
    uses=("mu_0", "e"),
    status=NodeStatus.PROVEN,
    tags=("superconductivity", "meissner"),
)

# London Equation
london_equation = EquationNode(
    id="london_equation",
    name="London Equation",
    domain="condensed_matter",
    latex=r"\nabla^2 \vec{B} = \frac{\vec{B}}{\lambda_L^2}",
    sympy="laplacian(B) = B/lambda_L**2",
    variables=(("B", "Magnetic field", "T"), ("lambda_L", "London depth", "m")),
    description="Describes field decay in superconductor. B(x) = B_0 exp(-x/λ_L).",
    derives_from=("london_penetration_depth",),
    status=NodeStatus.PROVEN,
    tags=("superconductivity", "field"),
)

# Coherence Length
coherence_length = EquationNode(
    id="coherence_length",
    name="BCS Coherence Length",
    domain="condensed_matter",
    latex=r"\xi_0 = \frac{\hbar v_F}{\pi \Delta} \approx \frac{0.18 \hbar v_F}{k_B T_c}",
    sympy="xi_0 = hbar*v_F/(pi*Delta)",
    variables=(("xi_0", "Coherence length", "m"), ("v_F", "Fermi velocity", "m/s"), ("Delta", "Energy gap", "J")),
    description="Size of Cooper pair. ~100-1000 nm for conventional superconductors.",
    uses=("hbar",),
    status=NodeStatus.PROVEN,
    tags=("superconductivity", "coherence"),
)

# Ginzburg-Landau Parameter
gl_parameter = EquationNode(
    id="ginzburg_landau_parameter",
    name="Ginzburg-Landau Parameter",
    domain="condensed_matter",
    latex=r"\kappa = \frac{\lambda_L}{\xi}",
    sympy="kappa = lambda_L/xi",
    variables=(("kappa", "GL parameter", "dimensionless"), ("lambda_L", "Penetration depth", "m"), ("xi", "Coherence length", "m")),
    description="κ < 1/√2: Type I (full Meissner). κ > 1/√2: Type II (vortices).",
    derives_from=("london_penetration_depth", "coherence_length"),
    status=NodeStatus.PROVEN,
    tags=("superconductivity", "type"),
)

# Critical Field (Type I)
critical_field_type1 = EquationNode(
    id="critical_field_type1",
    name="Thermodynamic Critical Field",
    domain="condensed_matter",
    latex=r"H_c = \frac{\Delta}{\sqrt{2}\mu_0\lambda_L\xi}",
    sympy="H_c = Delta/(sqrt(2)*mu_0*lambda_L*xi)",
    variables=(("H_c", "Critical field", "A/m"), ("Delta", "Energy gap", "J")),
    description="Field that destroys superconductivity in Type I.",
    uses=("mu_0",),
    status=NodeStatus.PROVEN,
    tags=("superconductivity", "critical_field"),
)

# Critical Fields (Type II)
critical_fields_type2 = EquationNode(
    id="critical_fields_type2",
    name="Type II Critical Fields",
    domain="condensed_matter",
    latex=r"H_{c1} = \frac{\phi_0}{4\pi\lambda_L^2}\ln\kappa, \quad H_{c2} = \frac{\phi_0}{2\pi\xi^2}",
    sympy="H_c1 = phi_0/(4*pi*lambda_L**2)*ln(kappa)",
    variables=(("H_c1", "Lower critical field", "A/m"), ("H_c2", "Upper critical field", "A/m"), ("phi_0", "Flux quantum", "Wb")),
    description="H < Hc1: Meissner. Hc1 < H < Hc2: mixed state. H > Hc2: normal.",
    uses=("phi_0",),
    status=NodeStatus.PROVEN,
    tags=("superconductivity", "type_II"),
)

# Flux Quantization
flux_quantization = EquationNode(
    id="flux_quantization",
    name="Flux Quantization",
    domain="condensed_matter",
    latex=r"\Phi = n\phi_0 = n\frac{h}{2e}",
    sympy="Phi = n*h/(2*e)",
    variables=(("Phi", "Magnetic flux", "Wb"), ("n", "Integer", "dimensionless"), ("phi_0", "Flux quantum ≈2.07×10⁻¹⁵ Wb", "Wb")),
    description="Flux through superconducting loop is quantized. 2e from Cooper pairs.",
    uses=("h", "e"),
    status=NodeStatus.EXPERIMENTAL,
    tags=("superconductivity", "quantization"),
)

# Josephson Current
josephson_current = EquationNode(
    id="josephson_current",
    name="DC Josephson Effect",
    domain="condensed_matter",
    latex=r"I = I_c \sin\phi",
    sympy="I = I_c*sin(phi)",
    variables=(("I", "Supercurrent", "A"), ("I_c", "Critical current", "A"), ("phi", "Phase difference", "rad")),
    description="Supercurrent through junction depends on phase difference.",
    status=NodeStatus.EXPERIMENTAL,
    tags=("josephson", "junction"),
)

# AC Josephson Effect
josephson_voltage = EquationNode(
    id="josephson_voltage",
    name="AC Josephson Effect",
    domain="condensed_matter",
    latex=r"V = \frac{\hbar}{2e}\frac{d\phi}{dt} = \frac{\phi_0}{2\pi}\frac{d\phi}{dt}",
    sympy="V = hbar/(2*e) * dphi/dt",
    variables=(("V", "Voltage", "V"), ("phi", "Phase", "rad")),
    description="Voltage produces oscillating supercurrent. f = 2eV/h ≈ 483.6 GHz/mV.",
    uses=("hbar", "e"),
    status=NodeStatus.EXPERIMENTAL,
    tags=("josephson", "frequency"),
)

# SQUID
squid = EquationNode(
    id="squid",
    name="SQUID Flux Response",
    domain="condensed_matter",
    latex=r"I_c(\Phi) = 2I_0\left|\cos\left(\frac{\pi\Phi}{\phi_0}\right)\right|",
    sympy="I_c = 2*I_0*|cos(pi*Phi/phi_0)|",
    variables=(("I_c", "Critical current", "A"), ("I_0", "Single junction critical current", "A"), ("Phi", "Total flux", "Wb")),
    description="SQUID critical current modulated by flux. Ultra-sensitive magnetometer.",
    derives_from=("josephson_current", "flux_quantization"),
    status=NodeStatus.PROVEN,
    tags=("squid", "magnetometer"),
)

# Meissner Effect
meissner_effect = EquationNode(
    id="meissner_effect",
    name="Meissner Effect",
    domain="condensed_matter",
    latex=r"\vec{B} = 0 \text{ inside superconductor}",
    sympy="B_inside = 0",
    variables=(),
    description="Perfect diamagnetism. Field expelled when T < T_c.",
    status=NodeStatus.EXPERIMENTAL,
    tags=("superconductivity", "diamagnetic"),
)

NODES = [
    bcs_tc, bcs_gap, london_depth, london_equation, coherence_length,
    gl_parameter, critical_field_type1, critical_fields_type2, flux_quantization,
    josephson_current, josephson_voltage, squid, meissner_effect
]
