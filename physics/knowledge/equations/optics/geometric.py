"""
PATH: physics/knowledge/equations/optics/geometric.py
PURPOSE: Geometric optics - reflection, refraction, lenses, mirrors
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Snell's Law
snells_law = EquationNode(
    id="snells_law",
    name="Snell's Law",
    domain="optics",
    latex=r"n_1 \sin\theta_1 = n_2 \sin\theta_2",
    sympy="n1 * sin(theta1) = n2 * sin(theta2)",
    variables=(("n1", "Refractive index 1", "dimensionless"), ("theta1", "Incident angle", "rad"), ("n2", "Refractive index 2", "dimensionless"), ("theta2", "Refracted angle", "rad")),
    description="Law of refraction. Light bends toward normal entering denser medium.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("refraction", "interface"),
)

# Critical Angle
critical_angle = EquationNode(
    id="critical_angle",
    name="Critical Angle for Total Internal Reflection",
    domain="optics",
    latex=r"\theta_c = \arcsin\frac{n_2}{n_1}",
    sympy="theta_c = asin(n2/n1)",
    variables=(("theta_c", "Critical angle", "rad"), ("n1", "Denser medium index", "dimensionless"), ("n2", "Less dense medium index", "dimensionless")),
    description="Beyond this angle, total internal reflection occurs.",
    derives_from=("snells_law",),
    conditions=("n1 > n2",),
    status=NodeStatus.PROVEN,
    tags=("refraction", "tir"),
)

# Law of Reflection
reflection_law = EquationNode(
    id="law_of_reflection",
    name="Law of Reflection",
    domain="optics",
    latex=r"\theta_i = \theta_r",
    sympy="theta_i = theta_r",
    variables=(("theta_i", "Incident angle", "rad"), ("theta_r", "Reflected angle", "rad")),
    description="Angle of incidence equals angle of reflection.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("reflection"),
)

# Thin Lens Equation
thin_lens = EquationNode(
    id="thin_lens_equation",
    name="Thin Lens Equation",
    domain="optics",
    latex=r"\frac{1}{f} = \frac{1}{d_o} + \frac{1}{d_i}",
    sympy="1/f = 1/d_o + 1/d_i",
    variables=(("f", "Focal length", "m"), ("d_o", "Object distance", "m"), ("d_i", "Image distance", "m")),
    description="Relates object and image distances to focal length.",
    status=NodeStatus.PROVEN,
    tags=("lens", "imaging"),
)

# Lensmaker's Equation
lensmaker = EquationNode(
    id="lensmaker_equation",
    name="Lensmaker's Equation",
    domain="optics",
    latex=r"\frac{1}{f} = (n-1)\left(\frac{1}{R_1} - \frac{1}{R_2}\right)",
    sympy="1/f = (n-1)*(1/R1 - 1/R2)",
    variables=(("f", "Focal length", "m"), ("n", "Refractive index", "dimensionless"), ("R1", "Front radius", "m"), ("R2", "Back radius", "m")),
    description="Focal length from lens shape and material.",
    derives_from=("snells_law",),
    status=NodeStatus.PROVEN,
    tags=("lens", "design"),
)

# Magnification
magnification = EquationNode(
    id="magnification",
    name="Magnification",
    domain="optics",
    latex=r"m = \frac{h_i}{h_o} = -\frac{d_i}{d_o}",
    sympy="m = -d_i/d_o",
    variables=(("m", "Magnification", "dimensionless"), ("h_i", "Image height", "m"), ("h_o", "Object height", "m")),
    description="Ratio of image to object size. Negative = inverted.",
    derives_from=("thin_lens_equation",),
    status=NodeStatus.PROVEN,
    tags=("lens", "imaging"),
)

# Mirror Equation
mirror_equation = EquationNode(
    id="mirror_equation",
    name="Mirror Equation",
    domain="optics",
    latex=r"\frac{1}{f} = \frac{1}{d_o} + \frac{1}{d_i} = \frac{2}{R}",
    sympy="1/f = 1/d_o + 1/d_i = 2/R",
    variables=(("f", "Focal length", "m"), ("R", "Radius of curvature", "m")),
    description="Same form as lens equation. f = R/2 for spherical mirror.",
    status=NodeStatus.PROVEN,
    tags=("mirror", "imaging"),
)

# Optical Power
optical_power = EquationNode(
    id="optical_power",
    name="Optical Power (Diopters)",
    domain="optics",
    latex=r"P = \frac{1}{f} \quad [D = m^{-1}]",
    sympy="P = 1/f",
    variables=(("P", "Optical power", "D"), ("f", "Focal length", "m")),
    description="Reciprocal of focal length in meters. Powers add for thin lenses in contact.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("lens", "power"),
)

# Numerical Aperture
numerical_aperture = EquationNode(
    id="numerical_aperture",
    name="Numerical Aperture",
    domain="optics",
    latex=r"NA = n \sin\theta_{max}",
    sympy="NA = n * sin(theta_max)",
    variables=(("NA", "Numerical aperture", "dimensionless"), ("n", "Refractive index", "dimensionless"), ("theta_max", "Half-angle of cone", "rad")),
    description="Light-gathering ability of optical system. Determines resolution.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("aperture", "resolution"),
)

# f-number
f_number = EquationNode(
    id="f_number",
    name="f-number",
    domain="optics",
    latex=r"N = \frac{f}{D}",
    sympy="N = f/D",
    variables=(("N", "f-number", "dimensionless"), ("f", "Focal length", "m"), ("D", "Aperture diameter", "m")),
    description="Ratio of focal length to aperture. Lower N = more light.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("aperture", "exposure"),
)

# Brewster's Angle
brewster_angle = EquationNode(
    id="brewster_angle",
    name="Brewster's Angle",
    domain="optics",
    latex=r"\tan\theta_B = \frac{n_2}{n_1}",
    sympy="tan(theta_B) = n2/n1",
    variables=(("theta_B", "Brewster angle", "rad"), ("n1", "Index 1", "dimensionless"), ("n2", "Index 2", "dimensionless")),
    description="Angle at which reflected light is completely polarized.",
    derives_from=("snells_law",),
    status=NodeStatus.PROVEN,
    tags=("polarization", "reflection"),
)

# Fresnel Equations (simplified)
fresnel_reflectance = EquationNode(
    id="fresnel_reflectance",
    name="Fresnel Reflectance (Normal Incidence)",
    domain="optics",
    latex=r"R = \left(\frac{n_1 - n_2}{n_1 + n_2}\right)^2",
    sympy="R = ((n1 - n2)/(n1 + n2))**2",
    variables=(("R", "Reflectance", "dimensionless"), ("n1", "Index 1", "dimensionless"), ("n2", "Index 2", "dimensionless")),
    description="Fraction of light reflected at normal incidence.",
    status=NodeStatus.PROVEN,
    tags=("reflection", "fresnel"),
)

# Prism Dispersion
prism_deviation = EquationNode(
    id="prism_deviation",
    name="Prism Minimum Deviation",
    domain="optics",
    latex=r"n = \frac{\sin\frac{A+\delta_m}{2}}{\sin\frac{A}{2}}",
    sympy="n = sin((A + delta_m)/2) / sin(A/2)",
    variables=(("n", "Refractive index", "dimensionless"), ("A", "Prism angle", "rad"), ("delta_m", "Minimum deviation", "rad")),
    description="Relates refractive index to prism geometry.",
    derives_from=("snells_law",),
    status=NodeStatus.PROVEN,
    tags=("prism", "dispersion"),
)

# Cauchy Dispersion
cauchy_dispersion = EquationNode(
    id="cauchy_dispersion",
    name="Cauchy Dispersion Formula",
    domain="optics",
    latex=r"n(\lambda) = A + \frac{B}{\lambda^2} + \frac{C}{\lambda^4} + ...",
    sympy="n = A + B/lambda**2 + C/lambda**4",
    variables=(("n", "Refractive index", "dimensionless"), ("lambda", "Wavelength", "m"), ("A", "Cauchy coefficient", "dimensionless"), ("B", "Cauchy coefficient", "m²")),
    description="Empirical relation for dispersion in transparent materials.",
    status=NodeStatus.EMPIRICAL,
    tags=("dispersion", "material"),
)

# Abbe Number
abbe_number = EquationNode(
    id="abbe_number",
    name="Abbe Number",
    domain="optics",
    latex=r"V_d = \frac{n_d - 1}{n_F - n_C}",
    sympy="V_d = (n_d - 1)/(n_F - n_C)",
    variables=(("V_d", "Abbe number", "dimensionless"), ("n_d", "Index at 589nm", "dimensionless"), ("n_F", "Index at 486nm", "dimensionless"), ("n_C", "Index at 656nm", "dimensionless")),
    description="Measure of dispersion. Higher V = lower dispersion.",
    status=NodeStatus.EMPIRICAL,
    tags=("dispersion", "glass"),
)

NODES = [
    snells_law, critical_angle, reflection_law, thin_lens, lensmaker,
    magnification, mirror_equation, optical_power, numerical_aperture, f_number,
    brewster_angle, fresnel_reflectance, prism_deviation, cauchy_dispersion, abbe_number
]
