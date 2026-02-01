"""
PATH: physics/knowledge/equations/classical/gravitation.py
PURPOSE: Classical gravitational equations and orbital mechanics
"""

from physics.knowledge.base import EquationNode

NODES = [
    # Newton's Law of Universal Gravitation
    EquationNode(
        id="newton_gravitation",
        name="Newton's Law of Universal Gravitation",
        description="Gravitational force between two masses is proportional to their product and inversely proportional to square of distance",
        latex=r"F = G \frac{m_1 m_2}{r^2}",
        sympy="F = G * m1 * m2 / r**2",
        variables=[
            ("F", "Gravitational force", "N"),
            ("G", "Gravitational constant", "N m^2/kg^2"),
            ("m1", "First mass", "kg"),
            ("m2", "Second mass", "kg"),
            ("r", "Distance between centers", "m"),
        ],
        domain="classical_mechanics",
        tags=["gravity", "inverse_square", "fundamental"],
    ),
    
    # Gravitational Field Strength
    EquationNode(
        id="gravitational_field",
        name="Gravitational Field Strength",
        description="Gravitational field strength at distance r from mass M",
        latex=r"g = \frac{GM}{r^2}",
        sympy="g = G * M / r**2",
        variables=[
            ("g", "Gravitational field strength", "m/s^2"),
            ("G", "Gravitational constant", "N m^2/kg^2"),
            ("M", "Source mass", "kg"),
            ("r", "Distance from center", "m"),
        ],
        domain="classical_mechanics",
        tags=["gravity", "field"],
    ),
    
    # Gravitational Potential Energy
    EquationNode(
        id="gravitational_potential_energy",
        name="Gravitational Potential Energy",
        description="Potential energy in a gravitational field",
        latex=r"U = -\frac{GMm}{r}",
        sympy="U = -G * M * m / r",
        variables=[
            ("U", "Gravitational potential energy", "J"),
            ("G", "Gravitational constant", "N m^2/kg^2"),
            ("M", "Source mass", "kg"),
            ("m", "Test mass", "kg"),
            ("r", "Distance", "m"),
        ],
        domain="classical_mechanics",
        tags=["gravity", "potential_energy"],
    ),
    
    # Escape Velocity
    EquationNode(
        id="escape_velocity",
        name="Escape Velocity",
        description="Minimum velocity needed to escape gravitational field",
        latex=r"v_{esc} = \sqrt{\frac{2GM}{r}}",
        sympy="v_esc = sqrt(2 * G * M / r)",
        variables=[
            ("v_esc", "Escape velocity", "m/s"),
            ("G", "Gravitational constant", "N m^2/kg^2"),
            ("M", "Mass of body", "kg"),
            ("r", "Distance from center", "m"),
        ],
        domain="classical_mechanics",
        tags=["gravity", "escape", "velocity"],
    ),
    
    # Orbital Velocity
    EquationNode(
        id="orbital_velocity",
        name="Circular Orbital Velocity",
        description="Velocity for circular orbit at radius r",
        latex=r"v_{orb} = \sqrt{\frac{GM}{r}}",
        sympy="v_orb = sqrt(G * M / r)",
        variables=[
            ("v_orb", "Orbital velocity", "m/s"),
            ("G", "Gravitational constant", "N m^2/kg^2"),
            ("M", "Central mass", "kg"),
            ("r", "Orbital radius", "m"),
        ],
        domain="classical_mechanics",
        tags=["gravity", "orbital", "velocity"],
    ),
    
    # Orbital Period (Kepler's Third Law)
    EquationNode(
        id="kepler_third_law",
        name="Kepler's Third Law",
        description="Orbital period squared is proportional to semi-major axis cubed",
        latex=r"T^2 = \frac{4\pi^2 a^3}{GM}",
        sympy="T**2 = 4 * pi**2 * a**3 / (G * M)",
        variables=[
            ("T", "Orbital period", "s"),
            ("a", "Semi-major axis", "m"),
            ("G", "Gravitational constant", "N m^2/kg^2"),
            ("M", "Central mass", "kg"),
        ],
        domain="classical_mechanics",
        tags=["kepler", "orbital", "period"],
    ),
    
    # Gravitational Potential
    EquationNode(
        id="gravitational_potential",
        name="Gravitational Potential",
        description="Gravitational potential at distance r from mass M",
        latex=r"\phi = -\frac{GM}{r}",
        sympy="phi = -G * M / r",
        variables=[
            ("phi", "Gravitational potential", "J/kg"),
            ("G", "Gravitational constant", "N m^2/kg^2"),
            ("M", "Source mass", "kg"),
            ("r", "Distance", "m"),
        ],
        domain="classical_mechanics",
        tags=["gravity", "potential"],
    ),
    
    # Vis-viva Equation
    EquationNode(
        id="vis_viva",
        name="Vis-viva Equation",
        description="Orbital velocity at any point in an elliptical orbit",
        latex=r"v^2 = GM\left(\frac{2}{r} - \frac{1}{a}\right)",
        sympy="v**2 = G * M * (2/r - 1/a)",
        variables=[
            ("v", "Orbital velocity", "m/s"),
            ("G", "Gravitational constant", "N m^2/kg^2"),
            ("M", "Central mass", "kg"),
            ("r", "Current distance", "m"),
            ("a", "Semi-major axis", "m"),
        ],
        domain="classical_mechanics",
        tags=["orbital", "ellipse", "velocity"],
    ),
    
    # Schwarzschild Radius
    EquationNode(
        id="schwarzschild_radius",
        name="Schwarzschild Radius",
        description="Event horizon radius of a non-rotating black hole",
        latex=r"r_s = \frac{2GM}{c^2}",
        sympy="r_s = 2 * G * M / c**2",
        variables=[
            ("r_s", "Schwarzschild radius", "m"),
            ("G", "Gravitational constant", "N m^2/kg^2"),
            ("M", "Mass", "kg"),
            ("c", "Speed of light", "m/s"),
        ],
        domain="classical_mechanics",
        tags=["black_hole", "event_horizon"],
    ),
    
    # Tidal Force
    EquationNode(
        id="tidal_force",
        name="Tidal Force",
        description="Differential gravitational force causing tides",
        latex=r"F_{tidal} = \frac{2GMmr}{d^3}",
        sympy="F_tidal = 2 * G * M * m * r / d**3",
        variables=[
            ("F_tidal", "Tidal force", "N"),
            ("G", "Gravitational constant", "N m^2/kg^2"),
            ("M", "Mass of perturbing body", "kg"),
            ("m", "Mass of affected body", "kg"),
            ("r", "Radius of affected body", "m"),
            ("d", "Distance between centers", "m"),
        ],
        domain="classical_mechanics",
        tags=["gravity", "tidal"],
    ),
    
    # Roche Limit
    EquationNode(
        id="roche_limit",
        name="Roche Limit",
        description="Distance within which a body is torn apart by tidal forces",
        latex=r"d = R_M \left(2\frac{\rho_M}{\rho_m}\right)^{1/3}",
        sympy="d = R_M * (2 * rho_M / rho_m)**(1/3)",
        variables=[
            ("d", "Roche limit distance", "m"),
            ("R_M", "Radius of primary", "m"),
            ("rho_M", "Density of primary", "kg/m^3"),
            ("rho_m", "Density of satellite", "kg/m^3"),
        ],
        domain="classical_mechanics",
        tags=["gravity", "tidal", "roche"],
    ),
    
    # Gravitational Binding Energy
    EquationNode(
        id="gravitational_binding_energy",
        name="Gravitational Binding Energy",
        description="Energy required to disperse a spherical mass to infinity",
        latex=r"U = \frac{3GM^2}{5R}",
        sympy="U = 3 * G * M**2 / (5 * R)",
        variables=[
            ("U", "Binding energy", "J"),
            ("G", "Gravitational constant", "N m^2/kg^2"),
            ("M", "Total mass", "kg"),
            ("R", "Radius", "m"),
        ],
        domain="classical_mechanics",
        tags=["gravity", "binding_energy"],
    ),
    
    # Specific Orbital Energy
    EquationNode(
        id="specific_orbital_energy",
        name="Specific Orbital Energy",
        description="Energy per unit mass in an orbit",
        latex=r"\epsilon = \frac{v^2}{2} - \frac{GM}{r} = -\frac{GM}{2a}",
        sympy="epsilon = v**2/2 - G*M/r",
        variables=[
            ("epsilon", "Specific orbital energy", "J/kg"),
            ("v", "Velocity", "m/s"),
            ("G", "Gravitational constant", "N m^2/kg^2"),
            ("M", "Central mass", "kg"),
            ("r", "Distance", "m"),
            ("a", "Semi-major axis", "m"),
        ],
        domain="classical_mechanics",
        tags=["orbital", "energy"],
    ),
    
    # Angular Momentum in Orbit
    EquationNode(
        id="orbital_angular_momentum",
        name="Orbital Angular Momentum",
        description="Specific angular momentum in orbit",
        latex=r"h = r \times v = \sqrt{GMa(1-e^2)}",
        sympy="h = sqrt(G * M * a * (1 - e**2))",
        variables=[
            ("h", "Specific angular momentum", "m^2/s"),
            ("G", "Gravitational constant", "N m^2/kg^2"),
            ("M", "Central mass", "kg"),
            ("a", "Semi-major axis", "m"),
            ("e", "Eccentricity", "dimensionless"),
        ],
        domain="classical_mechanics",
        tags=["orbital", "angular_momentum"],
    ),
    
    # Perihelion/Aphelion Distance
    EquationNode(
        id="perihelion_aphelion",
        name="Perihelion and Aphelion Distances",
        description="Closest and farthest distances in elliptical orbit",
        latex=r"r_p = a(1-e), \quad r_a = a(1+e)",
        sympy="r_p = a * (1 - e)",
        variables=[
            ("r_p", "Perihelion distance", "m"),
            ("r_a", "Aphelion distance", "m"),
            ("a", "Semi-major axis", "m"),
            ("e", "Eccentricity", "dimensionless"),
        ],
        domain="classical_mechanics",
        tags=["orbital", "ellipse"],
    ),
]
