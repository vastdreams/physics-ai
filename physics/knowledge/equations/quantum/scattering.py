"""
PATH: physics/knowledge/equations/quantum/scattering.py
PURPOSE: Quantum scattering theory equations
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Differential Cross Section
differential_cross_section = EquationNode(
    id="differential_cross_section",
    name="Differential Cross Section",
    domain="quantum_mechanics",
    latex=r"\frac{d\sigma}{d\Omega} = |f(\theta,\phi)|^2",
    sympy="dsigma/dOmega = |f(theta)|**2",
    variables=(("dsigma/dOmega", "Differential cross section", "m²/sr"), ("f", "Scattering amplitude", "m")),
    description="Probability of scattering into solid angle dΩ.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("scattering", "cross_section"),
)

# Total Cross Section
total_cross_section = EquationNode(
    id="total_cross_section_qm",
    name="Total Cross Section",
    domain="quantum_mechanics",
    latex=r"\sigma_{tot} = \int \frac{d\sigma}{d\Omega} d\Omega = 2\pi\int_0^\pi |f(\theta)|^2 \sin\theta \, d\theta",
    sympy="sigma_tot = 2*pi*integral(|f|**2*sin(theta), theta, 0, pi)",
    variables=(("sigma_tot", "Total cross section", "m²")),
    description="Total scattering cross section integrating over all angles.",
    derives_from=("differential_cross_section",),
    status=NodeStatus.PROVEN,
    tags=("scattering", "cross_section"),
)

# Optical Theorem
optical_theorem = EquationNode(
    id="optical_theorem",
    name="Optical Theorem",
    domain="quantum_mechanics",
    latex=r"\sigma_{tot} = \frac{4\pi}{k}\text{Im}[f(0)]",
    sympy="sigma_tot = 4*pi/k * Im(f(0))",
    variables=(("sigma_tot", "Total cross section", "m²"), ("k", "Wave number", "m⁻¹"), ("f(0)", "Forward scattering amplitude", "m")),
    description="Total cross section from imaginary part of forward scattering amplitude.",
    status=NodeStatus.PROVEN,
    tags=("scattering", "unitarity"),
)

# Born Approximation
born_approximation = EquationNode(
    id="born_approximation",
    name="Born Approximation",
    domain="quantum_mechanics",
    latex=r"f^{(1)}(\vec{q}) = -\frac{m}{2\pi\hbar^2}\int V(\vec{r})e^{-i\vec{q}\cdot\vec{r}} d^3r",
    sympy="f_1 = -m/(2*pi*hbar**2) * integral(V*exp(-i*q*r), r)",
    variables=(("f_1", "First Born amplitude", "m"), ("q", "Momentum transfer", "m⁻¹"), ("V", "Potential", "J")),
    description="Scattering amplitude as Fourier transform of potential. Valid for weak potentials.",
    uses=("hbar",),
    status=NodeStatus.PROVEN,
    tags=("scattering", "approximation"),
)

# Partial Wave Expansion
partial_wave = EquationNode(
    id="partial_wave_expansion",
    name="Partial Wave Expansion",
    domain="quantum_mechanics",
    latex=r"f(\theta) = \sum_{l=0}^{\infty}(2l+1)f_l P_l(\cos\theta), \quad f_l = \frac{e^{2i\delta_l}-1}{2ik}",
    sympy="f = sum((2*l+1)*f_l*P_l(cos(theta)))",
    variables=(("f_l", "Partial wave amplitude", "m"), ("delta_l", "Phase shift", "rad"), ("P_l", "Legendre polynomial", "dimensionless")),
    description="Expansion in angular momentum eigenstates. Each l contributes phase shift.",
    status=NodeStatus.PROVEN,
    tags=("scattering", "partial_wave"),
)

# Phase Shift
phase_shift_cross_section = EquationNode(
    id="phase_shift_cross_section",
    name="Cross Section from Phase Shifts",
    domain="quantum_mechanics",
    latex=r"\sigma_{tot} = \frac{4\pi}{k^2}\sum_{l=0}^{\infty}(2l+1)\sin^2\delta_l",
    sympy="sigma_tot = 4*pi/k**2 * sum((2*l+1)*sin(delta_l)**2)",
    variables=(("delta_l", "Phase shift for partial wave l", "rad")),
    description="Total cross section from partial wave phase shifts.",
    derives_from=("partial_wave_expansion",),
    status=NodeStatus.PROVEN,
    tags=("scattering", "phase_shift"),
)

# Unitarity Bound
unitarity_bound = EquationNode(
    id="unitarity_bound",
    name="Unitarity Bound on Partial Waves",
    domain="quantum_mechanics",
    latex=r"\sigma_l \leq \frac{4\pi(2l+1)}{k^2}",
    sympy="sigma_l <= 4*pi*(2*l+1)/k**2",
    variables=(("sigma_l", "Partial cross section", "m²")),
    description="Maximum cross section for partial wave l. Saturated when δ_l = π/2.",
    derives_from=("phase_shift_cross_section",),
    status=NodeStatus.PROVEN,
    tags=("scattering", "unitarity"),
)

# S-Matrix
s_matrix = EquationNode(
    id="s_matrix",
    name="S-Matrix",
    domain="quantum_mechanics",
    latex=r"S_{fi} = \langle f|S|i\rangle = \delta_{fi} + 2\pi i \delta(E_f - E_i)T_{fi}",
    sympy="S_fi = delta_fi + 2*pi*i*delta(E_f-E_i)*T_fi",
    variables=(("S", "S-matrix", "dimensionless"), ("T", "T-matrix", "varies")),
    description="Transition matrix between asymptotic states. Unitary: S†S = 1.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("scattering", "s_matrix"),
)

# Lippmann-Schwinger Equation
lippmann_schwinger = EquationNode(
    id="lippmann_schwinger",
    name="Lippmann-Schwinger Equation",
    domain="quantum_mechanics",
    latex=r"|\psi^{(\pm)}\rangle = |\phi\rangle + G_0^{(\pm)}V|\psi^{(\pm)}\rangle",
    sympy="|psi> = |phi> + G_0*V*|psi>",
    variables=(("psi", "Scattering state", "m^(-3/2)"), ("phi", "Free state", "m^(-3/2)"), ("G_0", "Free Green's function", "J⁻¹"), ("V", "Potential", "J")),
    description="Integral equation for scattering states. Can be iterated for Born series.",
    status=NodeStatus.PROVEN,
    tags=("scattering", "integral_equation"),
)

# Low Energy Scattering
scattering_length = EquationNode(
    id="scattering_length",
    name="Scattering Length",
    domain="quantum_mechanics",
    latex=r"f(k \to 0) = -a, \quad \sigma \to 4\pi a^2 \text{ (distinguishable)}",
    sympy="f_0 = -a",
    variables=(("a", "Scattering length", "m")),
    description="Low-energy limit of scattering. a > 0: weak attraction or repulsion. a < 0: near bound state.",
    status=NodeStatus.PROVEN,
    tags=("scattering", "low_energy"),
)

# Resonance
resonance = EquationNode(
    id="scattering_resonance",
    name="Scattering Resonance",
    domain="quantum_mechanics",
    latex=r"\delta_l \to \frac{\pi}{2} \text{ at } E = E_r, \quad \sigma \to \frac{4\pi(2l+1)}{k^2}",
    sympy="delta_l = pi/2 at E = E_r",
    variables=(("E_r", "Resonance energy", "J")),
    description="Phase shift passes through π/2 at resonance. Cross section peaks.",
    derives_from=("phase_shift_cross_section",),
    status=NodeStatus.PROVEN,
    tags=("scattering", "resonance"),
)

NODES = [
    differential_cross_section, total_cross_section, optical_theorem, born_approximation,
    partial_wave, phase_shift_cross_section, unitarity_bound, s_matrix,
    lippmann_schwinger, scattering_length, resonance
]
