"""
PATH: physics/knowledge/equations/electromagnetism/waves.py
PURPOSE: Electromagnetic wave equations and properties
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Wave Equation (General)
wave_equation = EquationNode(
    id="wave_equation",
    name="Wave Equation",
    domain="waves",
    latex=r"\frac{\partial^2 u}{\partial x^2} = \frac{1}{v^2}\frac{\partial^2 u}{\partial t^2}",
    sympy="d2u/dx2 = (1/v**2) * d2u/dt2",
    variables=(
        ("u", "Wave displacement", "varies"),
        ("x", "Position", "m"),
        ("t", "Time", "s"),
        ("v", "Wave speed", "m/s"),
    ),
    description="General wave equation for non-dispersive waves. "
                "Solutions are f(x ± vt).",
    status=NodeStatus.FUNDAMENTAL,
    tags=("waves", "differential_equation"),
)

# Wavelength-Frequency Relation
wavelength_frequency = EquationNode(
    id="wavelength_frequency",
    name="Wavelength-Frequency Relation",
    domain="waves",
    latex=r"v = f\lambda \quad \omega = 2\pi f \quad k = \frac{2\pi}{\lambda}",
    sympy="v = f * lambda",
    variables=(
        ("v", "Wave speed", "m/s"),
        ("f", "Frequency", "Hz"),
        ("lambda", "Wavelength", "m"),
        ("omega", "Angular frequency", "rad/s"),
        ("k", "Wave number", "rad/m"),
    ),
    description="Fundamental relation for all periodic waves.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("waves", "frequency", "wavelength"),
)

# Poynting Vector
poynting_vector = EquationNode(
    id="poynting_vector",
    name="Poynting Vector",
    domain="electromagnetism",
    latex=r"\vec{S} = \frac{1}{\mu_0}\vec{E} \times \vec{B}",
    sympy="S = (1/mu_0) * E cross B",
    variables=(
        ("S", "Energy flux", "W/m²"),
        ("E", "Electric field", "V/m"),
        ("B", "Magnetic field", "T"),
        ("mu_0", "Vacuum permeability", "H/m"),
    ),
    description="Electromagnetic energy flow per unit area. Direction is "
                "propagation direction. Magnitude is intensity.",
    derives_from=("em_wave_equation",),
    uses=("mu_0",),
    discoverer="John Henry Poynting",
    year=1884,
    status=NodeStatus.PROVEN,
    tags=("energy", "intensity", "power"),
)

# Intensity
intensity = EquationNode(
    id="em_intensity",
    name="Electromagnetic Intensity",
    domain="electromagnetism",
    latex=r"I = \langle S \rangle = \frac{1}{2}c\varepsilon_0 E_0^2 = \frac{E_0^2}{2\mu_0 c}",
    sympy="I = (1/2) * c * epsilon_0 * E_0**2",
    variables=(
        ("I", "Intensity (time-averaged)", "W/m²"),
        ("E_0", "Electric field amplitude", "V/m"),
        ("c", "Speed of light", "m/s"),
    ),
    description="Time-averaged power per unit area. "
                "For EM waves, I ∝ E₀².",
    derives_from=("poynting_vector",),
    uses=("c", "epsilon_0"),
    status=NodeStatus.PROVEN,
    tags=("intensity", "power", "average"),
)

# Radiation Pressure
radiation_pressure = EquationNode(
    id="radiation_pressure",
    name="Radiation Pressure",
    domain="electromagnetism",
    latex=r"P = \frac{I}{c} \text{ (absorbed)} \quad P = \frac{2I}{c} \text{ (reflected)}",
    sympy="P = I / c",
    variables=(
        ("P", "Radiation pressure", "Pa"),
        ("I", "Intensity", "W/m²"),
        ("c", "Speed of light", "m/s"),
    ),
    description="Momentum transfer from EM waves to surfaces. "
                "Doubled for perfect reflection.",
    derives_from=("poynting_vector",),
    uses=("c",),
    discoverer="James Clerk Maxwell",
    year=1873,
    status=NodeStatus.PROVEN,
    tags=("pressure", "momentum", "photon"),
)

# Export all nodes
NODES = [wave_equation, wavelength_frequency, poynting_vector, intensity, radiation_pressure]
