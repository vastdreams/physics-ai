"""
PATH: physics/knowledge/equations/electromagnetism/circuits.py
PURPOSE: Circuit equations - AC/DC, RLC, transmission lines
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Kirchhoff's Voltage Law
kvl = EquationNode(
    id="kirchhoff_voltage",
    name="Kirchhoff's Voltage Law",
    domain="electromagnetism",
    latex=r"\sum_{\text{loop}} V_i = 0",
    sympy="sum(V_i) = 0",
    variables=(("V_i", "Voltage drop", "V"),),
    description="Sum of voltages around closed loop is zero. Conservation of energy.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("circuit", "conservation"),
)

# Kirchhoff's Current Law
kcl = EquationNode(
    id="kirchhoff_current",
    name="Kirchhoff's Current Law",
    domain="electromagnetism",
    latex=r"\sum_{\text{node}} I_i = 0",
    sympy="sum(I_i) = 0",
    variables=(("I_i", "Current", "A"),),
    description="Sum of currents at node is zero. Conservation of charge.",
    status=NodeStatus.FUNDAMENTAL,
    tags=("circuit", "conservation"),
)

# Power in Resistor
resistor_power = EquationNode(
    id="resistor_power",
    name="Resistor Power Dissipation",
    domain="electromagnetism",
    latex=r"P = IV = I^2R = \frac{V^2}{R}",
    sympy="P = I * V = I**2 * R = V**2 / R",
    variables=(("P", "Power", "W"), ("I", "Current", "A"), ("V", "Voltage", "V"), ("R", "Resistance", "Ω")),
    description="Power dissipated in resistor as heat.",
    derives_from=("ohm_law",),
    status=NodeStatus.PROVEN,
    tags=("power", "resistor"),
)

# Series Resistance
series_resistance = EquationNode(
    id="series_resistance",
    name="Series Resistance",
    domain="electromagnetism",
    latex=r"R_{eq} = R_1 + R_2 + ... + R_n",
    sympy="R_eq = sum(R_i)",
    variables=(("R_eq", "Equivalent resistance", "Ω"),),
    description="Resistances in series add.",
    status=NodeStatus.PROVEN,
    tags=("circuit", "series"),
)

# Parallel Resistance
parallel_resistance = EquationNode(
    id="parallel_resistance",
    name="Parallel Resistance",
    domain="electromagnetism",
    latex=r"\frac{1}{R_{eq}} = \frac{1}{R_1} + \frac{1}{R_2} + ... + \frac{1}{R_n}",
    sympy="1/R_eq = sum(1/R_i)",
    variables=(("R_eq", "Equivalent resistance", "Ω"),),
    description="Reciprocals of resistances in parallel add.",
    status=NodeStatus.PROVEN,
    tags=("circuit", "parallel"),
)

# Series Capacitance
series_capacitance = EquationNode(
    id="series_capacitance",
    name="Series Capacitance",
    domain="electromagnetism",
    latex=r"\frac{1}{C_{eq}} = \frac{1}{C_1} + \frac{1}{C_2} + ... + \frac{1}{C_n}",
    sympy="1/C_eq = sum(1/C_i)",
    variables=(("C_eq", "Equivalent capacitance", "F"),),
    description="Reciprocals of capacitances in series add.",
    status=NodeStatus.PROVEN,
    tags=("circuit", "series"),
)

# Parallel Capacitance
parallel_capacitance = EquationNode(
    id="parallel_capacitance",
    name="Parallel Capacitance",
    domain="electromagnetism",
    latex=r"C_{eq} = C_1 + C_2 + ... + C_n",
    sympy="C_eq = sum(C_i)",
    variables=(("C_eq", "Equivalent capacitance", "F"),),
    description="Capacitances in parallel add.",
    status=NodeStatus.PROVEN,
    tags=("circuit", "parallel"),
)

# Inductance Equation
inductance_eq = EquationNode(
    id="inductance_equation",
    name="Inductor Voltage",
    domain="electromagnetism",
    latex=r"V_L = L\frac{dI}{dt}",
    sympy="V_L = L * dI/dt",
    variables=(("V_L", "Inductor voltage", "V"), ("L", "Inductance", "H"), ("I", "Current", "A")),
    description="Voltage across inductor proportional to rate of current change.",
    derives_from=("faraday_law",),
    status=NodeStatus.PROVEN,
    tags=("inductor", "voltage"),
)

# Inductor Energy
inductor_energy = EquationNode(
    id="inductor_energy",
    name="Inductor Stored Energy",
    domain="electromagnetism",
    latex=r"E = \frac{1}{2}LI^2",
    sympy="E = (1/2) * L * I**2",
    variables=(("E", "Energy", "J"), ("L", "Inductance", "H"), ("I", "Current", "A")),
    description="Energy stored in magnetic field of inductor.",
    status=NodeStatus.PROVEN,
    tags=("inductor", "energy"),
)

# Capacitor Energy
capacitor_energy = EquationNode(
    id="capacitor_energy",
    name="Capacitor Stored Energy",
    domain="electromagnetism",
    latex=r"E = \frac{1}{2}CV^2 = \frac{Q^2}{2C}",
    sympy="E = (1/2) * C * V**2",
    variables=(("E", "Energy", "J"), ("C", "Capacitance", "F"), ("V", "Voltage", "V")),
    description="Energy stored in electric field of capacitor.",
    status=NodeStatus.PROVEN,
    tags=("capacitor", "energy"),
)

# RC Time Constant
rc_time = EquationNode(
    id="rc_time_constant",
    name="RC Time Constant",
    domain="electromagnetism",
    latex=r"\tau = RC",
    sympy="tau = R * C",
    variables=(("tau", "Time constant", "s"), ("R", "Resistance", "Ω"), ("C", "Capacitance", "F")),
    description="Time for capacitor to charge/discharge to 63% or 37%.",
    status=NodeStatus.PROVEN,
    tags=("rc", "transient"),
)

# RC Charging
rc_charging = EquationNode(
    id="rc_charging",
    name="RC Circuit Charging",
    domain="electromagnetism",
    latex=r"V_C(t) = V_0(1 - e^{-t/RC})",
    sympy="V_C = V_0 * (1 - exp(-t/(R*C)))",
    variables=(("V_C", "Capacitor voltage", "V"), ("V_0", "Supply voltage", "V"), ("t", "Time", "s")),
    description="Capacitor voltage during charging.",
    derives_from=("rc_time_constant",),
    status=NodeStatus.PROVEN,
    tags=("rc", "transient"),
)

# RL Time Constant
rl_time = EquationNode(
    id="rl_time_constant",
    name="RL Time Constant",
    domain="electromagnetism",
    latex=r"\tau = \frac{L}{R}",
    sympy="tau = L / R",
    variables=(("tau", "Time constant", "s"), ("L", "Inductance", "H"), ("R", "Resistance", "Ω")),
    description="Time for inductor current to reach 63% of final value.",
    status=NodeStatus.PROVEN,
    tags=("rl", "transient"),
)

# RLC Resonance Frequency
rlc_resonance = EquationNode(
    id="rlc_resonance",
    name="RLC Resonance Frequency",
    domain="electromagnetism",
    latex=r"f_0 = \frac{1}{2\pi\sqrt{LC}} \quad \omega_0 = \frac{1}{\sqrt{LC}}",
    sympy="f_0 = 1/(2*pi*sqrt(L*C))",
    variables=(("f_0", "Resonant frequency", "Hz"), ("L", "Inductance", "H"), ("C", "Capacitance", "F")),
    description="Natural frequency of LC oscillation.",
    status=NodeStatus.PROVEN,
    tags=("resonance", "rlc"),
)

# Quality Factor
quality_factor = EquationNode(
    id="quality_factor",
    name="Quality Factor (Q)",
    domain="electromagnetism",
    latex=r"Q = \frac{\omega_0 L}{R} = \frac{1}{R}\sqrt{\frac{L}{C}}",
    sympy="Q = omega_0 * L / R",
    variables=(("Q", "Quality factor", "dimensionless"), ("omega_0", "Resonant frequency", "rad/s"), ("L", "Inductance", "H"), ("R", "Resistance", "Ω")),
    description="Sharpness of resonance. Higher Q = sharper peak, lower damping.",
    status=NodeStatus.PROVEN,
    tags=("resonance", "damping"),
)

# Impedance
impedance = EquationNode(
    id="impedance",
    name="Impedance",
    domain="electromagnetism",
    latex=r"Z = R + j(X_L - X_C) = R + j(\omega L - \frac{1}{\omega C})",
    sympy="Z = R + j*(omega*L - 1/(omega*C))",
    variables=(("Z", "Impedance", "Ω"), ("R", "Resistance", "Ω"), ("X_L", "Inductive reactance", "Ω"), ("X_C", "Capacitive reactance", "Ω")),
    description="Complex opposition to AC current. Z = V/I in phasor form.",
    status=NodeStatus.PROVEN,
    tags=("ac", "impedance"),
)

# Inductive Reactance
inductive_reactance = EquationNode(
    id="inductive_reactance",
    name="Inductive Reactance",
    domain="electromagnetism",
    latex=r"X_L = \omega L = 2\pi f L",
    sympy="X_L = omega * L",
    variables=(("X_L", "Inductive reactance", "Ω"), ("omega", "Angular frequency", "rad/s"), ("L", "Inductance", "H")),
    description="Opposition to AC by inductor. Increases with frequency.",
    status=NodeStatus.PROVEN,
    tags=("ac", "reactance"),
)

# Capacitive Reactance
capacitive_reactance = EquationNode(
    id="capacitive_reactance",
    name="Capacitive Reactance",
    domain="electromagnetism",
    latex=r"X_C = \frac{1}{\omega C} = \frac{1}{2\pi f C}",
    sympy="X_C = 1/(omega * C)",
    variables=(("X_C", "Capacitive reactance", "Ω"), ("omega", "Angular frequency", "rad/s"), ("C", "Capacitance", "F")),
    description="Opposition to AC by capacitor. Decreases with frequency.",
    status=NodeStatus.PROVEN,
    tags=("ac", "reactance"),
)

# Power Factor
power_factor = EquationNode(
    id="power_factor",
    name="Power Factor",
    domain="electromagnetism",
    latex=r"PF = \cos\phi = \frac{P}{S} = \frac{R}{|Z|}",
    sympy="PF = cos(phi) = R/|Z|",
    variables=(("PF", "Power factor", "dimensionless"), ("phi", "Phase angle", "rad"), ("P", "Real power", "W"), ("S", "Apparent power", "VA")),
    description="Ratio of real to apparent power. PF=1 for resistive load.",
    status=NodeStatus.PROVEN,
    tags=("ac", "power"),
)

# Transformer Equation
transformer = EquationNode(
    id="transformer_equation",
    name="Ideal Transformer",
    domain="electromagnetism",
    latex=r"\frac{V_s}{V_p} = \frac{N_s}{N_p} = \frac{I_p}{I_s}",
    sympy="V_s/V_p = N_s/N_p",
    variables=(("V_s", "Secondary voltage", "V"), ("V_p", "Primary voltage", "V"), ("N_s", "Secondary turns", "dimensionless"), ("N_p", "Primary turns", "dimensionless")),
    description="Voltage and current ratios in ideal transformer.",
    derives_from=("faraday_law",),
    status=NodeStatus.PROVEN,
    tags=("transformer", "ac"),
)

# Transmission Line Impedance
transmission_impedance = EquationNode(
    id="transmission_line_impedance",
    name="Characteristic Impedance",
    domain="electromagnetism",
    latex=r"Z_0 = \sqrt{\frac{L'}{C'}} \approx \sqrt{\frac{\mu}{\epsilon}} \text{ (lossless)}",
    sympy="Z_0 = sqrt(L_prime/C_prime)",
    variables=(("Z_0", "Characteristic impedance", "Ω"), ("L_prime", "Inductance per length", "H/m"), ("C_prime", "Capacitance per length", "F/m")),
    description="Impedance of transmission line. ~377Ω for free space.",
    status=NodeStatus.PROVEN,
    tags=("transmission_line", "rf"),
)

# Standing Wave Ratio
swr = EquationNode(
    id="standing_wave_ratio",
    name="Standing Wave Ratio (SWR)",
    domain="electromagnetism",
    latex=r"SWR = \frac{1 + |\Gamma|}{1 - |\Gamma|} \quad \Gamma = \frac{Z_L - Z_0}{Z_L + Z_0}",
    sympy="SWR = (1 + |Gamma|)/(1 - |Gamma|)",
    variables=(("SWR", "Standing wave ratio", "dimensionless"), ("Gamma", "Reflection coefficient", "dimensionless"), ("Z_L", "Load impedance", "Ω"), ("Z_0", "Line impedance", "Ω")),
    description="Measure of impedance mismatch. SWR=1 for perfect match.",
    status=NodeStatus.PROVEN,
    tags=("transmission_line", "rf"),
)

NODES = [
    kvl, kcl, resistor_power, series_resistance, parallel_resistance,
    series_capacitance, parallel_capacitance, inductance_eq, inductor_energy, capacitor_energy,
    rc_time, rc_charging, rl_time, rlc_resonance, quality_factor,
    impedance, inductive_reactance, capacitive_reactance, power_factor,
    transformer, transmission_impedance, swr
]
