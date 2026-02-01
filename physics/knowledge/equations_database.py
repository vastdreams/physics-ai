"""
PATH: physics/knowledge/equations_database.py
PURPOSE: Comprehensive database of all proven physics equations, constants, and their relationships.

FIRST PRINCIPLES APPROACH:
This module encodes physics knowledge from fundamental axioms upward:
1. Start with fundamental constants (measured values)
2. Build fundamental laws (empirically verified)
3. Derive relationships between equations
4. Track which equations derive from which

ORGANIZATION:
- Constants: Fundamental measured values
- Equations: Organized by domain (mechanics, EM, QM, thermo, relativity, nuclear)
- Relations: How equations connect to each other
- Derivations: First-principles derivation chains

DEPENDENCIES:
- sympy: Symbolic mathematics
- dataclasses: Structured data
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from enum import Enum
import math


class PhysicsDomain(Enum):
    """Physics domains for categorization."""
    FUNDAMENTAL = "fundamental"
    CLASSICAL_MECHANICS = "classical_mechanics"
    ELECTROMAGNETISM = "electromagnetism"
    THERMODYNAMICS = "thermodynamics"
    STATISTICAL_MECHANICS = "statistical_mechanics"
    QUANTUM_MECHANICS = "quantum_mechanics"
    SPECIAL_RELATIVITY = "special_relativity"
    GENERAL_RELATIVITY = "general_relativity"
    NUCLEAR_PHYSICS = "nuclear_physics"
    PARTICLE_PHYSICS = "particle_physics"
    FLUID_DYNAMICS = "fluid_dynamics"
    OPTICS = "optics"
    SOLID_STATE = "solid_state"
    COSMOLOGY = "cosmology"


class EquationStatus(Enum):
    """Verification status of equations."""
    FUNDAMENTAL = "fundamental"  # Axiom/postulate
    PROVEN = "proven"  # Mathematically derived
    EMPIRICAL = "empirical"  # Experimentally verified
    THEORETICAL = "theoretical"  # Predicted but not fully verified


@dataclass
class PhysicalConstant:
    """A physical constant with metadata."""
    name: str
    symbol: str
    value: float
    unit: str
    uncertainty: float  # Relative uncertainty
    description: str
    domain: PhysicsDomain
    is_exact: bool = False  # True for defined constants (like c)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'symbol': self.symbol,
            'value': self.value,
            'unit': self.unit,
            'uncertainty': self.uncertainty,
            'description': self.description,
            'domain': self.domain.value,
            'is_exact': self.is_exact
        }


@dataclass
class PhysicsEquation:
    """A physics equation with full metadata."""
    name: str
    equation: str  # Symbolic form (e.g., "F = m * a")
    latex: str  # LaTeX representation
    description: str
    domain: PhysicsDomain
    status: EquationStatus
    variables: Dict[str, str]  # Variable name -> description
    derived_from: List[str] = field(default_factory=list)  # Parent equations
    leads_to: List[str] = field(default_factory=list)  # Child equations
    conditions: List[str] = field(default_factory=list)  # When applicable
    first_principle_derivation: Optional[str] = None
    discoverer: Optional[str] = None
    year_discovered: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'equation': self.equation,
            'latex': self.latex,
            'description': self.description,
            'domain': self.domain.value,
            'status': self.status.value,
            'variables': self.variables,
            'derived_from': self.derived_from,
            'leads_to': self.leads_to,
            'conditions': self.conditions,
            'first_principle_derivation': self.first_principle_derivation,
            'discoverer': self.discoverer,
            'year_discovered': self.year_discovered
        }


class PhysicsConstantsDatabase:
    """
    Complete database of physical constants.
    
    Organized by:
    1. Universal constants
    2. Electromagnetic constants
    3. Atomic/nuclear constants
    4. Particle masses
    5. Coupling constants
    """
    
    def __init__(self):
        self.constants: Dict[str, PhysicalConstant] = {}
        self._initialize_constants()
    
    def _initialize_constants(self):
        """Initialize all physical constants."""
        
        # ============================================================
        # UNIVERSAL CONSTANTS (Exact by definition in SI)
        # ============================================================
        
        self._add(PhysicalConstant(
            name="Speed of light in vacuum",
            symbol="c",
            value=299792458,
            unit="m/s",
            uncertainty=0,
            description="Maximum speed of information/causality in the universe",
            domain=PhysicsDomain.FUNDAMENTAL,
            is_exact=True
        ))
        
        self._add(PhysicalConstant(
            name="Planck constant",
            symbol="h",
            value=6.62607015e-34,
            unit="J*s",
            uncertainty=0,
            description="Quantum of action, relates energy to frequency",
            domain=PhysicsDomain.QUANTUM_MECHANICS,
            is_exact=True
        ))
        
        self._add(PhysicalConstant(
            name="Reduced Planck constant",
            symbol="hbar",
            value=1.054571817e-34,
            unit="J*s",
            uncertainty=0,
            description="h/(2*pi), fundamental quantum scale",
            domain=PhysicsDomain.QUANTUM_MECHANICS,
            is_exact=True
        ))
        
        self._add(PhysicalConstant(
            name="Elementary charge",
            symbol="e",
            value=1.602176634e-19,
            unit="C",
            uncertainty=0,
            description="Charge of electron/proton",
            domain=PhysicsDomain.ELECTROMAGNETISM,
            is_exact=True
        ))
        
        self._add(PhysicalConstant(
            name="Boltzmann constant",
            symbol="k_B",
            value=1.380649e-23,
            unit="J/K",
            uncertainty=0,
            description="Relates temperature to energy",
            domain=PhysicsDomain.THERMODYNAMICS,
            is_exact=True
        ))
        
        self._add(PhysicalConstant(
            name="Avogadro constant",
            symbol="N_A",
            value=6.02214076e23,
            unit="1/mol",
            uncertainty=0,
            description="Number of particles per mole",
            domain=PhysicsDomain.THERMODYNAMICS,
            is_exact=True
        ))
        
        # ============================================================
        # GRAVITATIONAL CONSTANTS
        # ============================================================
        
        self._add(PhysicalConstant(
            name="Gravitational constant",
            symbol="G",
            value=6.67430e-11,
            unit="m^3/(kg*s^2)",
            uncertainty=2.2e-5,
            description="Strength of gravitational interaction",
            domain=PhysicsDomain.CLASSICAL_MECHANICS
        ))
        
        self._add(PhysicalConstant(
            name="Standard gravity",
            symbol="g",
            value=9.80665,
            unit="m/s^2",
            uncertainty=0,
            description="Standard gravitational acceleration on Earth",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            is_exact=True
        ))
        
        # ============================================================
        # ELECTROMAGNETIC CONSTANTS
        # ============================================================
        
        self._add(PhysicalConstant(
            name="Vacuum permittivity",
            symbol="epsilon_0",
            value=8.8541878128e-12,
            unit="F/m",
            uncertainty=1.5e-10,
            description="Electric constant, permittivity of free space",
            domain=PhysicsDomain.ELECTROMAGNETISM
        ))
        
        self._add(PhysicalConstant(
            name="Vacuum permeability",
            symbol="mu_0",
            value=1.25663706212e-6,
            unit="H/m",
            uncertainty=1.5e-10,
            description="Magnetic constant, permeability of free space",
            domain=PhysicsDomain.ELECTROMAGNETISM
        ))
        
        self._add(PhysicalConstant(
            name="Coulomb constant",
            symbol="k_e",
            value=8.9875517923e9,
            unit="N*m^2/C^2",
            uncertainty=1.5e-10,
            description="1/(4*pi*epsilon_0), electrostatic constant",
            domain=PhysicsDomain.ELECTROMAGNETISM
        ))
        
        self._add(PhysicalConstant(
            name="Impedance of free space",
            symbol="Z_0",
            value=376.730313668,
            unit="Ohm",
            uncertainty=1.5e-10,
            description="sqrt(mu_0/epsilon_0), characteristic impedance of vacuum",
            domain=PhysicsDomain.ELECTROMAGNETISM
        ))
        
        # ============================================================
        # PARTICLE MASSES
        # ============================================================
        
        self._add(PhysicalConstant(
            name="Electron mass",
            symbol="m_e",
            value=9.1093837015e-31,
            unit="kg",
            uncertainty=3.0e-10,
            description="Rest mass of electron",
            domain=PhysicsDomain.PARTICLE_PHYSICS
        ))
        
        self._add(PhysicalConstant(
            name="Proton mass",
            symbol="m_p",
            value=1.67262192369e-27,
            unit="kg",
            uncertainty=3.1e-10,
            description="Rest mass of proton",
            domain=PhysicsDomain.PARTICLE_PHYSICS
        ))
        
        self._add(PhysicalConstant(
            name="Neutron mass",
            symbol="m_n",
            value=1.67492749804e-27,
            unit="kg",
            uncertainty=5.7e-10,
            description="Rest mass of neutron",
            domain=PhysicsDomain.PARTICLE_PHYSICS
        ))
        
        self._add(PhysicalConstant(
            name="Muon mass",
            symbol="m_mu",
            value=1.883531627e-28,
            unit="kg",
            uncertainty=2.2e-8,
            description="Rest mass of muon",
            domain=PhysicsDomain.PARTICLE_PHYSICS
        ))
        
        self._add(PhysicalConstant(
            name="Tau mass",
            symbol="m_tau",
            value=3.16754e-27,
            unit="kg",
            uncertainty=9.5e-5,
            description="Rest mass of tau lepton",
            domain=PhysicsDomain.PARTICLE_PHYSICS
        ))
        
        self._add(PhysicalConstant(
            name="Atomic mass unit",
            symbol="u",
            value=1.66053906660e-27,
            unit="kg",
            uncertainty=3.0e-10,
            description="1/12 of carbon-12 mass",
            domain=PhysicsDomain.NUCLEAR_PHYSICS
        ))
        
        # ============================================================
        # COUPLING CONSTANTS
        # ============================================================
        
        self._add(PhysicalConstant(
            name="Fine structure constant",
            symbol="alpha",
            value=7.2973525693e-3,
            unit="dimensionless",
            uncertainty=1.5e-10,
            description="e^2/(4*pi*epsilon_0*hbar*c), EM coupling strength",
            domain=PhysicsDomain.QUANTUM_MECHANICS
        ))
        
        self._add(PhysicalConstant(
            name="Weak coupling constant",
            symbol="alpha_W",
            value=0.0337,
            unit="dimensionless",
            uncertainty=0.01,
            description="Weak force coupling at low energy",
            domain=PhysicsDomain.PARTICLE_PHYSICS
        ))
        
        self._add(PhysicalConstant(
            name="Strong coupling constant",
            symbol="alpha_s",
            value=0.1179,
            unit="dimensionless",
            uncertainty=0.01,
            description="QCD coupling constant at M_Z scale",
            domain=PhysicsDomain.PARTICLE_PHYSICS
        ))
        
        # ============================================================
        # QUANTUM/ATOMIC CONSTANTS
        # ============================================================
        
        self._add(PhysicalConstant(
            name="Bohr radius",
            symbol="a_0",
            value=5.29177210903e-11,
            unit="m",
            uncertainty=1.5e-10,
            description="Characteristic size of hydrogen atom",
            domain=PhysicsDomain.QUANTUM_MECHANICS
        ))
        
        self._add(PhysicalConstant(
            name="Classical electron radius",
            symbol="r_e",
            value=2.8179403262e-15,
            unit="m",
            uncertainty=1.5e-10,
            description="e^2/(4*pi*epsilon_0*m_e*c^2)",
            domain=PhysicsDomain.QUANTUM_MECHANICS
        ))
        
        self._add(PhysicalConstant(
            name="Compton wavelength (electron)",
            symbol="lambda_C",
            value=2.42631023867e-12,
            unit="m",
            uncertainty=3.0e-10,
            description="h/(m_e*c), quantum scale of electron",
            domain=PhysicsDomain.QUANTUM_MECHANICS
        ))
        
        self._add(PhysicalConstant(
            name="Rydberg constant",
            symbol="R_inf",
            value=10973731.568160,
            unit="1/m",
            uncertainty=1.9e-12,
            description="Hydrogen spectral line constant",
            domain=PhysicsDomain.QUANTUM_MECHANICS
        ))
        
        self._add(PhysicalConstant(
            name="Bohr magneton",
            symbol="mu_B",
            value=9.2740100783e-24,
            unit="J/T",
            uncertainty=3.0e-10,
            description="e*hbar/(2*m_e), magnetic moment unit",
            domain=PhysicsDomain.QUANTUM_MECHANICS
        ))
        
        self._add(PhysicalConstant(
            name="Nuclear magneton",
            symbol="mu_N",
            value=5.0507837461e-27,
            unit="J/T",
            uncertainty=3.1e-10,
            description="e*hbar/(2*m_p), nuclear magnetic moment unit",
            domain=PhysicsDomain.NUCLEAR_PHYSICS
        ))
        
        # ============================================================
        # THERMODYNAMIC CONSTANTS
        # ============================================================
        
        self._add(PhysicalConstant(
            name="Gas constant",
            symbol="R",
            value=8.314462618,
            unit="J/(mol*K)",
            uncertainty=0,
            description="N_A * k_B, ideal gas constant",
            domain=PhysicsDomain.THERMODYNAMICS,
            is_exact=True
        ))
        
        self._add(PhysicalConstant(
            name="Stefan-Boltzmann constant",
            symbol="sigma",
            value=5.670374419e-8,
            unit="W/(m^2*K^4)",
            uncertainty=0,
            description="Black body radiation constant",
            domain=PhysicsDomain.THERMODYNAMICS,
            is_exact=True
        ))
        
        self._add(PhysicalConstant(
            name="Wien displacement constant",
            symbol="b",
            value=2.897771955e-3,
            unit="m*K",
            uncertainty=0,
            description="lambda_max * T = b",
            domain=PhysicsDomain.THERMODYNAMICS,
            is_exact=True
        ))
        
        # ============================================================
        # COSMOLOGICAL CONSTANTS
        # ============================================================
        
        self._add(PhysicalConstant(
            name="Hubble constant",
            symbol="H_0",
            value=67.4e3,  # (m/s)/Mpc converted
            unit="(m/s)/Mpc",
            uncertainty=0.01,
            description="Current expansion rate of universe",
            domain=PhysicsDomain.COSMOLOGY
        ))
        
        self._add(PhysicalConstant(
            name="Cosmological constant",
            symbol="Lambda",
            value=1.1056e-52,
            unit="1/m^2",
            uncertainty=0.02,
            description="Dark energy density parameter",
            domain=PhysicsDomain.COSMOLOGY
        ))
        
        self._add(PhysicalConstant(
            name="Planck length",
            symbol="l_P",
            value=1.616255e-35,
            unit="m",
            uncertainty=1.1e-5,
            description="sqrt(hbar*G/c^3), quantum gravity scale",
            domain=PhysicsDomain.QUANTUM_MECHANICS
        ))
        
        self._add(PhysicalConstant(
            name="Planck mass",
            symbol="m_P",
            value=2.176434e-8,
            unit="kg",
            uncertainty=1.1e-5,
            description="sqrt(hbar*c/G), quantum gravity mass scale",
            domain=PhysicsDomain.QUANTUM_MECHANICS
        ))
        
        self._add(PhysicalConstant(
            name="Planck time",
            symbol="t_P",
            value=5.391247e-44,
            unit="s",
            uncertainty=1.1e-5,
            description="sqrt(hbar*G/c^5), quantum gravity time scale",
            domain=PhysicsDomain.QUANTUM_MECHANICS
        ))
        
        self._add(PhysicalConstant(
            name="Planck temperature",
            symbol="T_P",
            value=1.416784e32,
            unit="K",
            uncertainty=1.1e-5,
            description="sqrt(hbar*c^5/(G*k_B^2)), max temperature scale",
            domain=PhysicsDomain.QUANTUM_MECHANICS
        ))
    
    def _add(self, constant: PhysicalConstant):
        """Add a constant to the database."""
        self.constants[constant.symbol] = constant
    
    def get(self, symbol: str) -> Optional[PhysicalConstant]:
        """Get constant by symbol."""
        return self.constants.get(symbol)
    
    def get_value(self, symbol: str) -> Optional[float]:
        """Get just the numerical value."""
        const = self.constants.get(symbol)
        return const.value if const else None
    
    def list_all(self) -> Dict[str, PhysicalConstant]:
        """Get all constants."""
        return self.constants.copy()
    
    def list_by_domain(self, domain: PhysicsDomain) -> Dict[str, PhysicalConstant]:
        """Get constants filtered by domain."""
        return {k: v for k, v in self.constants.items() if v.domain == domain}
    
    def search(self, query: str) -> Dict[str, PhysicalConstant]:
        """Search constants by name or description."""
        query = query.lower()
        return {
            k: v for k, v in self.constants.items()
            if query in v.name.lower() or query in v.description.lower()
        }


class PhysicsEquationsDatabase:
    """
    Complete database of proven physics equations.
    
    Organized by domain with derivation relationships.
    """
    
    def __init__(self):
        self.equations: Dict[str, PhysicsEquation] = {}
        self._initialize_equations()
    
    def _add(self, eq: PhysicsEquation):
        """Add equation to database."""
        self.equations[eq.name] = eq
    
    def _initialize_equations(self):
        """Initialize all physics equations from first principles."""
        
        # ============================================================
        # CLASSICAL MECHANICS - Newton's Laws (Fundamental)
        # ============================================================
        
        self._add(PhysicsEquation(
            name="Newton's First Law",
            equation="F_net = 0 implies dv/dt = 0",
            latex=r"\sum \vec{F} = 0 \Rightarrow \frac{d\vec{v}}{dt} = 0",
            description="An object remains at rest or in uniform motion unless acted upon by a net force",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            status=EquationStatus.FUNDAMENTAL,
            variables={"F_net": "Net force", "v": "Velocity", "t": "Time"},
            leads_to=["Momentum Conservation"],
            conditions=["Inertial reference frame"],
            discoverer="Isaac Newton",
            year_discovered=1687
        ))
        
        self._add(PhysicsEquation(
            name="Newton's Second Law",
            equation="F = m * a",
            latex=r"\vec{F} = m\vec{a} = m\frac{d\vec{v}}{dt} = \frac{d\vec{p}}{dt}",
            description="Force equals mass times acceleration, or rate of change of momentum",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            status=EquationStatus.FUNDAMENTAL,
            variables={"F": "Force (N)", "m": "Mass (kg)", "a": "Acceleration (m/s^2)"},
            leads_to=["Kinetic Energy", "Work-Energy Theorem", "Impulse-Momentum"],
            conditions=["Non-relativistic speeds (v << c)", "Constant mass"],
            discoverer="Isaac Newton",
            year_discovered=1687
        ))
        
        self._add(PhysicsEquation(
            name="Newton's Third Law",
            equation="F_12 = -F_21",
            latex=r"\vec{F}_{12} = -\vec{F}_{21}",
            description="Every action has an equal and opposite reaction",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            status=EquationStatus.FUNDAMENTAL,
            variables={"F_12": "Force on 1 by 2", "F_21": "Force on 2 by 1"},
            leads_to=["Momentum Conservation"],
            conditions=["Instantaneous interaction (non-relativistic)"],
            discoverer="Isaac Newton",
            year_discovered=1687
        ))
        
        self._add(PhysicsEquation(
            name="Newton's Law of Gravitation",
            equation="F = G * m1 * m2 / r**2",
            latex=r"F = \frac{Gm_1m_2}{r^2}",
            description="Gravitational force between two masses",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            status=EquationStatus.EMPIRICAL,
            variables={"F": "Force (N)", "G": "Gravitational constant", "m1": "Mass 1", "m2": "Mass 2", "r": "Distance"},
            leads_to=["Gravitational Potential Energy", "Orbital Mechanics", "Kepler's Laws"],
            conditions=["Point masses or spherically symmetric", "Non-relativistic"],
            discoverer="Isaac Newton",
            year_discovered=1687
        ))
        
        # ============================================================
        # CLASSICAL MECHANICS - Derived Equations
        # ============================================================
        
        self._add(PhysicsEquation(
            name="Momentum",
            equation="p = m * v",
            latex=r"\vec{p} = m\vec{v}",
            description="Linear momentum of a particle",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"p": "Momentum (kg*m/s)", "m": "Mass (kg)", "v": "Velocity (m/s)"},
            derived_from=["Newton's Second Law"],
            leads_to=["Momentum Conservation", "Impulse-Momentum"],
            first_principle_derivation="From F=ma: F=d(mv)/dt, so p=mv is the conserved quantity"
        ))
        
        self._add(PhysicsEquation(
            name="Momentum Conservation",
            equation="p_initial = p_final",
            latex=r"\sum \vec{p}_i = \sum \vec{p}_f",
            description="Total momentum is conserved in isolated systems",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"p": "Momentum"},
            derived_from=["Newton's Second Law", "Newton's Third Law"],
            conditions=["No external forces"],
            first_principle_derivation="From Newton's Third Law: F_12=-F_21, so dp_1/dt=-dp_2/dt, thus d(p_1+p_2)/dt=0"
        ))
        
        self._add(PhysicsEquation(
            name="Kinetic Energy",
            equation="E_k = (1/2) * m * v**2",
            latex=r"E_k = \frac{1}{2}mv^2",
            description="Energy of motion",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"E_k": "Kinetic energy (J)", "m": "Mass (kg)", "v": "Speed (m/s)"},
            derived_from=["Work-Energy Theorem"],
            leads_to=["Energy Conservation"],
            first_principle_derivation="W = integral(F*dx) = integral(m*a*dx) = integral(m*v*dv) = (1/2)mv^2"
        ))
        
        self._add(PhysicsEquation(
            name="Gravitational Potential Energy",
            equation="E_p = m * g * h",
            latex=r"E_p = mgh",
            description="Potential energy near Earth's surface",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"E_p": "Potential energy (J)", "m": "Mass (kg)", "g": "Gravity (m/s^2)", "h": "Height (m)"},
            derived_from=["Newton's Law of Gravitation"],
            leads_to=["Energy Conservation"],
            conditions=["Near Earth surface (h << R_Earth)"],
            first_principle_derivation="E_p = -integral(F*dr) = -integral(-mg*dr) = mgh"
        ))
        
        self._add(PhysicsEquation(
            name="General Gravitational Potential Energy",
            equation="U = -G * M * m / r",
            latex=r"U = -\frac{GMm}{r}",
            description="Gravitational potential energy between two masses",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"U": "Potential energy (J)", "G": "Gravitational constant", "M": "Mass 1", "m": "Mass 2", "r": "Distance"},
            derived_from=["Newton's Law of Gravitation"],
            first_principle_derivation="U = -integral(F*dr) from infinity to r"
        ))
        
        self._add(PhysicsEquation(
            name="Work-Energy Theorem",
            equation="W = Delta_E_k",
            latex=r"W = \Delta E_k = E_{k,f} - E_{k,i}",
            description="Work done equals change in kinetic energy",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"W": "Work (J)", "E_k": "Kinetic energy (J)"},
            derived_from=["Newton's Second Law"],
            first_principle_derivation="W = integral(F*dx) = integral(m*dv/dt*dx) = integral(m*v*dv) = Delta(mv^2/2)"
        ))
        
        self._add(PhysicsEquation(
            name="Work",
            equation="W = F * d * cos(theta)",
            latex=r"W = \vec{F} \cdot \vec{d} = Fd\cos\theta",
            description="Work done by a force over a displacement",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"W": "Work (J)", "F": "Force (N)", "d": "Displacement (m)", "theta": "Angle"},
            conditions=["Constant force"]
        ))
        
        self._add(PhysicsEquation(
            name="Power",
            equation="P = W / t = F * v",
            latex=r"P = \frac{W}{t} = \vec{F} \cdot \vec{v}",
            description="Rate of doing work",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"P": "Power (W)", "W": "Work (J)", "t": "Time (s)", "F": "Force (N)", "v": "Velocity (m/s)"}
        ))
        
        self._add(PhysicsEquation(
            name="Impulse-Momentum Theorem",
            equation="J = F * Delta_t = Delta_p",
            latex=r"\vec{J} = \vec{F}\Delta t = \Delta \vec{p}",
            description="Impulse equals change in momentum",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"J": "Impulse (N*s)", "F": "Force (N)", "t": "Time (s)", "p": "Momentum (kg*m/s)"},
            derived_from=["Newton's Second Law"],
            first_principle_derivation="From F=dp/dt, integrate: integral(F*dt) = Delta_p"
        ))
        
        self._add(PhysicsEquation(
            name="Angular Momentum",
            equation="L = r * p * sin(theta) = I * omega",
            latex=r"\vec{L} = \vec{r} \times \vec{p} = I\vec{\omega}",
            description="Rotational analog of linear momentum",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"L": "Angular momentum (kg*m^2/s)", "r": "Position (m)", "p": "Momentum", "I": "Moment of inertia", "omega": "Angular velocity"}
        ))
        
        self._add(PhysicsEquation(
            name="Torque",
            equation="tau = r * F * sin(theta) = I * alpha",
            latex=r"\vec{\tau} = \vec{r} \times \vec{F} = I\vec{\alpha}",
            description="Rotational analog of force",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"tau": "Torque (N*m)", "r": "Position (m)", "F": "Force (N)", "I": "Moment of inertia", "alpha": "Angular acceleration"}
        ))
        
        self._add(PhysicsEquation(
            name="Rotational Kinetic Energy",
            equation="E_rot = (1/2) * I * omega**2",
            latex=r"E_{rot} = \frac{1}{2}I\omega^2",
            description="Kinetic energy of rotation",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"E_rot": "Rotational energy (J)", "I": "Moment of inertia (kg*m^2)", "omega": "Angular velocity (rad/s)"}
        ))
        
        self._add(PhysicsEquation(
            name="Centripetal Acceleration",
            equation="a_c = v**2 / r = omega**2 * r",
            latex=r"a_c = \frac{v^2}{r} = \omega^2 r",
            description="Acceleration toward center of circular motion",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"a_c": "Centripetal acceleration", "v": "Speed", "r": "Radius", "omega": "Angular velocity"}
        ))
        
        self._add(PhysicsEquation(
            name="Hooke's Law",
            equation="F = -k * x",
            latex=r"F = -kx",
            description="Restoring force of a spring",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            status=EquationStatus.EMPIRICAL,
            variables={"F": "Force (N)", "k": "Spring constant (N/m)", "x": "Displacement (m)"},
            leads_to=["Simple Harmonic Motion", "Elastic Potential Energy"],
            conditions=["Within elastic limit"]
        ))
        
        self._add(PhysicsEquation(
            name="Elastic Potential Energy",
            equation="E_s = (1/2) * k * x**2",
            latex=r"E_s = \frac{1}{2}kx^2",
            description="Energy stored in a spring",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"E_s": "Elastic energy (J)", "k": "Spring constant (N/m)", "x": "Displacement (m)"},
            derived_from=["Hooke's Law"]
        ))
        
        self._add(PhysicsEquation(
            name="Simple Harmonic Motion",
            equation="x(t) = A * cos(omega * t + phi)",
            latex=r"x(t) = A\cos(\omega t + \phi)",
            description="Position as function of time for SHM",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"x": "Position", "A": "Amplitude", "omega": "Angular frequency", "t": "Time", "phi": "Phase"},
            derived_from=["Hooke's Law", "Newton's Second Law"]
        ))
        
        self._add(PhysicsEquation(
            name="SHM Angular Frequency",
            equation="omega = sqrt(k / m)",
            latex=r"\omega = \sqrt{\frac{k}{m}}",
            description="Angular frequency of mass-spring system",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"omega": "Angular frequency (rad/s)", "k": "Spring constant (N/m)", "m": "Mass (kg)"},
            derived_from=["Hooke's Law", "Newton's Second Law"]
        ))
        
        self._add(PhysicsEquation(
            name="Pendulum Period",
            equation="T = 2 * pi * sqrt(L / g)",
            latex=r"T = 2\pi\sqrt{\frac{L}{g}}",
            description="Period of simple pendulum (small angles)",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"T": "Period (s)", "L": "Length (m)", "g": "Gravity (m/s^2)"},
            conditions=["Small angle approximation (sin(theta) ~ theta)"]
        ))
        
        # ============================================================
        # CLASSICAL MECHANICS - Lagrangian & Hamiltonian
        # ============================================================
        
        self._add(PhysicsEquation(
            name="Lagrangian",
            equation="L = T - V",
            latex=r"L = T - V",
            description="Lagrangian function: kinetic minus potential energy",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            status=EquationStatus.FUNDAMENTAL,
            variables={"L": "Lagrangian", "T": "Kinetic energy", "V": "Potential energy"},
            leads_to=["Euler-Lagrange Equation", "Principle of Least Action"]
        ))
        
        self._add(PhysicsEquation(
            name="Euler-Lagrange Equation",
            equation="d/dt(dL/d(q_dot)) - dL/dq = 0",
            latex=r"\frac{d}{dt}\frac{\partial L}{\partial \dot{q}} - \frac{\partial L}{\partial q} = 0",
            description="Equations of motion from variational principle",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"L": "Lagrangian", "q": "Generalized coordinate", "q_dot": "Generalized velocity"},
            derived_from=["Principle of Least Action"]
        ))
        
        self._add(PhysicsEquation(
            name="Hamiltonian",
            equation="H = sum(p_i * q_dot_i) - L = T + V",
            latex=r"H = \sum_i p_i \dot{q}_i - L = T + V",
            description="Hamiltonian function: total energy",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"H": "Hamiltonian", "p": "Generalized momentum", "q_dot": "Generalized velocity", "L": "Lagrangian"},
            derived_from=["Lagrangian"],
            leads_to=["Hamilton's Equations"]
        ))
        
        self._add(PhysicsEquation(
            name="Hamilton's Equations",
            equation="dq/dt = dH/dp, dp/dt = -dH/dq",
            latex=r"\dot{q} = \frac{\partial H}{\partial p}, \quad \dot{p} = -\frac{\partial H}{\partial q}",
            description="Equations of motion in Hamiltonian formalism",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"q": "Generalized coordinate", "p": "Generalized momentum", "H": "Hamiltonian"},
            derived_from=["Hamiltonian"]
        ))
        
        # ============================================================
        # ELECTROMAGNETISM - Maxwell's Equations
        # ============================================================
        
        self._add(PhysicsEquation(
            name="Gauss's Law (Electric)",
            equation="div(E) = rho / epsilon_0",
            latex=r"\nabla \cdot \vec{E} = \frac{\rho}{\epsilon_0}",
            description="Electric field divergence equals charge density",
            domain=PhysicsDomain.ELECTROMAGNETISM,
            status=EquationStatus.FUNDAMENTAL,
            variables={"E": "Electric field (V/m)", "rho": "Charge density (C/m^3)", "epsilon_0": "Permittivity"},
            leads_to=["Coulomb's Law"],
            discoverer="Carl Friedrich Gauss",
            year_discovered=1835
        ))
        
        self._add(PhysicsEquation(
            name="Gauss's Law (Magnetic)",
            equation="div(B) = 0",
            latex=r"\nabla \cdot \vec{B} = 0",
            description="No magnetic monopoles",
            domain=PhysicsDomain.ELECTROMAGNETISM,
            status=EquationStatus.FUNDAMENTAL,
            variables={"B": "Magnetic field (T)"},
            discoverer="Carl Friedrich Gauss"
        ))
        
        self._add(PhysicsEquation(
            name="Faraday's Law",
            equation="curl(E) = -dB/dt",
            latex=r"\nabla \times \vec{E} = -\frac{\partial \vec{B}}{\partial t}",
            description="Changing magnetic field induces electric field",
            domain=PhysicsDomain.ELECTROMAGNETISM,
            status=EquationStatus.FUNDAMENTAL,
            variables={"E": "Electric field", "B": "Magnetic field", "t": "Time"},
            leads_to=["Electromagnetic Induction", "Lenz's Law"],
            discoverer="Michael Faraday",
            year_discovered=1831
        ))
        
        self._add(PhysicsEquation(
            name="Ampere-Maxwell Law",
            equation="curl(B) = mu_0 * (J + epsilon_0 * dE/dt)",
            latex=r"\nabla \times \vec{B} = \mu_0\left(\vec{J} + \epsilon_0\frac{\partial \vec{E}}{\partial t}\right)",
            description="Currents and changing electric fields create magnetic fields",
            domain=PhysicsDomain.ELECTROMAGNETISM,
            status=EquationStatus.FUNDAMENTAL,
            variables={"B": "Magnetic field", "J": "Current density", "E": "Electric field", "mu_0": "Permeability", "epsilon_0": "Permittivity"},
            leads_to=["Electromagnetic Waves"],
            discoverer="James Clerk Maxwell",
            year_discovered=1865
        ))
        
        self._add(PhysicsEquation(
            name="Coulomb's Law",
            equation="F = k_e * q1 * q2 / r**2",
            latex=r"F = \frac{1}{4\pi\epsilon_0}\frac{q_1 q_2}{r^2}",
            description="Electrostatic force between two charges",
            domain=PhysicsDomain.ELECTROMAGNETISM,
            status=EquationStatus.PROVEN,
            variables={"F": "Force (N)", "k_e": "Coulomb constant", "q1": "Charge 1 (C)", "q2": "Charge 2 (C)", "r": "Distance (m)"},
            derived_from=["Gauss's Law (Electric)"],
            discoverer="Charles-Augustin de Coulomb",
            year_discovered=1785
        ))
        
        self._add(PhysicsEquation(
            name="Lorentz Force",
            equation="F = q * (E + v cross B)",
            latex=r"\vec{F} = q(\vec{E} + \vec{v} \times \vec{B})",
            description="Force on a charged particle in EM fields",
            domain=PhysicsDomain.ELECTROMAGNETISM,
            status=EquationStatus.FUNDAMENTAL,
            variables={"F": "Force (N)", "q": "Charge (C)", "E": "Electric field (V/m)", "v": "Velocity (m/s)", "B": "Magnetic field (T)"}
        ))
        
        self._add(PhysicsEquation(
            name="Electric Potential Energy",
            equation="U = k_e * q1 * q2 / r",
            latex=r"U = \frac{1}{4\pi\epsilon_0}\frac{q_1 q_2}{r}",
            description="Potential energy between two charges",
            domain=PhysicsDomain.ELECTROMAGNETISM,
            status=EquationStatus.PROVEN,
            variables={"U": "Potential energy (J)", "q1": "Charge 1", "q2": "Charge 2", "r": "Distance"},
            derived_from=["Coulomb's Law"]
        ))
        
        self._add(PhysicsEquation(
            name="Electric Field from Potential",
            equation="E = -grad(V)",
            latex=r"\vec{E} = -\nabla V",
            description="Electric field is negative gradient of potential",
            domain=PhysicsDomain.ELECTROMAGNETISM,
            status=EquationStatus.PROVEN,
            variables={"E": "Electric field", "V": "Electric potential"}
        ))
        
        self._add(PhysicsEquation(
            name="Capacitance",
            equation="C = Q / V",
            latex=r"C = \frac{Q}{V}",
            description="Capacitance defined as charge per voltage",
            domain=PhysicsDomain.ELECTROMAGNETISM,
            status=EquationStatus.PROVEN,
            variables={"C": "Capacitance (F)", "Q": "Charge (C)", "V": "Voltage (V)"}
        ))
        
        self._add(PhysicsEquation(
            name="Parallel Plate Capacitor",
            equation="C = epsilon_0 * A / d",
            latex=r"C = \frac{\epsilon_0 A}{d}",
            description="Capacitance of parallel plate capacitor",
            domain=PhysicsDomain.ELECTROMAGNETISM,
            status=EquationStatus.PROVEN,
            variables={"C": "Capacitance", "epsilon_0": "Permittivity", "A": "Plate area", "d": "Separation"}
        ))
        
        self._add(PhysicsEquation(
            name="Ohm's Law",
            equation="V = I * R",
            latex=r"V = IR",
            description="Voltage equals current times resistance",
            domain=PhysicsDomain.ELECTROMAGNETISM,
            status=EquationStatus.EMPIRICAL,
            variables={"V": "Voltage (V)", "I": "Current (A)", "R": "Resistance (Ohm)"},
            conditions=["Ohmic materials", "Constant temperature"],
            discoverer="Georg Ohm",
            year_discovered=1827
        ))
        
        self._add(PhysicsEquation(
            name="Electrical Power",
            equation="P = I * V = I**2 * R = V**2 / R",
            latex=r"P = IV = I^2R = \frac{V^2}{R}",
            description="Power dissipated in a resistor",
            domain=PhysicsDomain.ELECTROMAGNETISM,
            status=EquationStatus.PROVEN,
            variables={"P": "Power (W)", "I": "Current (A)", "V": "Voltage (V)", "R": "Resistance (Ohm)"}
        ))
        
        self._add(PhysicsEquation(
            name="Biot-Savart Law",
            equation="dB = (mu_0 / 4*pi) * (I * dl cross r_hat) / r**2",
            latex=r"d\vec{B} = \frac{\mu_0}{4\pi}\frac{I\,d\vec{l} \times \hat{r}}{r^2}",
            description="Magnetic field from a current element",
            domain=PhysicsDomain.ELECTROMAGNETISM,
            status=EquationStatus.PROVEN,
            variables={"B": "Magnetic field", "I": "Current", "dl": "Length element", "r": "Distance"}
        ))
        
        self._add(PhysicsEquation(
            name="Electromagnetic Wave Speed",
            equation="c = 1 / sqrt(epsilon_0 * mu_0)",
            latex=r"c = \frac{1}{\sqrt{\epsilon_0 \mu_0}}",
            description="Speed of light from Maxwell's equations",
            domain=PhysicsDomain.ELECTROMAGNETISM,
            status=EquationStatus.PROVEN,
            variables={"c": "Speed of light", "epsilon_0": "Permittivity", "mu_0": "Permeability"},
            derived_from=["Ampere-Maxwell Law", "Faraday's Law"]
        ))
        
        self._add(PhysicsEquation(
            name="Poynting Vector",
            equation="S = (1/mu_0) * E cross B",
            latex=r"\vec{S} = \frac{1}{\mu_0}\vec{E} \times \vec{B}",
            description="Energy flux of electromagnetic wave",
            domain=PhysicsDomain.ELECTROMAGNETISM,
            status=EquationStatus.PROVEN,
            variables={"S": "Poynting vector (W/m^2)", "E": "Electric field", "B": "Magnetic field"}
        ))
        
        # ============================================================
        # THERMODYNAMICS
        # ============================================================
        
        self._add(PhysicsEquation(
            name="Zeroth Law of Thermodynamics",
            equation="T_A = T_B and T_B = T_C implies T_A = T_C",
            latex=r"T_A = T_B \land T_B = T_C \Rightarrow T_A = T_C",
            description="Thermal equilibrium is transitive",
            domain=PhysicsDomain.THERMODYNAMICS,
            status=EquationStatus.FUNDAMENTAL,
            variables={"T": "Temperature"}
        ))
        
        self._add(PhysicsEquation(
            name="First Law of Thermodynamics",
            equation="dU = delta_Q - delta_W",
            latex=r"dU = \delta Q - \delta W",
            description="Energy conservation with heat and work",
            domain=PhysicsDomain.THERMODYNAMICS,
            status=EquationStatus.FUNDAMENTAL,
            variables={"U": "Internal energy (J)", "Q": "Heat (J)", "W": "Work (J)"},
            leads_to=["Enthalpy", "Heat Capacities"]
        ))
        
        self._add(PhysicsEquation(
            name="Second Law of Thermodynamics (Clausius)",
            equation="dS >= delta_Q / T",
            latex=r"dS \geq \frac{\delta Q}{T}",
            description="Entropy increases in isolated systems",
            domain=PhysicsDomain.THERMODYNAMICS,
            status=EquationStatus.FUNDAMENTAL,
            variables={"S": "Entropy (J/K)", "Q": "Heat (J)", "T": "Temperature (K)"},
            leads_to=["Carnot Efficiency"]
        ))
        
        self._add(PhysicsEquation(
            name="Third Law of Thermodynamics",
            equation="lim(T->0) S = 0",
            latex=r"\lim_{T \to 0} S = 0",
            description="Entropy approaches zero at absolute zero",
            domain=PhysicsDomain.THERMODYNAMICS,
            status=EquationStatus.FUNDAMENTAL,
            variables={"S": "Entropy", "T": "Temperature"}
        ))
        
        self._add(PhysicsEquation(
            name="Ideal Gas Law",
            equation="P * V = n * R * T = N * k_B * T",
            latex=r"PV = nRT = Nk_BT",
            description="Equation of state for ideal gas",
            domain=PhysicsDomain.THERMODYNAMICS,
            status=EquationStatus.EMPIRICAL,
            variables={"P": "Pressure (Pa)", "V": "Volume (m^3)", "n": "Moles", "R": "Gas constant", "T": "Temperature (K)", "N": "Number of particles", "k_B": "Boltzmann constant"}
        ))
        
        self._add(PhysicsEquation(
            name="Entropy (Statistical)",
            equation="S = k_B * ln(Omega)",
            latex=r"S = k_B \ln \Omega",
            description="Entropy from microstate counting",
            domain=PhysicsDomain.STATISTICAL_MECHANICS,
            status=EquationStatus.FUNDAMENTAL,
            variables={"S": "Entropy (J/K)", "k_B": "Boltzmann constant", "Omega": "Number of microstates"},
            discoverer="Ludwig Boltzmann",
            year_discovered=1877
        ))
        
        self._add(PhysicsEquation(
            name="Helmholtz Free Energy",
            equation="F = U - T * S",
            latex=r"F = U - TS",
            description="Thermodynamic potential at constant T, V",
            domain=PhysicsDomain.THERMODYNAMICS,
            status=EquationStatus.PROVEN,
            variables={"F": "Helmholtz energy (J)", "U": "Internal energy", "T": "Temperature", "S": "Entropy"}
        ))
        
        self._add(PhysicsEquation(
            name="Gibbs Free Energy",
            equation="G = H - T * S = U + P*V - T*S",
            latex=r"G = H - TS = U + PV - TS",
            description="Thermodynamic potential at constant T, P",
            domain=PhysicsDomain.THERMODYNAMICS,
            status=EquationStatus.PROVEN,
            variables={"G": "Gibbs energy (J)", "H": "Enthalpy", "T": "Temperature", "S": "Entropy"}
        ))
        
        self._add(PhysicsEquation(
            name="Enthalpy",
            equation="H = U + P * V",
            latex=r"H = U + PV",
            description="Total heat content",
            domain=PhysicsDomain.THERMODYNAMICS,
            status=EquationStatus.PROVEN,
            variables={"H": "Enthalpy (J)", "U": "Internal energy", "P": "Pressure", "V": "Volume"}
        ))
        
        self._add(PhysicsEquation(
            name="Heat Capacity (Constant Volume)",
            equation="C_V = dU/dT at constant V",
            latex=r"C_V = \left(\frac{\partial U}{\partial T}\right)_V",
            description="Heat capacity at constant volume",
            domain=PhysicsDomain.THERMODYNAMICS,
            status=EquationStatus.PROVEN,
            variables={"C_V": "Heat capacity (J/K)", "U": "Internal energy", "T": "Temperature"}
        ))
        
        self._add(PhysicsEquation(
            name="Heat Capacity (Constant Pressure)",
            equation="C_P = dH/dT at constant P",
            latex=r"C_P = \left(\frac{\partial H}{\partial T}\right)_P",
            description="Heat capacity at constant pressure",
            domain=PhysicsDomain.THERMODYNAMICS,
            status=EquationStatus.PROVEN,
            variables={"C_P": "Heat capacity (J/K)", "H": "Enthalpy", "T": "Temperature"}
        ))
        
        self._add(PhysicsEquation(
            name="Carnot Efficiency",
            equation="eta = 1 - T_cold / T_hot",
            latex=r"\eta = 1 - \frac{T_c}{T_h}",
            description="Maximum efficiency of heat engine",
            domain=PhysicsDomain.THERMODYNAMICS,
            status=EquationStatus.PROVEN,
            variables={"eta": "Efficiency", "T_cold": "Cold reservoir temp", "T_hot": "Hot reservoir temp"},
            derived_from=["Second Law of Thermodynamics (Clausius)"]
        ))
        
        self._add(PhysicsEquation(
            name="Stefan-Boltzmann Law",
            equation="P = sigma * A * T**4",
            latex=r"P = \sigma A T^4",
            description="Power radiated by black body",
            domain=PhysicsDomain.THERMODYNAMICS,
            status=EquationStatus.PROVEN,
            variables={"P": "Power (W)", "sigma": "Stefan-Boltzmann constant", "A": "Area (m^2)", "T": "Temperature (K)"},
            discoverer="Josef Stefan",
            year_discovered=1879
        ))
        
        self._add(PhysicsEquation(
            name="Wien's Displacement Law",
            equation="lambda_max * T = b",
            latex=r"\lambda_{max} T = b",
            description="Peak wavelength of black body radiation",
            domain=PhysicsDomain.THERMODYNAMICS,
            status=EquationStatus.PROVEN,
            variables={"lambda_max": "Peak wavelength (m)", "T": "Temperature (K)", "b": "Wien constant"},
            discoverer="Wilhelm Wien",
            year_discovered=1893
        ))
        
        self._add(PhysicsEquation(
            name="Planck's Law",
            equation="B(nu, T) = (2*h*nu**3/c**2) / (exp(h*nu/(k_B*T)) - 1)",
            latex=r"B(\nu, T) = \frac{2h\nu^3}{c^2}\frac{1}{e^{h\nu/k_BT} - 1}",
            description="Spectral radiance of black body",
            domain=PhysicsDomain.QUANTUM_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"B": "Spectral radiance", "nu": "Frequency", "T": "Temperature", "h": "Planck constant", "c": "Speed of light", "k_B": "Boltzmann constant"},
            discoverer="Max Planck",
            year_discovered=1900
        ))
        
        # ============================================================
        # STATISTICAL MECHANICS
        # ============================================================
        
        self._add(PhysicsEquation(
            name="Boltzmann Distribution",
            equation="P(E) = (1/Z) * exp(-E / (k_B * T))",
            latex=r"P(E) = \frac{1}{Z}e^{-E/k_BT}",
            description="Probability of state with energy E",
            domain=PhysicsDomain.STATISTICAL_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"P": "Probability", "E": "Energy", "Z": "Partition function", "k_B": "Boltzmann constant", "T": "Temperature"}
        ))
        
        self._add(PhysicsEquation(
            name="Partition Function",
            equation="Z = sum(exp(-E_i / (k_B * T)))",
            latex=r"Z = \sum_i e^{-E_i/k_BT}",
            description="Normalization for Boltzmann distribution",
            domain=PhysicsDomain.STATISTICAL_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"Z": "Partition function", "E_i": "Energy of state i", "k_B": "Boltzmann constant", "T": "Temperature"}
        ))
        
        self._add(PhysicsEquation(
            name="Free Energy from Partition Function",
            equation="F = -k_B * T * ln(Z)",
            latex=r"F = -k_BT\ln Z",
            description="Helmholtz energy from partition function",
            domain=PhysicsDomain.STATISTICAL_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"F": "Helmholtz energy", "k_B": "Boltzmann constant", "T": "Temperature", "Z": "Partition function"}
        ))
        
        self._add(PhysicsEquation(
            name="Fermi-Dirac Distribution",
            equation="f(E) = 1 / (exp((E - mu) / (k_B * T)) + 1)",
            latex=r"f(E) = \frac{1}{e^{(E-\mu)/k_BT} + 1}",
            description="Distribution function for fermions",
            domain=PhysicsDomain.STATISTICAL_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"f": "Occupation probability", "E": "Energy", "mu": "Chemical potential", "k_B": "Boltzmann constant", "T": "Temperature"}
        ))
        
        self._add(PhysicsEquation(
            name="Bose-Einstein Distribution",
            equation="n(E) = 1 / (exp((E - mu) / (k_B * T)) - 1)",
            latex=r"n(E) = \frac{1}{e^{(E-\mu)/k_BT} - 1}",
            description="Distribution function for bosons",
            domain=PhysicsDomain.STATISTICAL_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"n": "Occupation number", "E": "Energy", "mu": "Chemical potential", "k_B": "Boltzmann constant", "T": "Temperature"}
        ))
        
        self._add(PhysicsEquation(
            name="Maxwell-Boltzmann Speed Distribution",
            equation="f(v) = 4*pi*n*(m/(2*pi*k_B*T))**(3/2) * v**2 * exp(-m*v**2/(2*k_B*T))",
            latex=r"f(v) = 4\pi n \left(\frac{m}{2\pi k_BT}\right)^{3/2} v^2 e^{-mv^2/2k_BT}",
            description="Speed distribution in ideal gas",
            domain=PhysicsDomain.STATISTICAL_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"f": "Distribution function", "v": "Speed", "m": "Mass", "k_B": "Boltzmann constant", "T": "Temperature", "n": "Number density"}
        ))
        
        self._add(PhysicsEquation(
            name="Equipartition Theorem",
            equation="<E> = (1/2) * f * k_B * T",
            latex=r"\langle E \rangle = \frac{1}{2}fk_BT",
            description="Average energy per quadratic degree of freedom",
            domain=PhysicsDomain.STATISTICAL_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"E": "Energy", "f": "Degrees of freedom", "k_B": "Boltzmann constant", "T": "Temperature"}
        ))
        
        # ============================================================
        # QUANTUM MECHANICS
        # ============================================================
        
        self._add(PhysicsEquation(
            name="Planck-Einstein Relation",
            equation="E = h * nu = hbar * omega",
            latex=r"E = h\nu = \hbar\omega",
            description="Energy of a photon",
            domain=PhysicsDomain.QUANTUM_MECHANICS,
            status=EquationStatus.FUNDAMENTAL,
            variables={"E": "Energy (J)", "h": "Planck constant", "nu": "Frequency (Hz)", "hbar": "Reduced Planck constant", "omega": "Angular frequency"},
            discoverer="Max Planck / Albert Einstein",
            year_discovered=1905
        ))
        
        self._add(PhysicsEquation(
            name="de Broglie Wavelength",
            equation="lambda = h / p",
            latex=r"\lambda = \frac{h}{p}",
            description="Wavelength of matter wave",
            domain=PhysicsDomain.QUANTUM_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"lambda": "Wavelength (m)", "h": "Planck constant", "p": "Momentum (kg*m/s)"},
            discoverer="Louis de Broglie",
            year_discovered=1924
        ))
        
        self._add(PhysicsEquation(
            name="Time-Dependent Schrodinger Equation",
            equation="i * hbar * d(psi)/dt = H * psi",
            latex=r"i\hbar\frac{\partial \Psi}{\partial t} = \hat{H}\Psi",
            description="Fundamental equation of quantum mechanics",
            domain=PhysicsDomain.QUANTUM_MECHANICS,
            status=EquationStatus.FUNDAMENTAL,
            variables={"hbar": "Reduced Planck constant", "psi": "Wave function", "H": "Hamiltonian operator"},
            discoverer="Erwin Schrodinger",
            year_discovered=1926
        ))
        
        self._add(PhysicsEquation(
            name="Time-Independent Schrodinger Equation",
            equation="H * psi = E * psi",
            latex=r"\hat{H}\psi = E\psi",
            description="Eigenvalue equation for stationary states",
            domain=PhysicsDomain.QUANTUM_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"H": "Hamiltonian operator", "psi": "Wave function", "E": "Energy eigenvalue"},
            derived_from=["Time-Dependent Schrodinger Equation"]
        ))
        
        self._add(PhysicsEquation(
            name="Heisenberg Uncertainty Principle (Position-Momentum)",
            equation="Delta_x * Delta_p >= hbar / 2",
            latex=r"\Delta x \cdot \Delta p \geq \frac{\hbar}{2}",
            description="Fundamental limit on position-momentum precision",
            domain=PhysicsDomain.QUANTUM_MECHANICS,
            status=EquationStatus.FUNDAMENTAL,
            variables={"Delta_x": "Position uncertainty", "Delta_p": "Momentum uncertainty", "hbar": "Reduced Planck constant"},
            discoverer="Werner Heisenberg",
            year_discovered=1927
        ))
        
        self._add(PhysicsEquation(
            name="Energy-Time Uncertainty",
            equation="Delta_E * Delta_t >= hbar / 2",
            latex=r"\Delta E \cdot \Delta t \geq \frac{\hbar}{2}",
            description="Fundamental limit on energy-time precision",
            domain=PhysicsDomain.QUANTUM_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"Delta_E": "Energy uncertainty", "Delta_t": "Time uncertainty", "hbar": "Reduced Planck constant"}
        ))
        
        self._add(PhysicsEquation(
            name="Born Rule",
            equation="P(x) = |psi(x)|**2",
            latex=r"P(x) = |\Psi(x)|^2",
            description="Probability density from wave function",
            domain=PhysicsDomain.QUANTUM_MECHANICS,
            status=EquationStatus.FUNDAMENTAL,
            variables={"P": "Probability density", "psi": "Wave function"}
        ))
        
        self._add(PhysicsEquation(
            name="Expectation Value",
            equation="<A> = integral(psi* * A * psi * dx)",
            latex=r"\langle \hat{A} \rangle = \int \Psi^* \hat{A} \Psi \, dx",
            description="Average value of observable",
            domain=PhysicsDomain.QUANTUM_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"A": "Observable operator", "psi": "Wave function"}
        ))
        
        self._add(PhysicsEquation(
            name="Commutation Relation (Position-Momentum)",
            equation="[x, p] = i * hbar",
            latex=r"[\hat{x}, \hat{p}] = i\hbar",
            description="Fundamental commutator of QM",
            domain=PhysicsDomain.QUANTUM_MECHANICS,
            status=EquationStatus.FUNDAMENTAL,
            variables={"x": "Position operator", "p": "Momentum operator", "hbar": "Reduced Planck constant"}
        ))
        
        self._add(PhysicsEquation(
            name="Hydrogen Atom Energy Levels",
            equation="E_n = -13.6 eV / n**2",
            latex=r"E_n = -\frac{13.6 \text{ eV}}{n^2} = -\frac{m_e e^4}{2(4\pi\epsilon_0)^2\hbar^2 n^2}",
            description="Energy levels of hydrogen atom",
            domain=PhysicsDomain.QUANTUM_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"E_n": "Energy (eV)", "n": "Principal quantum number"},
            derived_from=["Time-Independent Schrodinger Equation"]
        ))
        
        self._add(PhysicsEquation(
            name="Quantum Harmonic Oscillator Energy",
            equation="E_n = hbar * omega * (n + 1/2)",
            latex=r"E_n = \hbar\omega\left(n + \frac{1}{2}\right)",
            description="Energy levels of quantum harmonic oscillator",
            domain=PhysicsDomain.QUANTUM_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"E_n": "Energy", "hbar": "Reduced Planck constant", "omega": "Angular frequency", "n": "Quantum number (0,1,2,...)"}
        ))
        
        self._add(PhysicsEquation(
            name="Photoelectric Effect",
            equation="E_k = h * nu - phi",
            latex=r"E_k = h\nu - \phi",
            description="Kinetic energy of emitted electron",
            domain=PhysicsDomain.QUANTUM_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"E_k": "Kinetic energy", "h": "Planck constant", "nu": "Frequency", "phi": "Work function"},
            discoverer="Albert Einstein",
            year_discovered=1905
        ))
        
        self._add(PhysicsEquation(
            name="Compton Scattering",
            equation="Delta_lambda = (h / (m_e * c)) * (1 - cos(theta))",
            latex=r"\Delta\lambda = \frac{h}{m_e c}(1 - \cos\theta)",
            description="Wavelength shift in photon-electron scattering",
            domain=PhysicsDomain.QUANTUM_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"Delta_lambda": "Wavelength shift", "h": "Planck constant", "m_e": "Electron mass", "c": "Speed of light", "theta": "Scattering angle"},
            discoverer="Arthur Compton",
            year_discovered=1923
        ))
        
        # ============================================================
        # SPECIAL RELATIVITY
        # ============================================================
        
        self._add(PhysicsEquation(
            name="Lorentz Factor",
            equation="gamma = 1 / sqrt(1 - v**2/c**2)",
            latex=r"\gamma = \frac{1}{\sqrt{1 - v^2/c^2}}",
            description="Relativistic gamma factor",
            domain=PhysicsDomain.SPECIAL_RELATIVITY,
            status=EquationStatus.FUNDAMENTAL,
            variables={"gamma": "Lorentz factor", "v": "Velocity", "c": "Speed of light"}
        ))
        
        self._add(PhysicsEquation(
            name="Time Dilation",
            equation="Delta_t = gamma * Delta_t_0",
            latex=r"\Delta t = \gamma \Delta t_0",
            description="Moving clocks run slow",
            domain=PhysicsDomain.SPECIAL_RELATIVITY,
            status=EquationStatus.PROVEN,
            variables={"Delta_t": "Dilated time", "Delta_t_0": "Proper time", "gamma": "Lorentz factor"},
            discoverer="Albert Einstein",
            year_discovered=1905
        ))
        
        self._add(PhysicsEquation(
            name="Length Contraction",
            equation="L = L_0 / gamma",
            latex=r"L = \frac{L_0}{\gamma}",
            description="Moving objects contract along direction of motion",
            domain=PhysicsDomain.SPECIAL_RELATIVITY,
            status=EquationStatus.PROVEN,
            variables={"L": "Contracted length", "L_0": "Proper length", "gamma": "Lorentz factor"}
        ))
        
        self._add(PhysicsEquation(
            name="Mass-Energy Equivalence",
            equation="E = m * c**2",
            latex=r"E = mc^2",
            description="Rest energy of mass",
            domain=PhysicsDomain.SPECIAL_RELATIVITY,
            status=EquationStatus.FUNDAMENTAL,
            variables={"E": "Energy (J)", "m": "Mass (kg)", "c": "Speed of light (m/s)"},
            discoverer="Albert Einstein",
            year_discovered=1905
        ))
        
        self._add(PhysicsEquation(
            name="Relativistic Energy",
            equation="E = gamma * m * c**2",
            latex=r"E = \gamma mc^2",
            description="Total energy of moving particle",
            domain=PhysicsDomain.SPECIAL_RELATIVITY,
            status=EquationStatus.PROVEN,
            variables={"E": "Total energy", "gamma": "Lorentz factor", "m": "Rest mass", "c": "Speed of light"}
        ))
        
        self._add(PhysicsEquation(
            name="Relativistic Momentum",
            equation="p = gamma * m * v",
            latex=r"\vec{p} = \gamma m\vec{v}",
            description="Momentum of relativistic particle",
            domain=PhysicsDomain.SPECIAL_RELATIVITY,
            status=EquationStatus.PROVEN,
            variables={"p": "Momentum", "gamma": "Lorentz factor", "m": "Rest mass", "v": "Velocity"}
        ))
        
        self._add(PhysicsEquation(
            name="Energy-Momentum Relation",
            equation="E**2 = (p*c)**2 + (m*c**2)**2",
            latex=r"E^2 = (pc)^2 + (mc^2)^2",
            description="Fundamental relation between energy and momentum",
            domain=PhysicsDomain.SPECIAL_RELATIVITY,
            status=EquationStatus.PROVEN,
            variables={"E": "Energy", "p": "Momentum", "m": "Rest mass", "c": "Speed of light"}
        ))
        
        self._add(PhysicsEquation(
            name="Relativistic Kinetic Energy",
            equation="E_k = (gamma - 1) * m * c**2",
            latex=r"E_k = (\gamma - 1)mc^2",
            description="Kinetic energy at relativistic speeds",
            domain=PhysicsDomain.SPECIAL_RELATIVITY,
            status=EquationStatus.PROVEN,
            variables={"E_k": "Kinetic energy", "gamma": "Lorentz factor", "m": "Rest mass", "c": "Speed of light"}
        ))
        
        self._add(PhysicsEquation(
            name="Velocity Addition",
            equation="u = (v + w) / (1 + v*w/c**2)",
            latex=r"u = \frac{v + w}{1 + vw/c^2}",
            description="Relativistic velocity addition",
            domain=PhysicsDomain.SPECIAL_RELATIVITY,
            status=EquationStatus.PROVEN,
            variables={"u": "Combined velocity", "v": "Velocity 1", "w": "Velocity 2", "c": "Speed of light"}
        ))
        
        self._add(PhysicsEquation(
            name="Spacetime Interval",
            equation="ds**2 = c**2*dt**2 - dx**2 - dy**2 - dz**2",
            latex=r"ds^2 = c^2dt^2 - dx^2 - dy^2 - dz^2",
            description="Invariant interval in spacetime",
            domain=PhysicsDomain.SPECIAL_RELATIVITY,
            status=EquationStatus.FUNDAMENTAL,
            variables={"ds": "Spacetime interval", "c": "Speed of light", "dt": "Time interval", "dx,dy,dz": "Space intervals"}
        ))
        
        self._add(PhysicsEquation(
            name="Relativistic Doppler Effect",
            equation="f_observed = f_source * sqrt((1 - v/c) / (1 + v/c))",
            latex=r"f_{obs} = f_s\sqrt{\frac{1 - v/c}{1 + v/c}}",
            description="Frequency shift due to relative motion",
            domain=PhysicsDomain.SPECIAL_RELATIVITY,
            status=EquationStatus.PROVEN,
            variables={"f_observed": "Observed frequency", "f_source": "Source frequency", "v": "Relative velocity", "c": "Speed of light"}
        ))
        
        # ============================================================
        # GENERAL RELATIVITY
        # ============================================================
        
        self._add(PhysicsEquation(
            name="Einstein Field Equations",
            equation="G_munu = (8*pi*G/c**4) * T_munu",
            latex=r"G_{\mu\nu} = \frac{8\pi G}{c^4}T_{\mu\nu}",
            description="Spacetime geometry determined by matter/energy",
            domain=PhysicsDomain.GENERAL_RELATIVITY,
            status=EquationStatus.FUNDAMENTAL,
            variables={"G_munu": "Einstein tensor", "G": "Gravitational constant", "c": "Speed of light", "T_munu": "Stress-energy tensor"},
            discoverer="Albert Einstein",
            year_discovered=1915
        ))
        
        self._add(PhysicsEquation(
            name="Einstein Tensor",
            equation="G_munu = R_munu - (1/2) * g_munu * R",
            latex=r"G_{\mu\nu} = R_{\mu\nu} - \frac{1}{2}g_{\mu\nu}R",
            description="Combination of Ricci tensor and scalar",
            domain=PhysicsDomain.GENERAL_RELATIVITY,
            status=EquationStatus.PROVEN,
            variables={"G_munu": "Einstein tensor", "R_munu": "Ricci tensor", "g_munu": "Metric tensor", "R": "Ricci scalar"}
        ))
        
        self._add(PhysicsEquation(
            name="Geodesic Equation",
            equation="d**2*x_mu/d*tau**2 + Gamma_mu_nu_rho * dx_nu/d*tau * dx_rho/d*tau = 0",
            latex=r"\frac{d^2x^\mu}{d\tau^2} + \Gamma^\mu_{\nu\rho}\frac{dx^\nu}{d\tau}\frac{dx^\rho}{d\tau} = 0",
            description="Path of free-falling particle in curved spacetime",
            domain=PhysicsDomain.GENERAL_RELATIVITY,
            status=EquationStatus.FUNDAMENTAL,
            variables={"x_mu": "Coordinates", "tau": "Proper time", "Gamma": "Christoffel symbols"}
        ))
        
        self._add(PhysicsEquation(
            name="Schwarzschild Metric",
            equation="ds**2 = (1-r_s/r)*c**2*dt**2 - (1-r_s/r)**(-1)*dr**2 - r**2*dOmega**2",
            latex=r"ds^2 = \left(1-\frac{r_s}{r}\right)c^2dt^2 - \frac{dr^2}{1-r_s/r} - r^2d\Omega^2",
            description="Metric around non-rotating spherical mass",
            domain=PhysicsDomain.GENERAL_RELATIVITY,
            status=EquationStatus.PROVEN,
            variables={"ds": "Line element", "r_s": "Schwarzschild radius", "r": "Radial coordinate", "dOmega": "Angular element"},
            discoverer="Karl Schwarzschild",
            year_discovered=1916
        ))
        
        self._add(PhysicsEquation(
            name="Schwarzschild Radius",
            equation="r_s = 2 * G * M / c**2",
            latex=r"r_s = \frac{2GM}{c^2}",
            description="Event horizon radius of black hole",
            domain=PhysicsDomain.GENERAL_RELATIVITY,
            status=EquationStatus.PROVEN,
            variables={"r_s": "Schwarzschild radius (m)", "G": "Gravitational constant", "M": "Mass (kg)", "c": "Speed of light"}
        ))
        
        self._add(PhysicsEquation(
            name="Gravitational Time Dilation",
            equation="Delta_t = Delta_t_0 / sqrt(1 - r_s/r)",
            latex=r"\Delta t = \frac{\Delta t_0}{\sqrt{1 - r_s/r}}",
            description="Time runs slower in gravitational field",
            domain=PhysicsDomain.GENERAL_RELATIVITY,
            status=EquationStatus.PROVEN,
            variables={"Delta_t": "Time at distance", "Delta_t_0": "Proper time", "r_s": "Schwarzschild radius", "r": "Distance from center"}
        ))
        
        self._add(PhysicsEquation(
            name="Gravitational Redshift",
            equation="z = 1/sqrt(1 - r_s/r) - 1",
            latex=r"z = \frac{1}{\sqrt{1 - r_s/r}} - 1",
            description="Frequency shift escaping gravitational field",
            domain=PhysicsDomain.GENERAL_RELATIVITY,
            status=EquationStatus.PROVEN,
            variables={"z": "Redshift", "r_s": "Schwarzschild radius", "r": "Emission radius"}
        ))
        
        # ============================================================
        # FLUID DYNAMICS
        # ============================================================
        
        self._add(PhysicsEquation(
            name="Continuity Equation (Fluids)",
            equation="d*rho/dt + div(rho * v) = 0",
            latex=r"\frac{\partial \rho}{\partial t} + \nabla \cdot (\rho \vec{v}) = 0",
            description="Mass conservation in fluid flow",
            domain=PhysicsDomain.FLUID_DYNAMICS,
            status=EquationStatus.FUNDAMENTAL,
            variables={"rho": "Density (kg/m^3)", "v": "Velocity (m/s)", "t": "Time"}
        ))
        
        self._add(PhysicsEquation(
            name="Navier-Stokes Equation",
            equation="rho*(dv/dt + (v.grad)v) = -grad(P) + mu*laplacian(v) + rho*g",
            latex=r"\rho\left(\frac{\partial \vec{v}}{\partial t} + (\vec{v}\cdot\nabla)\vec{v}\right) = -\nabla P + \mu\nabla^2\vec{v} + \rho\vec{g}",
            description="Fundamental equation of viscous fluid flow",
            domain=PhysicsDomain.FLUID_DYNAMICS,
            status=EquationStatus.FUNDAMENTAL,
            variables={"rho": "Density", "v": "Velocity", "P": "Pressure", "mu": "Viscosity", "g": "Gravity"}
        ))
        
        self._add(PhysicsEquation(
            name="Bernoulli's Equation",
            equation="P + (1/2)*rho*v**2 + rho*g*h = constant",
            latex=r"P + \frac{1}{2}\rho v^2 + \rho gh = \text{const}",
            description="Energy conservation along streamline",
            domain=PhysicsDomain.FLUID_DYNAMICS,
            status=EquationStatus.PROVEN,
            variables={"P": "Pressure (Pa)", "rho": "Density (kg/m^3)", "v": "Speed (m/s)", "g": "Gravity (m/s^2)", "h": "Height (m)"},
            conditions=["Inviscid flow", "Steady flow", "Incompressible"],
            discoverer="Daniel Bernoulli",
            year_discovered=1738
        ))
        
        self._add(PhysicsEquation(
            name="Stokes' Law",
            equation="F_d = 6 * pi * mu * r * v",
            latex=r"F_d = 6\pi\mu rv",
            description="Drag force on sphere in viscous fluid",
            domain=PhysicsDomain.FLUID_DYNAMICS,
            status=EquationStatus.PROVEN,
            variables={"F_d": "Drag force (N)", "mu": "Viscosity (Pa*s)", "r": "Radius (m)", "v": "Velocity (m/s)"},
            conditions=["Low Reynolds number (Re << 1)"]
        ))
        
        self._add(PhysicsEquation(
            name="Reynolds Number",
            equation="Re = rho * v * L / mu",
            latex=r"Re = \frac{\rho v L}{\mu}",
            description="Ratio of inertial to viscous forces",
            domain=PhysicsDomain.FLUID_DYNAMICS,
            status=EquationStatus.PROVEN,
            variables={"Re": "Reynolds number (dimensionless)", "rho": "Density", "v": "Velocity", "L": "Characteristic length", "mu": "Viscosity"}
        ))
        
        self._add(PhysicsEquation(
            name="Poiseuille's Law",
            equation="Q = (pi * Delta_P * r**4) / (8 * mu * L)",
            latex=r"Q = \frac{\pi \Delta P r^4}{8\mu L}",
            description="Volumetric flow rate in pipe",
            domain=PhysicsDomain.FLUID_DYNAMICS,
            status=EquationStatus.PROVEN,
            variables={"Q": "Flow rate (m^3/s)", "Delta_P": "Pressure difference (Pa)", "r": "Radius (m)", "mu": "Viscosity (Pa*s)", "L": "Length (m)"},
            conditions=["Laminar flow", "Newtonian fluid"]
        ))
        
        # ============================================================
        # OPTICS
        # ============================================================
        
        self._add(PhysicsEquation(
            name="Snell's Law",
            equation="n1 * sin(theta1) = n2 * sin(theta2)",
            latex=r"n_1\sin\theta_1 = n_2\sin\theta_2",
            description="Law of refraction",
            domain=PhysicsDomain.OPTICS,
            status=EquationStatus.EMPIRICAL,
            variables={"n1": "Refractive index 1", "theta1": "Angle of incidence", "n2": "Refractive index 2", "theta2": "Angle of refraction"},
            discoverer="Willebrord Snellius",
            year_discovered=1621
        ))
        
        self._add(PhysicsEquation(
            name="Thin Lens Equation",
            equation="1/f = 1/d_o + 1/d_i",
            latex=r"\frac{1}{f} = \frac{1}{d_o} + \frac{1}{d_i}",
            description="Object-image relation for thin lens",
            domain=PhysicsDomain.OPTICS,
            status=EquationStatus.PROVEN,
            variables={"f": "Focal length (m)", "d_o": "Object distance (m)", "d_i": "Image distance (m)"}
        ))
        
        self._add(PhysicsEquation(
            name="Magnification (Lens)",
            equation="M = -d_i / d_o = h_i / h_o",
            latex=r"M = -\frac{d_i}{d_o} = \frac{h_i}{h_o}",
            description="Linear magnification of lens",
            domain=PhysicsDomain.OPTICS,
            status=EquationStatus.PROVEN,
            variables={"M": "Magnification", "d_i": "Image distance", "d_o": "Object distance", "h_i": "Image height", "h_o": "Object height"}
        ))
        
        self._add(PhysicsEquation(
            name="Lensmaker's Equation",
            equation="1/f = (n-1)*(1/R1 - 1/R2)",
            latex=r"\frac{1}{f} = (n-1)\left(\frac{1}{R_1} - \frac{1}{R_2}\right)",
            description="Focal length from lens geometry",
            domain=PhysicsDomain.OPTICS,
            status=EquationStatus.PROVEN,
            variables={"f": "Focal length", "n": "Refractive index", "R1": "Radius of curvature 1", "R2": "Radius of curvature 2"}
        ))
        
        self._add(PhysicsEquation(
            name="Diffraction Grating",
            equation="d * sin(theta) = m * lambda",
            latex=r"d\sin\theta = m\lambda",
            description="Maxima condition for diffraction grating",
            domain=PhysicsDomain.OPTICS,
            status=EquationStatus.PROVEN,
            variables={"d": "Grating spacing (m)", "theta": "Diffraction angle", "m": "Order (integer)", "lambda": "Wavelength (m)"}
        ))
        
        self._add(PhysicsEquation(
            name="Single Slit Diffraction (Minima)",
            equation="a * sin(theta) = m * lambda",
            latex=r"a\sin\theta = m\lambda",
            description="Minima condition for single slit",
            domain=PhysicsDomain.OPTICS,
            status=EquationStatus.PROVEN,
            variables={"a": "Slit width (m)", "theta": "Angle", "m": "Order (nonzero integer)", "lambda": "Wavelength"}
        ))
        
        self._add(PhysicsEquation(
            name="Double Slit Interference (Maxima)",
            equation="d * sin(theta) = m * lambda",
            latex=r"d\sin\theta = m\lambda",
            description="Maxima condition for double slit",
            domain=PhysicsDomain.OPTICS,
            status=EquationStatus.PROVEN,
            variables={"d": "Slit separation (m)", "theta": "Angle", "m": "Order (integer)", "lambda": "Wavelength"}
        ))
        
        self._add(PhysicsEquation(
            name="Brewster's Angle",
            equation="tan(theta_B) = n2 / n1",
            latex=r"\tan\theta_B = \frac{n_2}{n_1}",
            description="Angle of complete polarization",
            domain=PhysicsDomain.OPTICS,
            status=EquationStatus.PROVEN,
            variables={"theta_B": "Brewster's angle", "n1": "Refractive index 1", "n2": "Refractive index 2"}
        ))
        
        self._add(PhysicsEquation(
            name="Malus's Law",
            equation="I = I_0 * cos(theta)**2",
            latex=r"I = I_0\cos^2\theta",
            description="Intensity through polarizer",
            domain=PhysicsDomain.OPTICS,
            status=EquationStatus.PROVEN,
            variables={"I": "Transmitted intensity", "I_0": "Incident intensity", "theta": "Angle between polarization and axis"}
        ))
        
        # ============================================================
        # NUCLEAR PHYSICS
        # ============================================================
        
        self._add(PhysicsEquation(
            name="Nuclear Binding Energy",
            equation="B = (Z*m_p + N*m_n - M_nucleus) * c**2",
            latex=r"B = (Zm_p + Nm_n - M_{nucleus})c^2",
            description="Energy to disassemble nucleus",
            domain=PhysicsDomain.NUCLEAR_PHYSICS,
            status=EquationStatus.PROVEN,
            variables={"B": "Binding energy", "Z": "Proton number", "m_p": "Proton mass", "N": "Neutron number", "m_n": "Neutron mass", "M_nucleus": "Nuclear mass"}
        ))
        
        self._add(PhysicsEquation(
            name="Semi-Empirical Mass Formula",
            equation="B = a_V*A - a_S*A**(2/3) - a_C*Z**2/A**(1/3) - a_A*(N-Z)**2/A + delta",
            latex=r"B = a_VA - a_SA^{2/3} - a_C\frac{Z^2}{A^{1/3}} - a_A\frac{(N-Z)^2}{A} + \delta",
            description="Bethe-Weizsacker formula for nuclear binding",
            domain=PhysicsDomain.NUCLEAR_PHYSICS,
            status=EquationStatus.EMPIRICAL,
            variables={"B": "Binding energy", "A": "Mass number", "Z": "Proton number", "N": "Neutron number", "a_V,a_S,a_C,a_A": "Empirical constants", "delta": "Pairing term"}
        ))
        
        self._add(PhysicsEquation(
            name="Radioactive Decay Law",
            equation="N(t) = N_0 * exp(-lambda * t)",
            latex=r"N(t) = N_0 e^{-\lambda t}",
            description="Number of nuclei vs time",
            domain=PhysicsDomain.NUCLEAR_PHYSICS,
            status=EquationStatus.PROVEN,
            variables={"N": "Number of nuclei", "N_0": "Initial number", "lambda": "Decay constant", "t": "Time"}
        ))
        
        self._add(PhysicsEquation(
            name="Half-Life",
            equation="t_half = ln(2) / lambda",
            latex=r"t_{1/2} = \frac{\ln 2}{\lambda}",
            description="Time for half of nuclei to decay",
            domain=PhysicsDomain.NUCLEAR_PHYSICS,
            status=EquationStatus.PROVEN,
            variables={"t_half": "Half-life", "lambda": "Decay constant"},
            derived_from=["Radioactive Decay Law"]
        ))
        
        self._add(PhysicsEquation(
            name="Activity",
            equation="A = lambda * N = A_0 * exp(-lambda * t)",
            latex=r"A = \lambda N = A_0 e^{-\lambda t}",
            description="Rate of radioactive decay",
            domain=PhysicsDomain.NUCLEAR_PHYSICS,
            status=EquationStatus.PROVEN,
            variables={"A": "Activity (Bq)", "lambda": "Decay constant", "N": "Number of nuclei"}
        ))
        
        self._add(PhysicsEquation(
            name="Q-Value",
            equation="Q = (m_initial - m_final) * c**2",
            latex=r"Q = (m_i - m_f)c^2",
            description="Energy released in nuclear reaction",
            domain=PhysicsDomain.NUCLEAR_PHYSICS,
            status=EquationStatus.PROVEN,
            variables={"Q": "Q-value (MeV)", "m_initial": "Initial mass", "m_final": "Final mass", "c": "Speed of light"}
        ))
        
        # ============================================================
        # WAVES
        # ============================================================
        
        self._add(PhysicsEquation(
            name="Wave Equation",
            equation="d2y/dx2 = (1/v**2) * d2y/dt2",
            latex=r"\frac{\partial^2 y}{\partial x^2} = \frac{1}{v^2}\frac{\partial^2 y}{\partial t^2}",
            description="General wave equation",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            status=EquationStatus.FUNDAMENTAL,
            variables={"y": "Displacement", "x": "Position", "t": "Time", "v": "Wave speed"}
        ))
        
        self._add(PhysicsEquation(
            name="Wave Speed",
            equation="v = f * lambda = omega / k",
            latex=r"v = f\lambda = \frac{\omega}{k}",
            description="Relationship between frequency and wavelength",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"v": "Wave speed (m/s)", "f": "Frequency (Hz)", "lambda": "Wavelength (m)", "omega": "Angular frequency", "k": "Wave number"}
        ))
        
        self._add(PhysicsEquation(
            name="Standing Wave (String)",
            equation="lambda_n = 2*L/n",
            latex=r"\lambda_n = \frac{2L}{n}",
            description="Wavelengths of standing waves on string",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"lambda_n": "Wavelength of nth mode", "L": "String length", "n": "Mode number (1,2,3,...)"}
        ))
        
        self._add(PhysicsEquation(
            name="Wave Speed on String",
            equation="v = sqrt(T / mu)",
            latex=r"v = \sqrt{\frac{T}{\mu}}",
            description="Speed of wave on stretched string",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"v": "Wave speed (m/s)", "T": "Tension (N)", "mu": "Linear mass density (kg/m)"}
        ))
        
        self._add(PhysicsEquation(
            name="Doppler Effect (Sound)",
            equation="f_obs = f_source * (v + v_obs) / (v + v_source)",
            latex=r"f_{obs} = f_s\frac{v + v_o}{v + v_s}",
            description="Frequency shift due to motion (non-relativistic)",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"f_obs": "Observed frequency", "f_source": "Source frequency", "v": "Sound speed", "v_obs": "Observer velocity", "v_source": "Source velocity"}
        ))
        
        self._add(PhysicsEquation(
            name="Intensity and Amplitude",
            equation="I proportional_to A**2",
            latex=r"I \propto A^2",
            description="Intensity proportional to amplitude squared",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"I": "Intensity", "A": "Amplitude"}
        ))
        
        self._add(PhysicsEquation(
            name="Beat Frequency",
            equation="f_beat = |f1 - f2|",
            latex=r"f_{beat} = |f_1 - f_2|",
            description="Frequency of beats from two waves",
            domain=PhysicsDomain.CLASSICAL_MECHANICS,
            status=EquationStatus.PROVEN,
            variables={"f_beat": "Beat frequency", "f1": "Frequency 1", "f2": "Frequency 2"}
        ))
    
    def get(self, name: str) -> Optional[PhysicsEquation]:
        """Get equation by name."""
        return self.equations.get(name)
    
    def list_all(self) -> Dict[str, PhysicsEquation]:
        """Get all equations."""
        return self.equations.copy()
    
    def list_by_domain(self, domain: PhysicsDomain) -> Dict[str, PhysicsEquation]:
        """Get equations filtered by domain."""
        return {k: v for k, v in self.equations.items() if v.domain == domain}
    
    def list_by_status(self, status: EquationStatus) -> Dict[str, PhysicsEquation]:
        """Get equations filtered by status."""
        return {k: v for k, v in self.equations.items() if v.status == status}
    
    def search(self, query: str) -> Dict[str, PhysicsEquation]:
        """Search equations by name or description."""
        query = query.lower()
        return {
            k: v for k, v in self.equations.items()
            if query in v.name.lower() or query in v.description.lower()
        }
    
    def get_derivation_tree(self, name: str) -> Dict[str, Any]:
        """Get derivation tree for an equation."""
        eq = self.equations.get(name)
        if not eq:
            return {}
        
        tree = {
            'equation': eq.name,
            'derived_from': [],
            'leads_to': []
        }
        
        for parent_name in eq.derived_from:
            parent = self.equations.get(parent_name)
            if parent:
                tree['derived_from'].append({
                    'name': parent.name,
                    'equation': parent.equation
                })
        
        for child_name in eq.leads_to:
            child = self.equations.get(child_name)
            if child:
                tree['leads_to'].append({
                    'name': child.name,
                    'equation': child.equation
                })
        
        return tree


class PhysicsKnowledgeBase:
    """
    Unified interface to all physics knowledge.
    
    Combines constants, equations, and relationships.
    """
    
    def __init__(self):
        self.constants = PhysicsConstantsDatabase()
        self.equations = PhysicsEquationsDatabase()
    
    def get_constant(self, symbol: str) -> Optional[PhysicalConstant]:
        """Get a physical constant."""
        return self.constants.get(symbol)
    
    def get_equation(self, name: str) -> Optional[PhysicsEquation]:
        """Get an equation by name."""
        return self.equations.get(name)
    
    def search_all(self, query: str) -> Dict[str, Any]:
        """Search both constants and equations."""
        return {
            'constants': self.constants.search(query),
            'equations': self.equations.search(query)
        }
    
    def get_domain(self, domain: PhysicsDomain) -> Dict[str, Any]:
        """Get all knowledge for a domain."""
        return {
            'constants': self.constants.list_by_domain(domain),
            'equations': self.equations.list_by_domain(domain)
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base."""
        equations = self.equations.list_all()
        constants = self.constants.list_all()
        
        domain_counts = {}
        for eq in equations.values():
            domain = eq.domain.value
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        status_counts = {}
        for eq in equations.values():
            status = eq.status.value
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            'total_constants': len(constants),
            'total_equations': len(equations),
            'equations_by_domain': domain_counts,
            'equations_by_status': status_counts,
            'exact_constants': sum(1 for c in constants.values() if c.is_exact),
            'fundamental_equations': status_counts.get('fundamental', 0),
            'proven_equations': status_counts.get('proven', 0),
            'empirical_equations': status_counts.get('empirical', 0)
        }
    
    def export_all(self) -> Dict[str, Any]:
        """Export entire knowledge base as dictionary."""
        return {
            'constants': {k: v.to_dict() for k, v in self.constants.list_all().items()},
            'equations': {k: v.to_dict() for k, v in self.equations.list_all().items()},
            'statistics': self.get_statistics()
        }


# Singleton instance
_knowledge_base = None

def get_knowledge_base() -> PhysicsKnowledgeBase:
    """Get the singleton knowledge base instance."""
    global _knowledge_base
    if _knowledge_base is None:
        _knowledge_base = PhysicsKnowledgeBase()
    return _knowledge_base
