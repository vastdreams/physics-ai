"""
PATH: physics/knowledge/equations/classical/elasticity.py
PURPOSE: Elasticity and continuum mechanics equations
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Hooke's Law (1D)
hooke_1d = EquationNode(
    id="hooke_law_1d",
    name="Hooke's Law (1D)",
    domain="classical_mechanics",
    latex=r"\sigma = E\epsilon",
    sympy="sigma = E*epsilon",
    variables=(("sigma", "Stress", "Pa"), ("E", "Young's modulus", "Pa"), ("epsilon", "Strain", "dimensionless")),
    description="Linear stress-strain relation. Valid in elastic regime.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("elasticity", "hooke"),
)

# Young's Modulus
youngs_modulus = EquationNode(
    id="youngs_modulus",
    name="Young's Modulus",
    domain="classical_mechanics",
    latex=r"E = \frac{\sigma}{\epsilon} = \frac{F/A}{\Delta L/L}",
    sympy="E = (F/A)/(delta_L/L)",
    variables=(("E", "Young's modulus", "Pa"), ("F", "Force", "N"), ("A", "Cross-sectional area", "m²"), ("L", "Original length", "m")),
    description="Stiffness of material under tension/compression. Steel ~200 GPa.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("modulus", "material"),
)

# Shear Modulus
shear_modulus = EquationNode(
    id="shear_modulus",
    name="Shear Modulus",
    domain="classical_mechanics",
    latex=r"G = \frac{\tau}{\gamma}",
    sympy="G = tau/gamma",
    variables=(("G", "Shear modulus", "Pa"), ("tau", "Shear stress", "Pa"), ("gamma", "Shear strain", "rad")),
    description="Resistance to shear deformation. G = E/(2(1+ν)).",
    status=NodeStatus.FUNDAMENTAL,
    tags=("modulus", "shear"),
)

# Bulk Modulus
bulk_modulus = EquationNode(
    id="bulk_modulus",
    name="Bulk Modulus",
    domain="classical_mechanics",
    latex=r"K = -V\frac{dp}{dV} = \frac{1}{\kappa}",
    sympy="K = -V*dp/dV",
    variables=(("K", "Bulk modulus", "Pa"), ("V", "Volume", "m³"), ("p", "Pressure", "Pa"), ("kappa", "Compressibility", "Pa⁻¹")),
    description="Resistance to uniform compression. K = E/(3(1-2ν)).",
    status=NodeStatus.FUNDAMENTAL,
    tags=("modulus", "compression"),
)

# Poisson's Ratio
poisson_ratio = EquationNode(
    id="poisson_ratio",
    name="Poisson's Ratio",
    domain="classical_mechanics",
    latex=r"\nu = -\frac{\epsilon_{lateral}}{\epsilon_{axial}}",
    sympy="nu = -epsilon_lat/epsilon_ax",
    variables=(("nu", "Poisson's ratio", "dimensionless")),
    description="Ratio of transverse to axial strain. Typically 0.2-0.5. Cork ~0, rubber ~0.5.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("modulus", "poisson"),
)

# Generalized Hooke's Law (3D)
hooke_3d = EquationNode(
    id="hooke_law_3d",
    name="Generalized Hooke's Law (3D)",
    domain="classical_mechanics",
    latex=r"\sigma_{ij} = C_{ijkl}\epsilon_{kl} = \lambda\delta_{ij}\epsilon_{kk} + 2\mu\epsilon_{ij}",
    sympy="sigma_ij = lambda*delta_ij*epsilon_kk + 2*mu*epsilon_ij",
    variables=(("sigma_ij", "Stress tensor", "Pa"), ("epsilon_kl", "Strain tensor", "dimensionless"), ("lambda", "Lamé's first parameter", "Pa"), ("mu", "Shear modulus (Lamé's second)", "Pa")),
    description="Isotropic linear elasticity. λ = K - 2G/3.",
    derives_from=("hooke_law_1d",),
    status=NodeStatus.PROVEN,
    tags=("elasticity", "tensor"),
)

# Strain Tensor
strain_tensor = EquationNode(
    id="strain_tensor",
    name="Strain Tensor",
    domain="classical_mechanics",
    latex=r"\epsilon_{ij} = \frac{1}{2}\left(\frac{\partial u_i}{\partial x_j} + \frac{\partial u_j}{\partial x_i}\right)",
    sympy="epsilon_ij = (1/2)*(du_i/dx_j + du_j/dx_i)",
    variables=(("epsilon_ij", "Strain tensor", "dimensionless"), ("u_i", "Displacement", "m")),
    description="Symmetric part of displacement gradient. Small strain approximation.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("strain", "tensor"),
)

# Cauchy Stress
cauchy_stress = EquationNode(
    id="cauchy_stress",
    name="Cauchy Stress Tensor",
    domain="classical_mechanics",
    latex=r"\sigma_{ij} = \frac{1}{A_j}F_i \quad t_i = \sigma_{ij}n_j",
    sympy="t_i = sigma_ij*n_j",
    variables=(("sigma_ij", "Stress tensor", "Pa"), ("t_i", "Traction vector", "Pa"), ("n_j", "Surface normal", "dimensionless")),
    description="Stress tensor relates traction to surface orientation.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("stress", "tensor"),
)

# Navier Equation
navier_elasticity = EquationNode(
    id="navier_elasticity",
    name="Navier Equation (Elastodynamics)",
    domain="classical_mechanics",
    latex=r"\rho\frac{\partial^2 u_i}{\partial t^2} = (\lambda+\mu)\frac{\partial^2 u_j}{\partial x_i\partial x_j} + \mu\nabla^2 u_i + f_i",
    sympy="rho*d2u/dt2 = (lambda+mu)*grad(div(u)) + mu*laplacian(u) + f",
    variables=(("u", "Displacement", "m"), ("lambda", "Lamé parameter", "Pa"), ("mu", "Shear modulus", "Pa")),
    description="Wave equation for elastic medium. Supports P and S waves.",
    derives_from=("hooke_law_3d",),
    status=NodeStatus.PROVEN,
    tags=("elasticity", "wave"),
)

# P-wave Speed
p_wave_speed = EquationNode(
    id="p_wave_speed",
    name="P-Wave Speed",
    domain="classical_mechanics",
    latex=r"v_P = \sqrt{\frac{\lambda + 2\mu}{\rho}} = \sqrt{\frac{K + 4G/3}{\rho}}",
    sympy="v_P = sqrt((lambda + 2*mu)/rho)",
    variables=(("v_P", "P-wave velocity", "m/s"), ("lambda", "Lamé parameter", "Pa"), ("mu", "Shear modulus", "Pa")),
    description="Longitudinal (compressional) wave speed. Fastest seismic wave.",
    derives_from=("navier_elasticity",),
    status=NodeStatus.PROVEN,
    tags=("wave", "seismic"),
)

# S-wave Speed
s_wave_speed = EquationNode(
    id="s_wave_speed",
    name="S-Wave Speed",
    domain="classical_mechanics",
    latex=r"v_S = \sqrt{\frac{\mu}{\rho}}",
    sympy="v_S = sqrt(mu/rho)",
    variables=(("v_S", "S-wave velocity", "m/s"), ("mu", "Shear modulus", "Pa"), ("rho", "Density", "kg/m³")),
    description="Transverse (shear) wave speed. Zero in fluids (μ=0).",
    derives_from=("navier_elasticity",),
    status=NodeStatus.PROVEN,
    tags=("wave", "seismic"),
)

# Beam Bending
beam_bending = EquationNode(
    id="beam_bending",
    name="Euler-Bernoulli Beam Equation",
    domain="classical_mechanics",
    latex=r"EI\frac{d^4w}{dx^4} = q(x)",
    sympy="E*I*d4w/dx4 = q",
    variables=(("w", "Deflection", "m"), ("E", "Young's modulus", "Pa"), ("I", "Second moment of area", "m⁴"), ("q", "Distributed load", "N/m")),
    description="Deflection of slender beam under transverse load.",
    status=NodeStatus.PROVEN,
    tags=("beam", "bending"),
)

# Bending Stress
bending_stress = EquationNode(
    id="bending_stress",
    name="Bending Stress",
    domain="classical_mechanics",
    latex=r"\sigma = \frac{My}{I}",
    sympy="sigma = M*y/I",
    variables=(("sigma", "Bending stress", "Pa"), ("M", "Bending moment", "N⋅m"), ("y", "Distance from neutral axis", "m"), ("I", "Second moment of area", "m⁴")),
    description="Stress in beam due to bending. Maximum at surface.",
    status=NodeStatus.PROVEN,
    tags=("beam", "stress"),
)

# Torsion
torsion = EquationNode(
    id="torsion",
    name="Torsion of Circular Shaft",
    domain="classical_mechanics",
    latex=r"\tau = \frac{Tr}{J}, \quad \phi = \frac{TL}{GJ}",
    sympy="tau = T*r/J",
    variables=(("tau", "Shear stress", "Pa"), ("T", "Torque", "N⋅m"), ("r", "Radius", "m"), ("J", "Polar moment of area", "m⁴"), ("phi", "Twist angle", "rad")),
    description="Shear stress and twist in circular shaft under torsion.",
    status=NodeStatus.PROVEN,
    tags=("torsion", "shaft"),
)

# Strain Energy Density
strain_energy = EquationNode(
    id="strain_energy_density",
    name="Strain Energy Density",
    domain="classical_mechanics",
    latex=r"U = \frac{1}{2}\sigma_{ij}\epsilon_{ij} = \frac{1}{2}C_{ijkl}\epsilon_{ij}\epsilon_{kl}",
    sympy="U = (1/2)*sigma*epsilon",
    variables=(("U", "Strain energy density", "J/m³")),
    description="Energy stored per unit volume in deformed material.",
    derives_from=("hooke_law_3d",),
    status=NodeStatus.PROVEN,
    tags=("energy", "elastic"),
)

NODES = [
    hooke_1d, youngs_modulus, shear_modulus, bulk_modulus, poisson_ratio,
    hooke_3d, strain_tensor, cauchy_stress, navier_elasticity, p_wave_speed, s_wave_speed,
    beam_bending, bending_stress, torsion, strain_energy
]
