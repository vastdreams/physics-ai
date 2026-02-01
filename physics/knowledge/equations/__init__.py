"""
PATH: physics/knowledge/equations/__init__.py
PURPOSE: Physics equations organized by domain

MICRO-MODULAR STRUCTURE:
├── classical/
│   ├── newton.py       : Laws of motion, gravity
│   ├── energy.py       : KE, PE, work-energy
│   ├── momentum.py     : Linear/angular momentum
│   └── oscillations.py : SHM, damped, driven
├── electromagnetism/
│   ├── maxwell.py      : Maxwell's equations
│   ├── coulomb.py      : Electrostatics
│   ├── lorentz.py      : Lorentz force, EM waves
│   └── circuits.py     : RLC, Ohm's law
├── quantum/
│   ├── schrodinger.py  : Wave equation
│   ├── operators.py    : Commutators, observables
│   ├── hydrogen.py     : Atomic solutions
│   └── uncertainty.py  : Heisenberg relations
├── relativity/
│   ├── special.py      : Lorentz transforms, E=mc²
│   └── general.py      : Einstein field equations
└── thermodynamics/
    ├── laws.py         : Thermodynamic laws
    └── statistical.py  : Boltzmann, partition function
"""

# Import from subpackages - lazy loading for efficiency
def get_all_equation_nodes():
    """Lazy load all equation nodes."""
    from .classical import NODES as CLASSICAL
    from .electromagnetism import NODES as EM
    from .quantum import NODES as QUANTUM
    from .relativity import NODES as RELATIVITY
    from .thermodynamics import NODES as THERMO
    
    return CLASSICAL + EM + QUANTUM + RELATIVITY + THERMO

# For direct import
__all__ = ['get_all_equation_nodes']
