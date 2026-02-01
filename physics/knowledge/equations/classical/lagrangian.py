"""
PATH: physics/knowledge/equations/classical/lagrangian.py
PURPOSE: Lagrangian and Hamiltonian mechanics
"""

from physics.knowledge.base.node import EquationNode, PrincipleNode, NodeStatus

# Lagrangian Definition
lagrangian_def = EquationNode(
    id="lagrangian_definition",
    name="Lagrangian",
    domain="classical_mechanics",
    latex=r"L = T - V = KE - PE",
    sympy="L = T - V",
    variables=(("L", "Lagrangian", "J"), ("T", "Kinetic energy", "J"), ("V", "Potential energy", "J")),
    description="Difference of kinetic and potential energy. Central object in analytical mechanics.",
    derives_from=("kinetic_energy",),
    leads_to=("euler_lagrange",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("lagrangian", "analytical_mechanics"),
)

# Euler-Lagrange Equation
euler_lagrange = EquationNode(
    id="euler_lagrange",
    name="Euler-Lagrange Equation",
    domain="classical_mechanics",
    latex=r"\frac{d}{dt}\frac{\partial L}{\partial \dot{q}_i} - \frac{\partial L}{\partial q_i} = 0",
    sympy="d/dt(dL/dqdot) - dL/dq = 0",
    variables=(("L", "Lagrangian", "J"), ("q_i", "Generalized coordinate", "varies"), ("qdot_i", "Generalized velocity", "varies")),
    description="Equations of motion from variational principle. Equivalent to Newton's laws.",
    derives_from=("lagrangian_definition", "principle_least_action"),
    leads_to=("hamiltonian_definition",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("lagrangian", "equation_of_motion"),
)

# Principle of Least Action
least_action = PrincipleNode(
    id="principle_least_action",
    name="Principle of Least Action",
    domain="classical_mechanics",
    statement="The path taken by a system between two states is the one for which the action is stationary (usually minimum).",
    mathematical_form=r"\delta S = \delta \int_{t_1}^{t_2} L \, dt = 0",
    description="Most fundamental principle in physics. Underlies classical, quantum, and relativistic mechanics.",
    leads_to=("euler_lagrange",),
    tags=("variational", "fundamental"),
)

# Action Integral
action_integral = EquationNode(
    id="action_integral",
    name="Action Integral",
    domain="classical_mechanics",
    latex=r"S = \int_{t_1}^{t_2} L(q, \dot{q}, t) \, dt",
    sympy="S = integral(L, t, t1, t2)",
    variables=(("S", "Action", "J⋅s"), ("L", "Lagrangian", "J")),
    description="Integral of Lagrangian over time. Central quantity in path integral formulation.",
    derives_from=("lagrangian_definition",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("action", "variational"),
)

# Generalized Momentum
generalized_momentum = EquationNode(
    id="generalized_momentum",
    name="Generalized (Canonical) Momentum",
    domain="classical_mechanics",
    latex=r"p_i = \frac{\partial L}{\partial \dot{q}_i}",
    sympy="p_i = dL/dqdot_i",
    variables=(("p_i", "Generalized momentum", "varies"), ("L", "Lagrangian", "J"), ("qdot_i", "Generalized velocity", "varies")),
    description="Conjugate momentum to generalized coordinate. Not always mv.",
    derives_from=("lagrangian_definition",),
    leads_to=("hamiltonian_definition",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("momentum", "canonical"),
)

# Hamiltonian Definition
hamiltonian_def = EquationNode(
    id="hamiltonian_definition",
    name="Hamiltonian",
    domain="classical_mechanics",
    latex=r"H = \sum_i p_i \dot{q}_i - L = T + V",
    sympy="H = sum(p_i * qdot_i) - L",
    variables=(("H", "Hamiltonian", "J"), ("p_i", "Generalized momentum", "varies"), ("qdot_i", "Generalized velocity", "varies")),
    description="Total energy in terms of coordinates and momenta. Generates time evolution.",
    derives_from=("lagrangian_definition", "generalized_momentum"),
    leads_to=("hamilton_equations",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("hamiltonian", "energy"),
)

# Hamilton's Equations
hamilton_equations = EquationNode(
    id="hamilton_equations",
    name="Hamilton's Equations",
    domain="classical_mechanics",
    latex=r"\dot{q}_i = \frac{\partial H}{\partial p_i}, \quad \dot{p}_i = -\frac{\partial H}{\partial q_i}",
    sympy="qdot = dH/dp, pdot = -dH/dq",
    variables=(("H", "Hamiltonian", "J"), ("q_i", "Coordinate", "varies"), ("p_i", "Momentum", "varies")),
    description="First-order equations of motion in phase space. Symmetric in q and p.",
    derives_from=("hamiltonian_definition",),
    leads_to=("poisson_bracket", "phase_space_flow"),
    status=NodeStatus.FUNDAMENTAL,
    tags=("hamiltonian", "phase_space"),
)

# Poisson Bracket
poisson_bracket = EquationNode(
    id="poisson_bracket",
    name="Poisson Bracket",
    domain="classical_mechanics",
    latex=r"\{f, g\} = \sum_i \left(\frac{\partial f}{\partial q_i}\frac{\partial g}{\partial p_i} - \frac{\partial f}{\partial p_i}\frac{\partial g}{\partial q_i}\right)",
    sympy="{f, g} = sum(df/dq * dg/dp - df/dp * dg/dq)",
    variables=(("f", "Phase space function", "varies"), ("g", "Phase space function", "varies")),
    description="Fundamental bracket structure. {q,p}=1. Becomes commutator in QM.",
    derives_from=("hamilton_equations",),
    leads_to=("canonical_commutation",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("bracket", "symplectic"),
)

# Time Evolution via Poisson Bracket
poisson_evolution = EquationNode(
    id="poisson_time_evolution",
    name="Time Evolution (Poisson)",
    domain="classical_mechanics",
    latex=r"\frac{df}{dt} = \{f, H\} + \frac{\partial f}{\partial t}",
    sympy="df/dt = {f, H} + df/dt_partial",
    variables=(("f", "Observable", "varies"), ("H", "Hamiltonian", "J")),
    description="Time evolution of any observable in Hamiltonian mechanics.",
    derives_from=("poisson_bracket", "hamiltonian_definition"),
    status=NodeStatus.PROVEN,
    tags=("evolution", "poisson"),
)

# Canonical Transformation
canonical_transform = EquationNode(
    id="canonical_transformation",
    name="Canonical Transformation",
    domain="classical_mechanics",
    latex=r"(q, p) \to (Q, P): \quad \{Q_i, P_j\} = \delta_{ij}",
    sympy="{Q, P} = delta_ij",
    variables=(("Q", "New coordinates", "varies"), ("P", "New momenta", "varies")),
    description="Transformation preserving Poisson bracket structure. Hamilton's equations remain valid.",
    derives_from=("poisson_bracket",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("transformation", "symplectic"),
)

# Generating Function
generating_function = EquationNode(
    id="generating_function",
    name="Generating Function",
    domain="classical_mechanics",
    latex=r"p_i = \frac{\partial F_1}{\partial q_i}, \quad P_i = -\frac{\partial F_1}{\partial Q_i}",
    sympy="p = dF1/dq, P = -dF1/dQ",
    variables=(("F_1", "Type-1 generating function", "J"), ("q", "Old coord", "varies"), ("Q", "New coord", "varies")),
    description="Function generating canonical transformation. Four types: F1(q,Q), F2(q,P), F3(p,Q), F4(p,P).",
    derives_from=("canonical_transformation",),
    status=NodeStatus.PROVEN,
    tags=("transformation", "generating"),
)

# Hamilton-Jacobi Equation
hamilton_jacobi = EquationNode(
    id="hamilton_jacobi",
    name="Hamilton-Jacobi Equation",
    domain="classical_mechanics",
    latex=r"H\left(q_i, \frac{\partial S}{\partial q_i}, t\right) + \frac{\partial S}{\partial t} = 0",
    sympy="H(q, dS/dq, t) + dS/dt = 0",
    variables=(("S", "Hamilton's principal function", "J⋅s"), ("H", "Hamiltonian", "J")),
    description="PDE for action. Solution gives complete solution to mechanics. Bridge to quantum mechanics.",
    derives_from=("hamiltonian_definition", "action_integral"),
    leads_to=("schrodinger_time_dependent",),
    status=NodeStatus.FUNDAMENTAL,
    tags=("hamilton_jacobi", "action"),
)

# Liouville's Theorem
liouville_theorem = EquationNode(
    id="liouville_theorem",
    name="Liouville's Theorem",
    domain="classical_mechanics",
    latex=r"\frac{d\rho}{dt} = 0 \quad \text{or} \quad \nabla \cdot \vec{v} = 0 \text{ in phase space}",
    sympy="drho/dt = 0",
    variables=(("rho", "Phase space density", "1/(J⋅s)^n")),
    description="Phase space density is conserved along trajectories. Volume in phase space preserved.",
    derives_from=("hamilton_equations",),
    status=NodeStatus.PROVEN,
    tags=("phase_space", "conservation"),
)

# Noether's Theorem
noether_theorem = EquationNode(
    id="noether_theorem",
    name="Noether's Theorem",
    domain="classical_mechanics",
    latex=r"\text{Symmetry} \leftrightarrow \text{Conservation Law}",
    sympy="symmetry <-> conservation",
    variables=(),
    description="Every continuous symmetry gives a conserved quantity. Time→Energy, Space→Momentum, Rotation→Angular momentum.",
    derives_from=("euler_lagrange",),
    leads_to=("momentum_conservation", "angular_momentum_conservation"),
    status=NodeStatus.PROVEN,
    tags=("symmetry", "conservation", "fundamental"),
)

# Cyclic Coordinate
cyclic_coordinate = EquationNode(
    id="cyclic_coordinate",
    name="Cyclic (Ignorable) Coordinate",
    domain="classical_mechanics",
    latex=r"\frac{\partial L}{\partial q_i} = 0 \Rightarrow p_i = \text{const}",
    sympy="dL/dq = 0 => p = const",
    variables=(("q_i", "Cyclic coordinate", "varies"), ("p_i", "Conjugate momentum", "varies")),
    description="If L doesn't depend on q_i, conjugate momentum p_i is conserved.",
    derives_from=("euler_lagrange",),
    status=NodeStatus.PROVEN,
    tags=("symmetry", "conservation"),
)

# Routhian
routhian = EquationNode(
    id="routhian",
    name="Routhian",
    domain="classical_mechanics",
    latex=r"R = p_\theta \dot{\theta} - L",
    sympy="R = p_theta * theta_dot - L",
    variables=(("R", "Routhian", "J")),
    description="Hybrid of Lagrangian and Hamiltonian. Useful when some coordinates are cyclic.",
    derives_from=("lagrangian_definition", "hamiltonian_definition"),
    status=NodeStatus.PROVEN,
    tags=("routhian", "hybrid"),
)

NODES = [
    lagrangian_def, euler_lagrange, least_action, action_integral, generalized_momentum,
    hamiltonian_def, hamilton_equations, poisson_bracket, poisson_evolution,
    canonical_transform, generating_function, hamilton_jacobi, liouville_theorem,
    noether_theorem, cyclic_coordinate, routhian
]
