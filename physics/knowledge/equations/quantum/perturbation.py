"""
PATH: physics/knowledge/equations/quantum/perturbation.py
PURPOSE: Quantum perturbation theory equations
"""

from physics.knowledge.base.node import EquationNode, NodeStatus

# Time-Independent First Order Energy
perturbation_energy_1 = EquationNode(
    id="perturbation_energy_first",
    name="First-Order Energy Correction",
    domain="quantum_mechanics",
    latex=r"E_n^{(1)} = \langle n^{(0)}|H'|n^{(0)}\rangle",
    sympy="E_n_1 = <n|H_prime|n>",
    variables=(("E_n_1", "First-order energy correction", "J"), ("H_prime", "Perturbation Hamiltonian", "J")),
    description="First-order energy correction = expectation value of perturbation in unperturbed state.",
    status=NodeStatus.PROVEN,
    tags=("perturbation", "energy"),
)

# First Order State
perturbation_state_1 = EquationNode(
    id="perturbation_state_first",
    name="First-Order State Correction",
    domain="quantum_mechanics",
    latex=r"|n^{(1)}\rangle = \sum_{m \neq n} \frac{\langle m^{(0)}|H'|n^{(0)}\rangle}{E_n^{(0)} - E_m^{(0)}}|m^{(0)}\rangle",
    sympy="|n_1> = sum(<m|H'|n>/(E_n - E_m)*|m>)",
    variables=(),
    description="First-order state correction. Sum over all other unperturbed states.",
    status=NodeStatus.PROVEN,
    tags=("perturbation", "state"),
)

# Second Order Energy
perturbation_energy_2 = EquationNode(
    id="perturbation_energy_second",
    name="Second-Order Energy Correction",
    domain="quantum_mechanics",
    latex=r"E_n^{(2)} = \sum_{m \neq n} \frac{|\langle m^{(0)}|H'|n^{(0)}\rangle|^2}{E_n^{(0)} - E_m^{(0)}}",
    sympy="E_n_2 = sum(|<m|H'|n>|**2/(E_n - E_m))",
    variables=(("E_n_2", "Second-order energy correction", "J")),
    description="Second-order correction always lowers ground state energy.",
    derives_from=("perturbation_state_first",),
    status=NodeStatus.PROVEN,
    tags=("perturbation", "energy"),
)

# Degenerate Perturbation
degenerate_perturbation = EquationNode(
    id="degenerate_perturbation",
    name="Degenerate Perturbation Theory",
    domain="quantum_mechanics",
    latex=r"\det(H'_{ij} - E^{(1)}\delta_{ij}) = 0",
    sympy="det(H'_ij - E_1*delta_ij) = 0",
    variables=(("H'_ij", "Perturbation matrix elements", "J")),
    description="Diagonalize H' in degenerate subspace to find proper zeroth-order states.",
    status=NodeStatus.PROVEN,
    tags=("perturbation", "degenerate"),
)

# Time-Dependent First Order
time_dependent_perturbation = EquationNode(
    id="time_dependent_perturbation",
    name="Time-Dependent Perturbation",
    domain="quantum_mechanics",
    latex=r"c_f^{(1)}(t) = -\frac{i}{\hbar}\int_0^t \langle f|H'(t')|i\rangle e^{i\omega_{fi}t'} dt'",
    sympy="c_f_1 = -i/hbar * integral(<f|H'|i>*exp(i*omega*t), t, 0, t)",
    variables=(("c_f", "Transition amplitude", "dimensionless"), ("omega_fi", "(E_f - E_i)/ℏ", "rad/s")),
    description="Amplitude for transition from state i to f under perturbation H'(t).",
    uses=("hbar",),
    status=NodeStatus.PROVEN,
    tags=("perturbation", "time_dependent"),
)

# Fermi's Golden Rule
fermis_golden_rule = EquationNode(
    id="fermis_golden_rule_qm",
    name="Fermi's Golden Rule",
    domain="quantum_mechanics",
    latex=r"\Gamma_{i\to f} = \frac{2\pi}{\hbar}|\langle f|H'|i\rangle|^2 \rho(E_f)",
    sympy="Gamma = 2*pi/hbar * |<f|H'|i>|**2 * rho_E",
    variables=(("Gamma", "Transition rate", "s⁻¹"), ("rho_E", "Density of final states", "J⁻¹")),
    description="Transition rate for constant perturbation switched on at t=0.",
    derives_from=("time_dependent_perturbation",),
    uses=("hbar",),
    status=NodeStatus.PROVEN,
    tags=("transition", "rate"),
)

