"""
PATH: physics/knowledge/equations/astrophysics/stellar.py
PURPOSE: Stellar physics equations
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Luminosity-Mass Relation
mass_luminosity = EquationNode(
    id="mass_luminosity_relation",
    name="Mass-Luminosity Relation",
    domain="astrophysics",
    latex=r"L \propto M^{3.5} \quad \text{(main sequence)}",
    sympy="L ~ M**3.5",
    variables=(("L", "Luminosity", "W"), ("M", "Mass", "kg")),
    description="More massive stars are much more luminous. L/L_☉ ≈ (M/M_☉)^3.5.",
    status=NodeStatus.EMPIRICAL,
    tags=("stellar", "main_sequence"),
)

# Stefan-Boltzmann (Stellar)
stellar_luminosity = EquationNode(
    id="stellar_luminosity",
    name="Stellar Luminosity",
    domain="astrophysics",
    latex=r"L = 4\pi R^2 \sigma T_{eff}^4",
    sympy="L = 4*pi*R**2*sigma*T**4",
    variables=(("L", "Luminosity", "W"), ("R", "Stellar radius", "m"), ("sigma", "Stefan-Boltzmann", "W/(m²K⁴)"), ("T_eff", "Effective temperature", "K")),
    description="Total power radiated by star.",
    derives_from=("stefan_boltzmann_law",),
    uses=("sigma",),
    status=NodeStatus.PROVEN,
    tags=("stellar", "luminosity"),
)

# Hydrostatic Equilibrium
hydrostatic_equilibrium = EquationNode(
    id="stellar_hydrostatic",
    name="Stellar Hydrostatic Equilibrium",
    domain="astrophysics",
    latex=r"\frac{dP}{dr} = -\frac{GM(r)\rho(r)}{r^2}",
    sympy="dP/dr = -G*M_r*rho/r**2",
    variables=(("P", "Pressure", "Pa"), ("r", "Radius", "m"), ("M_r", "Mass inside r", "kg"), ("rho", "Density", "kg/m³")),
    description="Balance of gravity and pressure in stellar interior.",
    uses=("G",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("stellar", "equilibrium"),
)

# Mass Continuity (Stellar)
mass_continuity_stellar = EquationNode(
    id="stellar_mass_continuity",
    name="Stellar Mass Continuity",
    domain="astrophysics",
    latex=r"\frac{dM}{dr} = 4\pi r^2 \rho",
    sympy="dM/dr = 4*pi*r**2*rho",
    variables=(("M", "Enclosed mass", "kg"), ("r", "Radius", "m"), ("rho", "Density", "kg/m³")),
    description="Mass inside radius r.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("stellar", "structure"),
)

# Energy Generation
energy_generation = EquationNode(
    id="stellar_energy_generation",
    name="Stellar Energy Generation",
    domain="astrophysics",
    latex=r"\frac{dL}{dr} = 4\pi r^2 \rho \epsilon",
    sympy="dL/dr = 4*pi*r**2*rho*epsilon",
    variables=(("L", "Luminosity", "W"), ("r", "Radius", "m"), ("rho", "Density", "kg/m³"), ("epsilon", "Energy rate per mass", "W/kg")),
    description="Luminosity increases due to nuclear energy generation.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("stellar", "nuclear"),
)

# Radiative Transfer
radiative_transfer = EquationNode(
    id="radiative_transfer",
    name="Radiative Temperature Gradient",
    domain="astrophysics",
    latex=r"\frac{dT}{dr} = -\frac{3\kappa\rho L}{16\pi ac T^3 r^2}",
    sympy="dT/dr = -3*kappa*rho*L/(16*pi*a*c*T**3*r**2)",
    variables=(("T", "Temperature", "K"), ("kappa", "Opacity", "m²/kg"), ("L", "Luminosity", "W"), ("a", "Radiation constant", "J/(m³K⁴)")),
    description="Temperature gradient in radiative zone.",
    status=NodeStatus.PROVEN,
    tags=("stellar", "radiative"),
)

# Eddington Luminosity
eddington_luminosity = EquationNode(
    id="eddington_luminosity",
    name="Eddington Luminosity",
    domain="astrophysics",
    latex=r"L_{Edd} = \frac{4\pi GMm_pc}{\sigma_T} \approx 3.3 \times 10^4 \left(\frac{M}{M_\odot}\right) L_\odot",
    sympy="L_Edd = 4*pi*G*M*m_p*c/sigma_T",
    variables=(("L_Edd", "Eddington luminosity", "W"), ("M", "Mass", "kg"), ("sigma_T", "Thomson cross section", "m²")),
    description="Maximum luminosity before radiation pressure expels matter.",
    uses=("G", "m_p", "c"),
    status=NodeStatus.PROVEN,
    tags=("stellar", "limit"),
)

# Schwarzschild Criterion
schwarzschild_criterion = EquationNode(
    id="schwarzschild_criterion",
    name="Schwarzschild Convection Criterion",
    domain="astrophysics",
    latex=r"\left|\frac{dT}{dr}\right|_{rad} > \left|\frac{dT}{dr}\right|_{ad}",
    sympy="|dT/dr|_rad > |dT/dr|_ad",
    variables=(),
    description="Convection occurs when radiative gradient exceeds adiabatic gradient.",
    status=NodeStatus.PROVEN,
    tags=("stellar", "convection"),
)

# Chandrasekhar Mass
chandrasekhar_mass = EquationNode(
    id="chandrasekhar_mass",
    name="Chandrasekhar Mass",
    domain="astrophysics",
    latex=r"M_{Ch} = \frac{\omega_3^0 \sqrt{3\pi}}{2}\left(\frac{\hbar c}{G}\right)^{3/2}\frac{1}{(\mu_e m_H)^2} \approx 1.44 M_\odot",
    sympy="M_Ch = 1.44*M_sun",
    variables=(("M_Ch", "Chandrasekhar mass", "kg"), ("mu_e", "Mean mol. weight per electron", "dimensionless")),
    description="Maximum mass of white dwarf supported by electron degeneracy.",
    uses=("hbar", "c", "G"),
    status=NodeStatus.PROVEN,
    tags=("white_dwarf", "limit"),
)

# Oppenheimer-Volkoff Limit
ov_limit = EquationNode(
    id="oppenheimer_volkoff_limit",
    name="Tolman-Oppenheimer-Volkoff Limit",
    domain="astrophysics",
    latex=r"M_{TOV} \approx 2-3 M_\odot",
    sympy="M_TOV ~ 2.5*M_sun",
    variables=(("M_TOV", "TOV limit", "kg")),
    description="Maximum mass of neutron star. Above this, collapse to black hole.",
    status=NodeStatus.THEORETICAL,
    tags=("neutron_star", "limit"),
)

# Jeans Mass
jeans_mass = EquationNode(
    id="jeans_mass",
    name="Jeans Mass",
    domain="astrophysics",
    latex=r"M_J = \left(\frac{5k_BT}{Gm}\right)^{3/2}\left(\frac{3}{4\pi\rho}\right)^{1/2}",
    sympy="M_J = (5*k_B*T/(G*m))**(3/2) * (3/(4*pi*rho))**(1/2)",
    variables=(("M_J", "Jeans mass", "kg"), ("T", "Temperature", "K"), ("rho", "Density", "kg/m³"), ("m", "Mean particle mass", "kg")),
    description="Minimum mass for gravitational collapse. Cloud collapses if M > M_J.",
    uses=("k_B", "G"),
    status=NodeStatus.PROVEN,
    tags=("collapse", "cloud"),
)

# Jeans Length
jeans_length = EquationNode(
    id="jeans_length",
    name="Jeans Length",
    domain="astrophysics",
    latex=r"\lambda_J = \sqrt{\frac{\pi k_B T}{G\rho m}}",
    sympy="lambda_J = sqrt(pi*k_B*T/(G*rho*m))",
    variables=(("lambda_J", "Jeans length", "m"), ("T", "Temperature", "K"), ("rho", "Density", "kg/m³")),
    description="Minimum size for gravitational instability.",
    uses=("k_B", "G"),
    status=NodeStatus.PROVEN,
    tags=("collapse", "instability"),
)

# Virial Theorem (Gravitational)
virial_gravitational = EquationNode(
    id="virial_theorem_gravitational",
    name="Virial Theorem (Gravitational)",
    domain="astrophysics",
    latex=r"2K + U = 0 \quad \text{or} \quad 2\langle T \rangle = -\langle V \rangle",
    sympy="2*K + U = 0",
    variables=(("K", "Kinetic energy", "J"), ("U", "Gravitational potential energy", "J")),
    description="For gravitationally bound system in equilibrium.",
    status=NodeStatus.PROVEN,
    tags=("virial", "equilibrium"),
)

# Pulsar Period Derivative
pulsar_spindown = EquationNode(
    id="pulsar_spindown",
    name="Pulsar Spindown",
    domain="astrophysics",
    latex=r"\dot{E} = -I\Omega\dot{\Omega} = 4\pi^2 I \frac{\dot{P}}{P^3}",
    sympy="E_dot = 4*pi**2*I*P_dot/P**3",
    variables=(("E_dot", "Spindown luminosity", "W"), ("I", "Moment of inertia", "kg⋅m²"), ("P", "Period", "s"), ("P_dot", "Period derivative", "s/s")),
    description="Energy loss rate from rotating pulsar.",
    status=NodeStatus.PROVEN,
    tags=("pulsar", "rotation"),
)

# Characteristic Age
pulsar_age = EquationNode(
    id="pulsar_characteristic_age",
    name="Pulsar Characteristic Age",
    domain="astrophysics",
    latex=r"\tau_c = \frac{P}{2\dot{P}}",
    sympy="tau_c = P/(2*P_dot)",
    variables=(("tau_c", "Characteristic age", "s"), ("P", "Period", "s"), ("P_dot", "Period derivative", "s/s")),
    description="Estimate of pulsar age assuming magnetic dipole braking.",
    derives_from=("pulsar_spindown",),
    status=NodeStatus.APPROXIMATE,
    tags=("pulsar", "age"),
)

NODES = [
    mass_luminosity, stellar_luminosity, hydrostatic_equilibrium, mass_continuity_stellar,
    energy_generation, radiative_transfer, eddington_luminosity, schwarzschild_criterion,
    chandrasekhar_mass, ov_limit, jeans_mass, jeans_length, virial_gravitational,
    pulsar_spindown, pulsar_age
]
