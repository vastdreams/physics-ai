"""
PATH: physics/knowledge/equations/relativity/general.py
PURPOSE: General relativity equations

FIRST PRINCIPLES:
General relativity extends special relativity to non-inertial frames
and gravity. Key insight: gravity is geometry (curvature of spacetime).
Equivalence principle: locally, gravity and acceleration are indistinguishable.
"""

from physics.knowledge.base.node import EquationNode, PrincipleNode, NodeStatus

# Equivalence Principle
equivalence_principle = PrincipleNode(
    id="equivalence_principle",
    name="Equivalence Principle",
    domain="general_relativity",
    statement="A uniform gravitational field is locally indistinguishable "
              "from uniform acceleration.",
    mathematical_form="Inertial mass = gravitational mass",
    description="Einstein's 'happiest thought'. Leads to gravity as geometry. "
                "Tested to 10⁻¹⁵ precision.",
    discoverer="Albert Einstein",
    year=1907,
    leads_to=("einstein_field_equations",),
    tags=("postulate", "gravity", "geometry"),
)

# Einstein Field Equations
einstein_field = EquationNode(
    id="einstein_field_equations",
    name="Einstein Field Equations",
    domain="general_relativity",
    latex=r"G_{\mu\nu} + \Lambda g_{\mu\nu} = \frac{8\pi G}{c^4} T_{\mu\nu}",
    sympy="G_munu + Lambda * g_munu = (8*pi*G/c**4) * T_munu",
    variables=(
        ("G_munu", "Einstein tensor", "m⁻²"),
        ("g_munu", "Metric tensor", "(dimensionless)"),
        ("Lambda", "Cosmological constant", "m⁻²"),
        ("T_munu", "Stress-energy tensor", "J/m³"),
        ("G", "Gravitational constant", "m³/(kg⋅s²)"),
        ("c", "Speed of light", "m/s"),
    ),
    description="Mass-energy tells spacetime how to curve; curvature tells "
                "matter how to move. 10 coupled nonlinear PDEs.",
    derivation_steps=(
        "Require: Geometry (left) = Matter (right)",
        "Left side: Einstein tensor G_μν = R_μν - (1/2)Rg_μν",
        "Right side: 8πG/c⁴ T_μν (from Newtonian limit)",
        "Λg_μν added for cosmology",
    ),
    derives_from=("equivalence_principle",),
    uses=("G", "c"),
    leads_to=("schwarzschild_metric", "gravitational_waves", "cosmological_models"),
    discoverer="Albert Einstein",
    year=1915,
    status=NodeStatus.FUNDAMENTAL,
    tags=("field_equations", "curvature", "tensor"),
)

# Schwarzschild Metric
schwarzschild = EquationNode(
    id="schwarzschild_metric",
    name="Schwarzschild Metric",
    domain="general_relativity",
    latex=r"ds^2 = -\left(1-\frac{r_s}{r}\right)c^2dt^2 + \left(1-\frac{r_s}{r}\right)^{-1}dr^2 + r^2d\Omega^2",
    sympy="ds2 = -(1 - r_s/r)*c**2*dt**2 + (1 - r_s/r)**(-1)*dr**2 + r**2*dOmega**2",
    variables=(
        ("ds", "Spacetime interval", "m"),
        ("r_s", "Schwarzschild radius 2GM/c²", "m"),
        ("r", "Radial coordinate", "m"),
        ("t", "Time coordinate", "s"),
        ("dOmega", "Angular element", "rad"),
    ),
    description="Exact solution for spherically symmetric, non-rotating mass. "
                "Describes black holes when r < r_s.",
    derives_from=("einstein_field_equations",),
    uses=("G", "c"),
    leads_to=("black_hole_physics", "gravitational_redshift"),
    discoverer="Karl Schwarzschild",
    year=1916,
    status=NodeStatus.PROVEN,
    tags=("metric", "black_hole", "exact_solution"),
)

# Schwarzschild Radius
schwarzschild_radius = EquationNode(
    id="schwarzschild_radius",
    name="Schwarzschild Radius",
    domain="general_relativity",
    latex=r"r_s = \frac{2GM}{c^2}",
    sympy="r_s = 2 * G * M / c**2",
    variables=(
        ("r_s", "Schwarzschild radius", "m"),
        ("G", "Gravitational constant", "m³/(kg⋅s²)"),
        ("M", "Mass", "kg"),
        ("c", "Speed of light", "m/s"),
    ),
    description="Event horizon radius for non-rotating black hole. "
                "For Sun: ~3 km. For Earth: ~9 mm.",
    derives_from=("schwarzschild_metric",),
    uses=("G", "c"),
    discoverer="Karl Schwarzschild",
    year=1916,
    status=NodeStatus.PROVEN,
    tags=("black_hole", "event_horizon"),
)

# Gravitational Time Dilation
gravitational_time_dilation = EquationNode(
    id="gravitational_time_dilation",
    name="Gravitational Time Dilation",
    domain="general_relativity",
    latex=r"\frac{d\tau}{dt} = \sqrt{1 - \frac{r_s}{r}} = \sqrt{1 - \frac{2GM}{rc^2}}",
    sympy="dtau/dt = sqrt(1 - r_s/r)",
    variables=(
        ("tau", "Proper time", "s"),
        ("t", "Coordinate time", "s"),
        ("r_s", "Schwarzschild radius", "m"),
        ("r", "Radial distance", "m"),
    ),
    description="Clocks run slower in stronger gravitational fields. "
                "Confirmed by GPS (38 μs/day correction).",
    derives_from=("schwarzschild_metric",),
    uses=("G", "c"),
    discoverer="Albert Einstein",
    year=1915,
    status=NodeStatus.EXPERIMENTAL,
    tags=("time_dilation", "gravity", "gps"),
)

# Geodesic Equation
geodesic = EquationNode(
    id="geodesic_equation",
    name="Geodesic Equation",
    domain="general_relativity",
    latex=r"\frac{d^2x^\mu}{d\tau^2} + \Gamma^\mu_{\nu\rho}\frac{dx^\nu}{d\tau}\frac{dx^\rho}{d\tau} = 0",
    sympy="d2x_mu/dtau2 + Gamma_mu_nu_rho * dx_nu/dtau * dx_rho/dtau = 0",
    variables=(
        ("x_mu", "Spacetime coordinates", "varies"),
        ("tau", "Proper time", "s"),
        ("Gamma", "Christoffel symbols", "m⁻¹"),
    ),
    description="Equation of motion in curved spacetime. Free particles follow "
                "geodesics (straightest possible paths).",
    derives_from=("einstein_field_equations",),
    discoverer="Albert Einstein",
    year=1915,
    status=NodeStatus.PROVEN,
    tags=("motion", "geodesic", "free_fall"),
)

# Export all nodes
NODES = [
    equivalence_principle,
    einstein_field,
    schwarzschild,
    schwarzschild_radius,
    gravitational_time_dilation,
    geodesic,
]