# Stark Effect
stark_effect = EquationNode(
    id="stark_effect",
    name="Stark Effect",
    domain="quantum_mechanics",
    latex=r"\Delta E^{(1)} = \langle n|e\vec{r}\cdot\vec{E}|n\rangle = 0 \text{ (usually)}, \quad \Delta E^{(2)} = -\frac{1}{2}\alpha E^2",
    sympy="delta_E_2 = -(1/2)*alpha*E**2",
    variables=(("alpha", "Polarizability", "C⋅m²/V")),
    description="Energy shift in electric field. Usually quadratic (second-order).",
    derives_from=("perturbation_energy_second",),
    status=NodeStatus.EXPERIMENTAL,
    tags=("electric", "splitting"),
)

# Fine Structure
fine_structure = EquationNode(
    id="fine_structure",
    name="Hydrogen Fine Structure",
    domain="quantum_mechanics",
    latex=r"\Delta E_{fs} = -\frac{E_n^{(0)}}{n}\left(\frac{\alpha^2}{n}\right)\left(\frac{1}{j+1/2} - \frac{3}{4n}\right)",
    sympy="delta_E_fs = -E_n*alpha**2/n * (1/(j+1/2) - 3/(4*n))",
    variables=(("alpha", "Fine structure constant", "dimensionless"), ("j", "Total angular momentum", "dimensionless")),
    description="Relativistic and spin-orbit corrections. Splits levels by j value.",
    uses=("alpha",),
    status=NodeStatus.PROVEN,
    tags=("hydrogen", "relativistic"),
)

# Lamb Shift
lamb_shift = EquationNode(
    id="lamb_shift",
    name="Lamb Shift",
    domain="quantum_mechanics",
    latex=r"\Delta E_{Lamb} \approx \frac{\alpha^5 m_e c^2}{4\pi^3 n^3}\left(\ln\frac{1}{\alpha^2} + ...\right)",
    sympy="delta_E_lamb ~ alpha**5 * m_e*c**2 / (4*pi**3*n**3)",
    variables=(),
    description="QED correction lifting 2S₁/₂ - 2P₁/₂ degeneracy. ~1057 MHz for H.",
    uses=("alpha", "m_e", "c"),
    status=NodeStatus.EXPERIMENTAL,
    tags=("qed", "correction"),
)

# Hyperfine Structure
hyperfine = EquationNode(
    id="hyperfine_structure",
    name="Hyperfine Structure",
    domain="quantum_mechanics",
    latex=r"\Delta E_{hfs} = A_{hfs}[\vec{I}\cdot\vec{J}] = \frac{A_{hfs}}{2}[F(F+1) - I(I+1) - J(J+1)]",
    sympy="delta_E_hfs = A_hfs/2 * (F*(F+1) - I*(I+1) - J*(J+1))",
    variables=(("A_hfs", "Hyperfine constant", "Hz"), ("I", "Nuclear spin", "dimensionless"), ("J", "Electron angular momentum", "dimensionless"), ("F", "Total angular momentum", "dimensionless")),
    description="Electron-nucleus magnetic interaction. 21 cm line from H hyperfine.",
    status=NodeStatus.EXPERIMENTAL,
    tags=("hyperfine", "nuclear"),
)

# Variational Principle
variational = EquationNode(
    id="variational_principle",
    name="Variational Principle",
    domain="quantum_mechanics",
    latex=r"E_{trial} = \frac{\langle\psi_{trial}|H|\psi_{trial}\rangle}{\langle\psi_{trial}|\psi_{trial}\rangle} \geq E_0",
    sympy="E_trial = <psi|H|psi>/<psi|psi> >= E_0",
    variables=(("E_trial", "Variational energy", "J"), ("E_0", "True ground state energy", "J")),
    description="Any trial wave function gives upper bound on ground state energy.",
    status=NodeStatus.PROVEN,
    tags=("variational", "bound"),
)

# WKB Approximation
wkb = EquationNode(
    id="wkb_approximation",
    name="WKB Approximation",
    domain="quantum_mechanics",
    latex=r"\psi \approx \frac{C}{\sqrt{p(x)}}e^{\pm\frac{i}{\hbar}\int p(x')dx'}, \quad p(x) = \sqrt{2m(E-V(x))}",
    sympy="psi ~ 1/sqrt(p)*exp(i/hbar*integral(p))",
    variables=(("p", "Local momentum", "kg⋅m/s")),
    description="Semiclassical approximation. Valid when potential varies slowly.",
    uses=("hbar",),
    status=NodeStatus.APPROXIMATE,
    tags=("semiclassical", "approximation"),
)

NODES = [
    perturbation_energy_1, perturbation_state_1, perturbation_energy_2, degenerate_perturbation,
    time_dependent_perturbation, fermis_golden_rule, stark_effect, fine_structure,
    lamb_shift, hyperfine, variational, wkb
]
