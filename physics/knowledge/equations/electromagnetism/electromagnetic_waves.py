"""
PATH: physics/knowledge/equations/electromagnetism/electromagnetic_waves.py
PURPOSE: Electromagnetic wave equations and related phenomena
"""

from physics.knowledge.base import EquationNode

NODES = [
    # EM Wave Equation
    EquationNode(
        id="em_wave_equation",
        name="Electromagnetic Wave Equation",
        description="Wave equation for electromagnetic fields in vacuum",
        latex=r"\nabla^2 \mathbf{E} = \mu_0\epsilon_0 \frac{\partial^2 \mathbf{E}}{\partial t^2}",
        sympy="nabla2_E = mu_0 * epsilon_0 * d2E/dt2",
        variables=[
            ("E", "Electric field", "V/m"),
            ("mu_0", "Permeability of free space", "H/m"),
            ("epsilon_0", "Permittivity of free space", "F/m"),
        ],
        domain="electromagnetism",
        tags=["waves", "maxwell"],
    ),
    
    # Speed of Light from Maxwell
    EquationNode(
        id="speed_of_light_maxwell",
        name="Speed of Light from Maxwell's Equations",
        description="Speed of light derived from electromagnetic constants",
        latex=r"c = \frac{1}{\sqrt{\mu_0\epsilon_0}}",
        sympy="c = 1 / sqrt(mu_0 * epsilon_0)",
        variables=[
            ("c", "Speed of light", "m/s"),
            ("mu_0", "Permeability of free space", "H/m"),
            ("epsilon_0", "Permittivity of free space", "F/m"),
        ],
        domain="electromagnetism",
        tags=["waves", "fundamental"],
    ),
    
    # Poynting Vector
    EquationNode(
        id="poynting_vector",
        name="Poynting Vector",
        description="Energy flux density of electromagnetic field",
        latex=r"\mathbf{S} = \frac{1}{\mu_0}\mathbf{E} \times \mathbf{B}",
        sympy="S = E x B / mu_0",
        variables=[
            ("S", "Poynting vector", "W/m^2"),
            ("E", "Electric field", "V/m"),
            ("B", "Magnetic field", "T"),
            ("mu_0", "Permeability of free space", "H/m"),
        ],
        domain="electromagnetism",
        tags=["waves", "energy", "poynting"],
    ),
    
    # Wave Intensity
    EquationNode(
        id="em_wave_intensity",
        name="EM Wave Intensity",
        description="Time-averaged intensity of electromagnetic wave",
        latex=r"I = \frac{1}{2}c\epsilon_0 E_0^2 = \frac{c B_0^2}{2\mu_0}",
        sympy="I = c * epsilon_0 * E_0**2 / 2",
        variables=[
            ("I", "Intensity", "W/m^2"),
            ("c", "Speed of light", "m/s"),
            ("epsilon_0", "Permittivity", "F/m"),
            ("E_0", "Electric field amplitude", "V/m"),
            ("B_0", "Magnetic field amplitude", "T"),
        ],
        domain="electromagnetism",
        tags=["waves", "intensity"],
    ),
    
    # Radiation Pressure
    EquationNode(
        id="radiation_pressure",
        name="Radiation Pressure",
        description="Pressure exerted by electromagnetic radiation",
        latex=r"P = \frac{I}{c} \text{ (absorbed)}, \quad P = \frac{2I}{c} \text{ (reflected)}",
        sympy="P = I / c",
        variables=[
            ("P", "Radiation pressure", "Pa"),
            ("I", "Intensity", "W/m^2"),
            ("c", "Speed of light", "m/s"),
        ],
        domain="electromagnetism",
        tags=["waves", "pressure", "momentum"],
    ),
    
    # Dispersion Relation
    EquationNode(
        id="dispersion_relation_em",
        name="Dispersion Relation",
        description="Relationship between frequency and wave vector",
        latex=r"\omega = c|\mathbf{k}|",
        sympy="omega = c * k",
        variables=[
            ("omega", "Angular frequency", "rad/s"),
            ("c", "Speed of light", "m/s"),
            ("k", "Wave vector magnitude", "1/m"),
        ],
        domain="electromagnetism",
        tags=["waves", "dispersion"],
    ),
    
    # Refractive Index
    EquationNode(
        id="refractive_index",
        name="Refractive Index",
        description="Ratio of light speed in vacuum to medium",
        latex=r"n = \frac{c}{v} = \sqrt{\epsilon_r \mu_r}",
        sympy="n = c / v",
        variables=[
            ("n", "Refractive index", "dimensionless"),
            ("c", "Speed of light in vacuum", "m/s"),
            ("v", "Speed of light in medium", "m/s"),
            ("epsilon_r", "Relative permittivity", "dimensionless"),
            ("mu_r", "Relative permeability", "dimensionless"),
        ],
        domain="electromagnetism",
        tags=["waves", "optics", "refraction"],
    ),
    
    # Snell's Law
    EquationNode(
        id="snells_law",
        name="Snell's Law",
        description="Law of refraction at interface",
        latex=r"n_1 \sin\theta_1 = n_2 \sin\theta_2",
        sympy="n_1 * sin(theta_1) = n_2 * sin(theta_2)",
        variables=[
            ("n_1", "Refractive index 1", "dimensionless"),
            ("n_2", "Refractive index 2", "dimensionless"),
            ("theta_1", "Incident angle", "rad"),
            ("theta_2", "Refracted angle", "rad"),
        ],
        domain="electromagnetism",
        tags=["waves", "optics", "refraction"],
    ),
    
    # Fresnel Equations (Reflection)
    EquationNode(
        id="fresnel_reflection_s",
        name="Fresnel Reflection (s-polarization)",
        description="Reflection coefficient for s-polarized light",
        latex=r"r_s = \frac{n_1\cos\theta_i - n_2\cos\theta_t}{n_1\cos\theta_i + n_2\cos\theta_t}",
        sympy="r_s = (n_1 * cos(theta_i) - n_2 * cos(theta_t)) / (n_1 * cos(theta_i) + n_2 * cos(theta_t))",
        variables=[
            ("r_s", "Reflection coefficient", "dimensionless"),
            ("n_1", "Refractive index 1", "dimensionless"),
            ("n_2", "Refractive index 2", "dimensionless"),
            ("theta_i", "Incident angle", "rad"),
            ("theta_t", "Transmitted angle", "rad"),
        ],
        domain="electromagnetism",
        tags=["waves", "optics", "fresnel"],
    ),
    
    # Fresnel Equations (p-polarization)
    EquationNode(
        id="fresnel_reflection_p",
        name="Fresnel Reflection (p-polarization)",
        description="Reflection coefficient for p-polarized light",
        latex=r"r_p = \frac{n_2\cos\theta_i - n_1\cos\theta_t}{n_2\cos\theta_i + n_1\cos\theta_t}",
        sympy="r_p = (n_2 * cos(theta_i) - n_1 * cos(theta_t)) / (n_2 * cos(theta_i) + n_1 * cos(theta_t))",
        variables=[
            ("r_p", "Reflection coefficient", "dimensionless"),
            ("n_1", "Refractive index 1", "dimensionless"),
            ("n_2", "Refractive index 2", "dimensionless"),
        ],
        domain="electromagnetism",
        tags=["waves", "optics", "fresnel"],
    ),
    
    # Brewster's Angle
    EquationNode(
        id="brewsters_angle",
        name="Brewster's Angle",
        description="Angle at which p-polarized light is not reflected",
        latex=r"\tan\theta_B = \frac{n_2}{n_1}",
        sympy="tan(theta_B) = n_2 / n_1",
        variables=[
            ("theta_B", "Brewster's angle", "rad"),
            ("n_1", "Refractive index 1", "dimensionless"),
            ("n_2", "Refractive index 2", "dimensionless"),
        ],
        domain="electromagnetism",
        tags=["waves", "optics", "polarization"],
    ),
    
    # Critical Angle
    EquationNode(
        id="critical_angle",
        name="Critical Angle",
        description="Angle for total internal reflection",
        latex=r"\sin\theta_c = \frac{n_2}{n_1}",
        sympy="sin(theta_c) = n_2 / n_1",
        variables=[
            ("theta_c", "Critical angle", "rad"),
            ("n_1", "Refractive index 1 (higher)", "dimensionless"),
            ("n_2", "Refractive index 2 (lower)", "dimensionless"),
        ],
        domain="electromagnetism",
        tags=["waves", "optics", "total_internal_reflection"],
    ),
    
    # Malus's Law
    EquationNode(
        id="malus_law",
        name="Malus's Law",
        description="Intensity of polarized light through analyzer",
        latex=r"I = I_0 \cos^2\theta",
        sympy="I = I_0 * cos(theta)**2",
        variables=[
            ("I", "Transmitted intensity", "W/m^2"),
            ("I_0", "Incident intensity", "W/m^2"),
            ("theta", "Angle between polarizers", "rad"),
        ],
        domain="electromagnetism",
        tags=["waves", "optics", "polarization"],
    ),
    
    # Skin Depth
    EquationNode(
        id="skin_depth",
        name="Skin Depth",
        description="Depth of electromagnetic penetration in conductor",
        latex=r"\delta = \sqrt{\frac{2}{\omega\mu\sigma}}",
        sympy="delta = sqrt(2 / (omega * mu * sigma))",
        variables=[
            ("delta", "Skin depth", "m"),
            ("omega", "Angular frequency", "rad/s"),
            ("mu", "Permeability", "H/m"),
            ("sigma", "Conductivity", "S/m"),
        ],
        domain="electromagnetism",
        tags=["waves", "conductor", "skin_effect"],
    ),
    
    # Plasma Frequency
    EquationNode(
        id="plasma_frequency",
        name="Plasma Frequency",
        description="Natural oscillation frequency of plasma",
        latex=r"\omega_p = \sqrt{\frac{n_e e^2}{m_e \epsilon_0}}",
        sympy="omega_p = sqrt(n_e * e**2 / (m_e * epsilon_0))",
        variables=[
            ("omega_p", "Plasma frequency", "rad/s"),
            ("n_e", "Electron density", "1/m^3"),
            ("e", "Electron charge", "C"),
            ("m_e", "Electron mass", "kg"),
            ("epsilon_0", "Permittivity", "F/m"),
        ],
        domain="electromagnetism",
        tags=["waves", "plasma"],
    ),
    
    # Group Velocity
    EquationNode(
        id="group_velocity",
        name="Group Velocity",
        description="Velocity of wave packet envelope",
        latex=r"v_g = \frac{d\omega}{dk}",
        sympy="v_g = d_omega / dk",
        variables=[
            ("v_g", "Group velocity", "m/s"),
            ("omega", "Angular frequency", "rad/s"),
            ("k", "Wave number", "1/m"),
        ],
        domain="electromagnetism",
        tags=["waves", "dispersion"],
    ),
    
    # Phase Velocity
    EquationNode(
        id="phase_velocity",
        name="Phase Velocity",
        description="Velocity of constant phase surface",
        latex=r"v_p = \frac{\omega}{k}",
        sympy="v_p = omega / k",
        variables=[
            ("v_p", "Phase velocity", "m/s"),
            ("omega", "Angular frequency", "rad/s"),
            ("k", "Wave number", "1/m"),
        ],
        domain="electromagnetism",
        tags=["waves", "phase"],
    ),
]
