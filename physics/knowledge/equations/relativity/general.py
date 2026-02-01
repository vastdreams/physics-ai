"""
PATH: physics/knowledge/equations/relativity/general.py
PURPOSE: General relativity equations
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Einstein Field Equations
einstein_field = EquationNode(
    id="einstein_field_equations",
    name="Einstein Field Equations",
    domain="general_relativity",
    latex=r"G_{\mu\nu} + \Lambda g_{\mu\nu} = \frac{8\pi G}{c^4}T_{\mu\nu}",
    sympy="G_munu + Lambda*g_munu = 8*pi*G/c**4 * T_munu",
    variables=(("G_munu", "Einstein tensor", "m⁻²"), ("g_munu", "Metric tensor", "dimensionless"), ("T_munu", "Stress-energy tensor", "J/m³"), ("Lambda", "Cosmological constant", "m⁻²")),
    description="Geometry = matter content. G_μν = R_μν - (1/2)Rg_μν.",
    uses=("G", "c"),
    status=NodeStatus.FUNDAMENTAL,
    tags=("gravity", "tensor"),
)

# Ricci Tensor
ricci_tensor = EquationNode(
    id="ricci_tensor",
    name="Ricci Tensor",
    domain="general_relativity",
    latex=r"R_{\mu\nu} = R^\lambda_{\mu\lambda\nu} = \partial_\lambda\Gamma^\lambda_{\mu\nu} - \partial_\nu\Gamma^\lambda_{\mu\lambda} + ...",
    sympy="R_munu = R^lambda_mulambdanu",
    variables=(("R_munu", "Ricci tensor", "m⁻²"), ("Gamma", "Christoffel symbols", "m⁻¹")),
    description="Contraction of Riemann tensor. Measures volume change.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("curvature", "tensor"),
)

# Riemann Tensor
riemann_tensor = EquationNode(
    id="riemann_tensor",
    name="Riemann Curvature Tensor",
    domain="general_relativity",
    latex=r"R^\rho_{\sigma\mu\nu} = \partial_\mu\Gamma^\rho_{\nu\sigma} - \partial_\nu\Gamma^\rho_{\mu\sigma} + \Gamma^\rho_{\mu\lambda}\Gamma^\lambda_{\nu\sigma} - \Gamma^\rho_{\nu\lambda}\Gamma^\lambda_{\mu\sigma}",
    sympy="R^rho_sigmamunu = ...",
    variables=(("R^rho_sigmamunu", "Riemann tensor", "m⁻²")),
    description="Full curvature tensor. 20 independent components in 4D.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("curvature", "tensor"),
)

# Christoffel Symbols
christoffel = EquationNode(
    id="christoffel_symbols",
    name="Christoffel Symbols",
    domain="general_relativity",
    latex=r"\Gamma^\lambda_{\mu\nu} = \frac{1}{2}g^{\lambda\sigma}(\partial_\mu g_{\nu\sigma} + \partial_\nu g_{\mu\sigma} - \partial_\sigma g_{\mu\nu})",
    sympy="Gamma^lambda_munu = (1/2)*g^lambdasigma*(dg + dg - dg)",
    variables=(("Gamma", "Christoffel symbols", "m⁻¹"), ("g_munu", "Metric", "dimensionless")),
    description="Connection coefficients. Not a tensor but determines geodesics.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("connection", "metric"),
)

# Geodesic Equation
geodesic = EquationNode(
    id="geodesic_equation",
    name="Geodesic Equation",
    domain="general_relativity",
    latex=r"\frac{d^2x^\mu}{d\tau^2} + \Gamma^\mu_{\alpha\beta}\frac{dx^\alpha}{d\tau}\frac{dx^\beta}{d\tau} = 0",
    sympy="d2x/dtau2 + Gamma*dx/dtau*dx/dtau = 0",
    variables=(("x^mu", "Position", "m"), ("tau", "Proper time", "s"), ("Gamma", "Christoffel symbols", "m⁻¹")),
    description="Equation of motion for free particle in curved spacetime.",
    derives_from=("christoffel_symbols",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("geodesic", "motion"),
)

# Schwarzschild Metric
schwarzschild = EquationNode(
    id="schwarzschild_metric",
    name="Schwarzschild Metric",
    domain="general_relativity",
    latex=r"ds^2 = -\left(1-\frac{r_s}{r}\right)c^2dt^2 + \left(1-\frac{r_s}{r}\right)^{-1}dr^2 + r^2d\Omega^2",
    sympy="ds**2 = -(1-r_s/r)*c**2*dt**2 + (1-r_s/r)**(-1)*dr**2 + r**2*dOmega**2",
    variables=(("r_s", "Schwarzschild radius = 2GM/c²", "m"), ("dOmega", "Solid angle element", "sr")),
    description="Spacetime around non-rotating, uncharged mass. Exact vacuum solution.",
    derives_from=("einstein_field_equations",),
    uses=("G", "c"),
    status=NodeStatus.PROVEN,
    tags=("black_hole", "metric"),
)

# Schwarzschild Radius
schwarzschild_radius = EquationNode(
    id="schwarzschild_radius",
    name="Schwarzschild Radius",
    domain="general_relativity",
    latex=r"r_s = \frac{2GM}{c^2} \approx 3 \text{ km}\left(\frac{M}{M_\odot}\right)",
    sympy="r_s = 2*G*M/c**2",
    variables=(("r_s", "Schwarzschild radius", "m"), ("M", "Mass", "kg")),
    description="Event horizon radius for non-rotating black hole.",
    uses=("G", "c"),
    status=NodeStatus.PROVEN,
    tags=("black_hole", "horizon"),
)

# Kerr Metric
kerr_metric = EquationNode(
    id="kerr_metric",
    name="Kerr Metric (Boyer-Lindquist)",
    domain="general_relativity",
    latex=r"ds^2 = -\left(1-\frac{r_sr}{\Sigma}\right)dt^2 - \frac{2r_sra\sin^2\theta}{\Sigma}dtd\phi + \frac{\Sigma}{\Delta}dr^2 + ...",
    sympy="ds**2 = -(1-r_s*r/Sigma)*dt**2 + ...",
    variables=(("a", "Spin parameter J/Mc", "m"), ("Sigma", "r² + a²cos²θ", "m²"), ("Delta", "r² - r_s r + a²", "m²")),
    description="Rotating black hole. Has ergosphere outside event horizon.",
    derives_from=("einstein_field_equations",),
    status=NodeStatus.PROVEN,
    tags=("black_hole", "rotation"),
)

# Gravitational Redshift
gravitational_redshift = EquationNode(
    id="gravitational_redshift",
    name="Gravitational Redshift",
    domain="general_relativity",
    latex=r"z = \frac{\Delta\lambda}{\lambda} = \sqrt{\frac{1-r_s/r_e}{1-r_s/r_o}} - 1 \approx \frac{GM}{c^2r}",
    sympy="z = sqrt((1-r_s/r_e)/(1-r_s/r_o)) - 1",
    variables=(("z", "Redshift", "dimensionless"), ("r_e", "Emission radius", "m"), ("r_o", "Observer radius", "m")),
    description="Light loses energy climbing out of gravitational well.",
    derives_from=("schwarzschild_metric",),
    uses=("G", "c"),
    status=NodeStatus.EXPERIMENTAL,
    tags=("redshift", "time_dilation"),
)

# Gravitational Time Dilation
gravitational_time_dilation = EquationNode(
    id="gravitational_time_dilation",
    name="Gravitational Time Dilation",
    domain="general_relativity",
    latex=r"\frac{d\tau}{dt} = \sqrt{1 - \frac{r_s}{r}} \approx 1 - \frac{GM}{c^2r}",
    sympy="dtau/dt = sqrt(1 - r_s/r)",
    variables=(("tau", "Proper time", "s"), ("t", "Coordinate time", "s")),
    description="Clocks run slower in gravitational field. GPS must correct for this.",
    derives_from=("schwarzschild_metric",),
    uses=("G", "c"),
    status=NodeStatus.EXPERIMENTAL,
    tags=("time_dilation", "gps"),
)

# Perihelion Precession
perihelion_precession = EquationNode(
    id="perihelion_precession",
    name="Perihelion Precession",
    domain="general_relativity",
    latex=r"\Delta\phi = \frac{6\pi GM}{c^2a(1-e^2)} \text{ per orbit}",
    sympy="delta_phi = 6*pi*G*M/(c**2*a*(1-e**2))",
    variables=(("delta_phi", "Precession per orbit", "rad"), ("a", "Semi-major axis", "m"), ("e", "Eccentricity", "dimensionless")),
    description="Mercury: 43 arcsec/century. First confirmed prediction of GR.",
    derives_from=("schwarzschild_metric",),
    uses=("G", "c"),
    status=NodeStatus.EXPERIMENTAL,
    tags=("precession", "orbit"),
)

# Light Bending
light_bending = EquationNode(
    id="light_bending",
    name="Light Bending",
    domain="general_relativity",
    latex=r"\delta = \frac{4GM}{c^2b} = \frac{2r_s}{b}",
    sympy="delta = 4*G*M/(c**2*b)",
    variables=(("delta", "Deflection angle", "rad"), ("b", "Impact parameter", "m")),
    description="Light bent by gravity. Sun: 1.75 arcsec. Twice Newtonian prediction.",
    derives_from=("geodesic_equation", "schwarzschild_metric"),
    uses=("G", "c"),
    status=NodeStatus.EXPERIMENTAL,
    tags=("lensing", "deflection"),
)

# Shapiro Delay
shapiro_delay = EquationNode(
    id="shapiro_delay",
    name="Shapiro Time Delay",
    domain="general_relativity",
    latex=r"\Delta t = \frac{4GM}{c^3}\ln\frac{4r_1 r_2}{b^2}",
    sympy="delta_t = 4*G*M/c**3 * ln(4*r1*r2/b**2)",
    variables=(("delta_t", "Time delay", "s"), ("r1", "Distance to emitter", "m"), ("r2", "Distance to receiver", "m"), ("b", "Impact parameter", "m")),
    description="Fourth classical test of GR. Light takes longer near massive body.",
    uses=("G", "c"),
    status=NodeStatus.EXPERIMENTAL,
    tags=("time_delay", "radar"),
)

# Gravitational Wave Power
gw_power = EquationNode(
    id="gravitational_wave_power",
    name="Gravitational Wave Power",
    domain="general_relativity",
    latex=r"P = \frac{32G^4}{5c^5}\frac{(m_1 m_2)^2(m_1+m_2)}{r^5}",
    sympy="P = 32*G**4/(5*c**5)*(m1*m2)**2*(m1+m2)/r**5",
    variables=(("P", "Radiated power", "W"), ("m1", "Mass 1", "kg"), ("m2", "Mass 2", "kg"), ("r", "Separation", "m")),
    description="Quadrupole formula for GW emission. Binary pulsars lose energy this way.",
    uses=("G", "c"),
    status=NodeStatus.EXPERIMENTAL,
    tags=("gravitational_waves", "power"),
)

# Gravitational Wave Strain
gw_strain = EquationNode(
    id="gravitational_wave_strain",
    name="Gravitational Wave Strain",
    domain="general_relativity",
    latex=r"h \sim \frac{4G\mathcal{M}^{5/3}}{c^4 d}(\pi f)^{2/3}",
    sympy="h ~ 4*G*M_chirp**(5/3)/(c**4*d)*(pi*f)**(2/3)",
    variables=(("h", "Strain amplitude", "dimensionless"), ("M_chirp", "Chirp mass", "kg"), ("d", "Distance", "m"), ("f", "Frequency", "Hz")),
    description="Dimensionless strain h ~ ΔL/L. LIGO sensitivity ~10⁻²³.",
    uses=("G", "c"),
    status=NodeStatus.EXPERIMENTAL,
    tags=("gravitational_waves", "detection"),
)

NODES = [
    einstein_field, ricci_tensor, riemann_tensor, christoffel, geodesic,
    schwarzschild, schwarzschild_radius, kerr_metric, gravitational_redshift,
    gravitational_time_dilation, perihelion_precession, light_bending, shapiro_delay,
    gw_power, gw_strain
]
