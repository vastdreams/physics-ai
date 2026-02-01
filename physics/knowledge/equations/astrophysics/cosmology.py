"""
PATH: physics/knowledge/equations/astrophysics/cosmology.py
PURPOSE: Cosmology equations
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Friedmann Equation
friedmann = EquationNode(
    id="friedmann_equation",
    name="Friedmann Equation",
    domain="cosmology",
    latex=r"H^2 = \left(\frac{\dot{a}}{a}\right)^2 = \frac{8\pi G\rho}{3} - \frac{kc^2}{a^2} + \frac{\Lambda c^2}{3}",
    sympy="H**2 = 8*pi*G*rho/3 - k*c**2/a**2 + Lambda*c**2/3",
    variables=(("H", "Hubble parameter", "s⁻¹"), ("a", "Scale factor", "dimensionless"), ("rho", "Energy density", "kg/m³"), ("k", "Curvature", "m⁻²"), ("Lambda", "Cosmological constant", "m⁻²")),
    description="Evolution of expanding universe. Derived from Einstein field equations.",
    derives_from=("einstein_field_equations",),
    uses=("G", "c"),
    status=NodeStatus.FUNDAMENTAL,
    tags=("cosmology", "expansion"),
)

# Hubble's Law
hubble_law = EquationNode(
    id="hubble_law",
    name="Hubble's Law",
    domain="cosmology",
    latex=r"v = H_0 d",
    sympy="v = H_0 * d",
    variables=(("v", "Recession velocity", "m/s"), ("H_0", "Hubble constant ~70 km/s/Mpc", "s⁻¹"), ("d", "Distance", "m")),
    description="Galaxies recede with velocity proportional to distance.",
    status=NodeStatus.EXPERIMENTAL,
    tags=("expansion", "redshift"),
)

# Cosmological Redshift
cosmological_redshift = EquationNode(
    id="cosmological_redshift",
    name="Cosmological Redshift",
    domain="cosmology",
    latex=r"1 + z = \frac{a(t_0)}{a(t_e)} = \frac{\lambda_{obs}}{\lambda_{emit}}",
    sympy="1 + z = a_0/a_e",
    variables=(("z", "Redshift", "dimensionless"), ("a", "Scale factor", "dimensionless"), ("lambda", "Wavelength", "m")),
    description="Light stretched by expansion. z=0 today, z→∞ at Big Bang.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("redshift", "expansion"),
)

# Critical Density
critical_density = EquationNode(
    id="critical_density",
    name="Critical Density",
    domain="cosmology",
    latex=r"\rho_c = \frac{3H^2}{8\pi G} \approx 9.5 \times 10^{-27} \text{ kg/m}^3",
    sympy="rho_c = 3*H**2/(8*pi*G)",
    variables=(("rho_c", "Critical density", "kg/m³"), ("H", "Hubble parameter", "s⁻¹")),
    description="Density for flat universe. ~5 H atoms per m³.",
    derives_from=("friedmann_equation",),
    uses=("G",),
    status=NodeStatus.PROVEN,
    tags=("cosmology", "density"),
)

# Density Parameters
density_parameters = EquationNode(
    id="density_parameters",
    name="Density Parameters",
    domain="cosmology",
    latex=r"\Omega_m + \Omega_\Lambda + \Omega_k = 1, \quad \Omega_i = \frac{\rho_i}{\rho_c}",
    sympy="Omega_m + Omega_Lambda + Omega_k = 1",
    variables=(("Omega_m", "Matter density parameter ~0.3", "dimensionless"), ("Omega_Lambda", "Dark energy parameter ~0.7", "dimensionless"), ("Omega_k", "Curvature parameter ~0", "dimensionless")),
    description="Normalized densities. Flat universe: Ω_total = 1.",
    derives_from=("friedmann_equation", "critical_density"),
    status=NodeStatus.EXPERIMENTAL,
    tags=("cosmology", "density"),
)

# Age of Universe
age_of_universe = EquationNode(
    id="age_of_universe",
    name="Age of Universe (Flat, Matter+Λ)",
    domain="cosmology",
    latex=r"t_0 = \frac{2}{3H_0\sqrt{\Omega_\Lambda}}\sinh^{-1}\sqrt{\frac{\Omega_\Lambda}{\Omega_m}} \approx 13.8 \text{ Gyr}",
    sympy="t_0 = 2/(3*H_0*sqrt(Omega_Lambda))*arcsinh(sqrt(Omega_Lambda/Omega_m))",
    variables=(("t_0", "Age", "s")),
    description="Age of universe since Big Bang.",
    derives_from=("friedmann_equation",),
    status=NodeStatus.EXPERIMENTAL,
    tags=("cosmology", "age"),
)

# Deceleration Parameter
deceleration_parameter = EquationNode(
    id="deceleration_parameter",
    name="Deceleration Parameter",
    domain="cosmology",
    latex=r"q = -\frac{a\ddot{a}}{\dot{a}^2} = \frac{\Omega_m}{2} - \Omega_\Lambda",
    sympy="q = -a*a_ddot/a_dot**2",
    variables=(("q", "Deceleration parameter", "dimensionless")),
    description="q > 0: decelerating. q < 0: accelerating. Currently q ≈ -0.55.",
    derives_from=("friedmann_equation",),
    status=NodeStatus.EXPERIMENTAL,
    tags=("cosmology", "acceleration"),
)

# Luminosity Distance
luminosity_distance = EquationNode(
    id="luminosity_distance",
    name="Luminosity Distance",
    domain="cosmology",
    latex=r"d_L = (1+z) \int_0^z \frac{c \, dz'}{H(z')}",
    sympy="d_L = (1+z)*integral(c/H(z), z, 0, z)",
    variables=(("d_L", "Luminosity distance", "m"), ("z", "Redshift", "dimensionless")),
    description="Distance such that observed flux = L/(4πd_L²).",
    status=NodeStatus.PROVEN,
    tags=("cosmology", "distance"),
)

# Angular Diameter Distance
angular_diameter_distance = EquationNode(
    id="angular_diameter_distance",
    name="Angular Diameter Distance",
    domain="cosmology",
    latex=r"d_A = \frac{d_L}{(1+z)^2}",
    sympy="d_A = d_L/(1+z)**2",
    variables=(("d_A", "Angular diameter distance", "m"), ("d_L", "Luminosity distance", "m")),
    description="Distance such that angular size = physical size / d_A.",
    derives_from=("luminosity_distance",),
    status=NodeStatus.PROVEN,
    tags=("cosmology", "distance"),
)

# CMB Temperature
cmb_temperature = EquationNode(
    id="cmb_temperature",
    name="CMB Temperature Evolution",
    domain="cosmology",
    latex=r"T(z) = T_0(1+z) = 2.725(1+z) \text{ K}",
    sympy="T = T_0*(1 + z)",
    variables=(("T", "CMB temperature", "K"), ("T_0", "Today's temperature ≈2.725 K", "K"), ("z", "Redshift", "dimensionless")),
    description="CMB was hotter in past. At recombination (z≈1100): T≈3000K.",
    status=NodeStatus.EXPERIMENTAL,
    tags=("cmb", "temperature"),
)

# Recombination
recombination_temp = EquationNode(
    id="recombination",
    name="Recombination Temperature",
    domain="cosmology",
    latex=r"T_{rec} \approx 3000 \text{ K}, \quad z_{rec} \approx 1100",
    sympy="T_rec = 3000",
    variables=(("T_rec", "Recombination temperature", "K"), ("z_rec", "Recombination redshift", "dimensionless")),
    description="When universe became transparent. CMB last scattering surface.",
    status=NodeStatus.EXPERIMENTAL,
    tags=("cmb", "recombination"),
)

# Saha Equation
saha_equation = EquationNode(
    id="saha_equation",
    name="Saha Equation",
    domain="cosmology",
    latex=r"\frac{n_e n_p}{n_H} = \left(\frac{2\pi m_e k_B T}{h^2}\right)^{3/2} e^{-E_I/k_B T}",
    sympy="n_e*n_p/n_H = (2*pi*m_e*k_B*T/h**2)**(3/2)*exp(-E_I/(k_B*T))",
    variables=(("n_e", "Electron density", "m⁻³"), ("n_p", "Proton density", "m⁻³"), ("n_H", "Neutral H density", "m⁻³"), ("E_I", "Ionization energy 13.6 eV", "J")),
    description="Ionization equilibrium. Determines recombination epoch.",
    uses=("k_B", "h", "m_e"),
    status=NodeStatus.PROVEN,
    tags=("ionization", "recombination"),
)

# Horizon Size
particle_horizon = EquationNode(
    id="particle_horizon",
    name="Particle Horizon",
    domain="cosmology",
    latex=r"d_H = a(t)\int_0^t \frac{c \, dt'}{a(t')} = \int_0^a \frac{c \, da'}{a'^2 H(a')}",
    sympy="d_H = a*integral(c/a, t, 0, t)",
    variables=(("d_H", "Particle horizon", "m"), ("a", "Scale factor", "dimensionless")),
    description="Maximum distance light could have traveled since Big Bang.",
    status=NodeStatus.PROVEN,
    tags=("cosmology", "horizon"),
)

# Inflation e-folding
inflation = EquationNode(
    id="inflation_efolding",
    name="Inflation e-folding",
    domain="cosmology",
    latex=r"N = \ln\frac{a_{end}}{a_{start}} \approx 60",
    sympy="N = ln(a_end/a_start)",
    variables=(("N", "Number of e-folds", "dimensionless")),
    description="Universe expanded by e^60 ≈ 10²⁶ during inflation.",
    status=NodeStatus.THEORETICAL,
    tags=("inflation", "expansion"),
)

NODES = [
    friedmann, hubble_law, cosmological_redshift, critical_density, density_parameters,
    age_of_universe, deceleration_parameter, luminosity_distance, angular_diameter_distance,
    cmb_temperature, recombination_temp, saha_equation, particle_horizon, inflation
]
