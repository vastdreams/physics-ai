"""
PATH: physics/knowledge/equations/electromagnetism/magnetic.py
PURPOSE: Magnetostatics and magnetic materials equations
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Biot-Savart Law
biot_savart = EquationNode(
    id="biot_savart",
    name="Biot-Savart Law",
    domain="electromagnetism",
    latex=r"d\vec{B} = \frac{\mu_0}{4\pi}\frac{I d\vec{l} \times \hat{r}}{r^2}",
    sympy="dB = mu_0/(4*pi) * I*dl cross r_hat / r**2",
    variables=(("B", "Magnetic field", "T"), ("I", "Current", "A"), ("dl", "Current element", "m"), ("r", "Distance", "m")),
    description="Magnetic field from current element. Integrates to Ampère.",
    uses=("mu_0",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("magnetostatics", "current"),
)

# Magnetic Field of Wire
wire_field = EquationNode(
    id="magnetic_field_wire",
    name="Magnetic Field of Long Wire",
    domain="electromagnetism",
    latex=r"B = \frac{\mu_0 I}{2\pi r}",
    sympy="B = mu_0*I/(2*pi*r)",
    variables=(("B", "Magnetic field", "T"), ("I", "Current", "A"), ("r", "Distance from wire", "m")),
    description="Field circulates around wire. Right-hand rule.",
    derives_from=("biot_savart",),
    uses=("mu_0",),
    status=NodeStatus.PROVEN,
    tags=("wire", "field"),
)

# Solenoid Field
solenoid_field = EquationNode(
    id="solenoid_field",
    name="Solenoid Magnetic Field",
    domain="electromagnetism",
    latex=r"B = \mu_0 n I",
    sympy="B = mu_0*n*I",
    variables=(("B", "Magnetic field", "T"), ("n", "Turns per unit length", "m⁻¹"), ("I", "Current", "A")),
    description="Uniform field inside ideal solenoid.",
    derives_from=("biot_savart",),
    uses=("mu_0",),
    status=NodeStatus.PROVEN,
    tags=("solenoid", "field"),
)

# Toroid Field
toroid_field = EquationNode(
    id="toroid_field",
    name="Toroid Magnetic Field",
    domain="electromagnetism",
    latex=r"B = \frac{\mu_0 NI}{2\pi r}",
    sympy="B = mu_0*N*I/(2*pi*r)",
    variables=(("B", "Magnetic field", "T"), ("N", "Total turns", "dimensionless"), ("r", "Radius to point", "m")),
    description="Field confined inside toroidal coil.",
    derives_from=("biot_savart",),
    uses=("mu_0",),
    status=NodeStatus.PROVEN,
    tags=("toroid", "field"),
)

# Magnetic Dipole Moment
magnetic_dipole = EquationNode(
    id="magnetic_dipole_moment",
    name="Magnetic Dipole Moment",
    domain="electromagnetism",
    latex=r"\vec{m} = NIA\hat{n}",
    sympy="m = N*I*A*n_hat",
    variables=(("m", "Magnetic dipole moment", "A⋅m²"), ("N", "Number of turns", "dimensionless"), ("I", "Current", "A"), ("A", "Loop area", "m²")),
    description="Magnetic moment of current loop. Points normal to loop.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("dipole", "moment"),
)

# Torque on Dipole
dipole_torque = EquationNode(
    id="magnetic_dipole_torque",
    name="Torque on Magnetic Dipole",
    domain="electromagnetism",
    latex=r"\vec{\tau} = \vec{m} \times \vec{B}",
    sympy="tau = m cross B",
    variables=(("tau", "Torque", "N⋅m"), ("m", "Magnetic moment", "A⋅m²"), ("B", "Magnetic field", "T")),
    description="Torque aligns dipole with field.",
    derives_from=("magnetic_dipole_moment",),
    status=NodeStatus.PROVEN,
    tags=("dipole", "torque"),
)

# Dipole Energy
dipole_energy = EquationNode(
    id="magnetic_dipole_energy",
    name="Magnetic Dipole Energy",
    domain="electromagnetism",
    latex=r"U = -\vec{m} \cdot \vec{B}",
    sympy="U = -m dot B",
    variables=(("U", "Potential energy", "J"), ("m", "Magnetic moment", "A⋅m²"), ("B", "Magnetic field", "T")),
    description="Energy minimum when m parallel to B.",
    derives_from=("magnetic_dipole_moment",),
    status=NodeStatus.PROVEN,
    tags=("dipole", "energy"),
)

# Magnetic Field in Matter
magnetic_matter = EquationNode(
    id="magnetic_field_matter",
    name="Magnetic Field in Matter",
    domain="electromagnetism",
    latex=r"\vec{B} = \mu_0(\vec{H} + \vec{M}) = \mu_0\mu_r\vec{H} = \mu\vec{H}",
    sympy="B = mu_0*(H + M) = mu*H",
    variables=(("B", "Magnetic flux density", "T"), ("H", "Magnetic field intensity", "A/m"), ("M", "Magnetization", "A/m"), ("mu_r", "Relative permeability", "dimensionless")),
    description="B-H-M relation. μ_r > 1 paramagnetic, μ_r >> 1 ferromagnetic.",
    uses=("mu_0",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("magnetic", "material"),
)

# Magnetic Susceptibility
susceptibility_magnetic = EquationNode(
    id="magnetic_susceptibility",
    name="Magnetic Susceptibility",
    domain="electromagnetism",
    latex=r"\vec{M} = \chi_m \vec{H}, \quad \mu_r = 1 + \chi_m",
    sympy="M = chi_m*H",
    variables=(("M", "Magnetization", "A/m"), ("chi_m", "Magnetic susceptibility", "dimensionless"), ("H", "Field intensity", "A/m")),
    description="χ < 0 diamagnetic, χ > 0 paramagnetic.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("susceptibility", "material"),
)

# Curie Law
curie_law = EquationNode(
    id="curie_law",
    name="Curie Law",
    domain="electromagnetism",
    latex=r"\chi_m = \frac{C}{T}",
    sympy="chi_m = C/T",
    variables=(("chi_m", "Susceptibility", "dimensionless"), ("C", "Curie constant", "K"), ("T", "Temperature", "K")),
    description="Paramagnetic susceptibility ∝ 1/T.",
    status=NodeStatus.EMPIRICAL,
    tags=("paramagnetism", "temperature"),
)

# Curie-Weiss Law
curie_weiss = EquationNode(
    id="curie_weiss",
    name="Curie-Weiss Law",
    domain="electromagnetism",
    latex=r"\chi_m = \frac{C}{T - T_c}",
    sympy="chi_m = C/(T - T_c)",
    variables=(("T_c", "Curie temperature", "K")),
    description="Ferromagnet susceptibility above T_c. Diverges at T_c.",
    derives_from=("curie_law",),
    status=NodeStatus.EMPIRICAL,
    tags=("ferromagnetism", "transition"),
)

# Force Between Wires
wire_force = EquationNode(
    id="force_between_wires",
    name="Force Between Parallel Wires",
    domain="electromagnetism",
    latex=r"\frac{F}{L} = \frac{\mu_0 I_1 I_2}{2\pi d}",
    sympy="F/L = mu_0*I1*I2/(2*pi*d)",
    variables=(("F/L", "Force per unit length", "N/m"), ("I1", "Current 1", "A"), ("I2", "Current 2", "A"), ("d", "Separation", "m")),
    description="Parallel currents attract, antiparallel repel. Defines the ampere.",
    derives_from=("wire_field", "lorentz_force"),
    uses=("mu_0",),
    status=NodeStatus.PROVEN,
    tags=("force", "wires"),
)

# Mutual Inductance
mutual_inductance = EquationNode(
    id="mutual_inductance",
    name="Mutual Inductance",
    domain="electromagnetism",
    latex=r"\mathcal{E}_2 = -M\frac{dI_1}{dt}, \quad M = \frac{\Phi_{12}}{I_1}",
    sympy="M = Phi_12/I_1",
    variables=(("M", "Mutual inductance", "H"), ("Phi_12", "Flux through 2 from 1", "Wb"), ("I_1", "Current in 1", "A")),
    description="Coupling between two circuits. M₁₂ = M₂₁.",
    status=NodeStatus.PROVEN,
    tags=("inductance", "coupling"),
)

# Self Inductance
self_inductance = EquationNode(
    id="self_inductance",
    name="Self Inductance",
    domain="electromagnetism",
    latex=r"L = \frac{\Phi}{I} = \frac{N\Phi}{I}",
    sympy="L = N*Phi/I",
    variables=(("L", "Self inductance", "H"), ("Phi", "Flux", "Wb"), ("I", "Current", "A"), ("N", "Turns", "dimensionless")),
    description="Flux linkage per unit current. Solenoid: L = μ₀n²V.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("inductance", "self"),
)

# Magnetic Energy Density
magnetic_energy_density = EquationNode(
    id="magnetic_energy_density",
    name="Magnetic Energy Density",
    domain="electromagnetism",
    latex=r"u_B = \frac{B^2}{2\mu_0} = \frac{1}{2}\mu_0 H^2",
    sympy="u_B = B**2/(2*mu_0)",
    variables=(("u_B", "Energy density", "J/m³"), ("B", "Magnetic field", "T")),
    description="Energy stored per unit volume in magnetic field.",
    uses=("mu_0",),
    status=NodeStatus.PROVEN,
    tags=("energy", "magnetic"),
)

NODES = [
    biot_savart, wire_field, solenoid_field, toroid_field, magnetic_dipole,
    dipole_torque, dipole_energy, magnetic_matter, susceptibility_magnetic,
    curie_law, curie_weiss, wire_force, mutual_inductance, self_inductance, magnetic_energy_density
]
