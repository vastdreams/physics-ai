"""
PATH: physics/knowledge/equations/classical/rotational.py
PURPOSE: Rotational dynamics equations
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Moment of Inertia - Point Mass
moment_inertia_point = EquationNode(
    id="moment_inertia_point",
    name="Moment of Inertia (Point Mass)",
    domain="classical_mechanics",
    latex=r"I = mr^2",
    sympy="I = m * r**2",
    variables=(("I", "Moment of inertia", "kg⋅m²"), ("m", "Mass", "kg"), ("r", "Distance from axis", "m")),
    description="Rotational analog of mass. Measures resistance to angular acceleration.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("rotation", "inertia"),
)

# Moment of Inertia - Continuous
moment_inertia_continuous = EquationNode(
    id="moment_inertia_continuous",
    name="Moment of Inertia (Continuous)",
    domain="classical_mechanics",
    latex=r"I = \int r^2 \, dm = \int \rho r^2 \, dV",
    sympy="I = integral(r**2 * rho, V)",
    variables=(("I", "Moment of inertia", "kg⋅m²"), ("rho", "Density", "kg/m³")),
    description="Moment of inertia for continuous mass distributions.",
    status=NodeStatus.PROVEN,
    tags=("rotation", "integration"),
)

# Parallel Axis Theorem
parallel_axis = EquationNode(
    id="parallel_axis_theorem",
    name="Parallel Axis Theorem",
    domain="classical_mechanics",
    latex=r"I = I_{cm} + Md^2",
    sympy="I = I_cm + M * d**2",
    variables=(("I", "Moment of inertia about parallel axis", "kg⋅m²"), ("I_cm", "Moment about CM", "kg⋅m²"), ("d", "Distance between axes", "m")),
    description="Relates moment of inertia about any axis to that about parallel axis through CM.",
    status=NodeStatus.PROVEN,
    tags=("rotation", "theorem"),
)

# Perpendicular Axis Theorem
perpendicular_axis = EquationNode(
    id="perpendicular_axis_theorem",
    name="Perpendicular Axis Theorem",
    domain="classical_mechanics",
    latex=r"I_z = I_x + I_y",
    sympy="I_z = I_x + I_y",
    variables=(("I_z", "Moment about z-axis", "kg⋅m²"), ("I_x", "Moment about x-axis", "kg⋅m²"), ("I_y", "Moment about y-axis", "kg⋅m²")),
    description="For planar objects: moment about perpendicular axis equals sum of two in-plane moments.",
    conditions=("Planar lamina only",),
    status=NodeStatus.PROVEN,
    tags=("rotation", "theorem", "planar"),
)

# Rotational Kinetic Energy
rotational_ke = EquationNode(
    id="rotational_kinetic_energy",
    name="Rotational Kinetic Energy",
    domain="classical_mechanics",
    latex=r"KE_{rot} = \frac{1}{2}I\omega^2",
    sympy="KE_rot = (1/2) * I * omega**2",
    variables=(("KE_rot", "Rotational kinetic energy", "J"), ("I", "Moment of inertia", "kg⋅m²"), ("omega", "Angular velocity", "rad/s")),
    description="Energy of rotational motion. Analog of (1/2)mv².",
    derives_from=("kinetic_energy",),
    status=NodeStatus.PROVEN,
    tags=("rotation", "energy"),
)

# Rolling Without Slipping
rolling_condition = EquationNode(
    id="rolling_without_slipping",
    name="Rolling Without Slipping",
    domain="classical_mechanics",
    latex=r"v_{cm} = \omega R \quad a_{cm} = \alpha R",
    sympy="v_cm = omega * R",
    variables=(("v_cm", "CM velocity", "m/s"), ("omega", "Angular velocity", "rad/s"), ("R", "Radius", "m")),
    description="Constraint for pure rolling motion. Contact point instantaneously at rest.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("rotation", "rolling", "constraint"),
)

# Rolling Kinetic Energy
rolling_ke = EquationNode(
    id="rolling_kinetic_energy",
    name="Rolling Kinetic Energy",
    domain="classical_mechanics",
    latex=r"KE = \frac{1}{2}Mv_{cm}^2 + \frac{1}{2}I_{cm}\omega^2 = \frac{1}{2}(M + I_{cm}/R^2)v_{cm}^2",
    sympy="KE = (1/2)*M*v**2 + (1/2)*I*omega**2",
    variables=(("KE", "Total kinetic energy", "J"), ("M", "Mass", "kg"), ("v_cm", "CM velocity", "m/s")),
    description="Total KE of rolling object = translational + rotational.",
    derives_from=("kinetic_energy", "rotational_kinetic_energy", "rolling_without_slipping"),
    status=NodeStatus.PROVEN,
    tags=("rotation", "rolling", "energy"),
)

# Gyroscopic Precession
precession = EquationNode(
    id="gyroscopic_precession",
    name="Gyroscopic Precession",
    domain="classical_mechanics",
    latex=r"\Omega_p = \frac{Mgr}{I\omega} = \frac{\tau}{L}",
    sympy="Omega_p = M * g * r / (I * omega)",
    variables=(("Omega_p", "Precession angular velocity", "rad/s"), ("M", "Mass", "kg"), ("r", "Distance to pivot", "m"), ("L", "Angular momentum", "kg⋅m²/s")),
    description="Precession rate of spinning top or gyroscope under gravity.",
    derives_from=("angular_momentum", "torque"),
    status=NodeStatus.PROVEN,
    tags=("rotation", "gyroscope", "precession"),
)

# Nutation
nutation = EquationNode(
    id="nutation",
    name="Nutation Frequency",
    domain="classical_mechanics",
    latex=r"\omega_n = \frac{I_3 \omega_3}{I_1}",
    sympy="omega_n = I3 * omega3 / I1",
    variables=(("omega_n", "Nutation frequency", "rad/s"), ("I_3", "Moment about spin axis", "kg⋅m²"), ("I_1", "Moment about perpendicular axis", "kg⋅m²")),
    description="Small oscillations superimposed on precession of symmetric top.",
    status=NodeStatus.PROVEN,
    tags=("rotation", "gyroscope", "nutation"),
)

# Euler's Equations
euler_rotation = EquationNode(
    id="euler_rotation_equations",
    name="Euler's Rotation Equations",
    domain="classical_mechanics",
    latex=r"I_1\dot{\omega}_1 + (I_3-I_2)\omega_2\omega_3 = \tau_1",
    sympy="I1*domega1/dt + (I3-I2)*omega2*omega3 = tau1",
    variables=(("I_1", "Principal moment 1", "kg⋅m²"), ("omega_1", "Angular velocity component", "rad/s"), ("tau_1", "Torque component", "N⋅m")),
    description="Equations of motion for rigid body in body-fixed frame. Three cyclic equations.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("rotation", "rigid_body", "euler"),
)

# Moment of Inertia Tensor
inertia_tensor = EquationNode(
    id="inertia_tensor",
    name="Moment of Inertia Tensor",
    domain="classical_mechanics",
    latex=r"I_{ij} = \int \rho(r^2\delta_{ij} - x_i x_j) dV",
    sympy="I_ij = integral(rho * (r**2 * delta_ij - x_i * x_j), V)",
    variables=(("I_ij", "Inertia tensor components", "kg⋅m²"), ("rho", "Density", "kg/m³")),
    description="Full 3×3 inertia tensor. Diagonal in principal axes.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("rotation", "tensor", "rigid_body"),
)

# Angular Momentum Vector
angular_momentum_vector = EquationNode(
    id="angular_momentum_vector",
    name="Angular Momentum (Tensor Form)",
    domain="classical_mechanics",
    latex=r"\vec{L} = \mathbf{I} \cdot \vec{\omega}",
    sympy="L = I * omega",
    variables=(("L", "Angular momentum vector", "kg⋅m²/s"), ("I", "Inertia tensor", "kg⋅m²"), ("omega", "Angular velocity vector", "rad/s")),
    description="L and ω not necessarily parallel for asymmetric bodies.",
    derives_from=("inertia_tensor", "angular_momentum"),
    status=NodeStatus.PROVEN,
    tags=("rotation", "tensor", "angular_momentum"),
)

# Coriolis Force
coriolis_force = EquationNode(
    id="coriolis_force",
    name="Coriolis Force",
    domain="classical_mechanics",
    latex=r"\vec{F}_{Cor} = -2m\vec{\Omega} \times \vec{v}",
    sympy="F_cor = -2 * m * Omega cross v",
    variables=(("F_cor", "Coriolis force", "N"), ("m", "Mass", "kg"), ("Omega", "Frame angular velocity", "rad/s"), ("v", "Velocity in rotating frame", "m/s")),
    description="Fictitious force in rotating reference frame. Deflects moving objects.",
    status=NodeStatus.PROVEN,
    tags=("rotation", "non-inertial", "fictitious"),
)

# Centrifugal Force
centrifugal_force = EquationNode(
    id="centrifugal_force",
    name="Centrifugal Force",
    domain="classical_mechanics",
    latex=r"\vec{F}_{cf} = -m\vec{\Omega} \times (\vec{\Omega} \times \vec{r}) = m\Omega^2 r \hat{r}",
    sympy="F_cf = m * Omega**2 * r",
    variables=(("F_cf", "Centrifugal force", "N"), ("Omega", "Angular velocity", "rad/s"), ("r", "Distance from axis", "m")),
    description="Fictitious outward force in rotating frame.",
    status=NodeStatus.PROVEN,
    tags=("rotation", "non-inertial", "fictitious"),
)

# Centripetal Acceleration
centripetal = EquationNode(
    id="centripetal_acceleration",
    name="Centripetal Acceleration",
    domain="classical_mechanics",
    latex=r"a_c = \frac{v^2}{r} = \omega^2 r",
    sympy="a_c = v**2 / r",
    variables=(("a_c", "Centripetal acceleration", "m/s²"), ("v", "Speed", "m/s"), ("r", "Radius", "m")),
    description="Acceleration toward center for circular motion.",
    status=NodeStatus.PROVEN,
    tags=("rotation", "circular_motion"),
)

NODES = [
    moment_inertia_point, moment_inertia_continuous, parallel_axis, perpendicular_axis,
    rotational_ke, rolling_condition, rolling_ke, precession, nutation,
    euler_rotation, inertia_tensor, angular_momentum_vector,
    coriolis_force, centrifugal_force, centripetal
]
