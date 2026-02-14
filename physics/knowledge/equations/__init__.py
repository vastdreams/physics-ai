"""
PATH: physics/knowledge/equations/__init__.py
PURPOSE: Physics equations organized by domain

MICRO-MODULAR STRUCTURE:
├── classical/
│   ├── newton.py       : Laws of motion, gravity
│   ├── energy.py       : KE, PE, work-energy
│   ├── momentum.py     : Linear/angular momentum
│   ├── oscillations.py : SHM, damped, driven
│   ├── rotational.py   : Rotation, inertia, gyroscopes
│   ├── lagrangian.py   : Lagrangian/Hamiltonian mechanics
│   └── orbital.py      : Kepler, orbital mechanics
├── electromagnetism/
│   ├── maxwell.py      : Maxwell's equations
│   ├── coulomb.py      : Electrostatics
│   ├── waves.py        : EM waves
│   └── circuits.py     : RLC, AC/DC circuits
├── quantum/
│   ├── schrodinger.py      : Wave equation
│   ├── uncertainty.py      : Heisenberg relations
│   ├── angular_momentum.py : Spin, L², selection rules
│   ├── perturbation.py     : Perturbation theory
│   └── scattering.py       : Cross sections, S-matrix
├── relativity/
│   ├── special.py      : Lorentz transforms, E=mc²
│   └── general.py      : Einstein field equations
├── thermodynamics/
│   └── laws.py         : Thermodynamic laws
├── fluids/
│   ├── fundamental.py  : Navier-Stokes, Bernoulli
│   ├── compressible.py : Shocks, Mach, isentropic
│   └── turbulence.py   : TKE, Kolmogorov, RANS
├── optics/
│   ├── geometric.py    : Snell, lenses, mirrors
│   ├── wave_optics.py  : Interference, diffraction
│   └── quantum_optics.py: Photons, lasers, blackbody
├── nuclear/
│   ├── radioactivity.py: Decay laws, half-life
│   ├── nuclear_reactions.py: Binding, fission, fusion
│   └── particle.py     : Dirac, Standard Model
├── condensed/
│   ├── solid_state.py  : Band theory, semiconductors
│   └── superconductivity.py: BCS, Josephson
├── astrophysics/
│   ├── stellar.py      : Stellar structure, limits
│   └── cosmology.py    : Friedmann, Hubble, CMB
├── plasma/
│   ├── plasma_fundamentals.py: Debye, plasma freq
│   └── mhd.py          : MHD, Alfvén waves
└── acoustics/
    ├── waves.py        : Wave equation, Doppler
    └── sound.py        : Sound, reverberation
"""

def get_all_equation_nodes() -> list:
    """Lazy-load and return all equation nodes from every physics domain."""
    from .classical import NODES as CLASSICAL
    from .electromagnetism import NODES as EM
    from .quantum import NODES as QUANTUM
    from .relativity import NODES as RELATIVITY
    from .thermodynamics import NODES as THERMO
    from .fluids import NODES as FLUIDS
    from .optics import NODES as OPTICS
    from .nuclear import NODES as NUCLEAR
    from .condensed import NODES as CONDENSED
    from .astrophysics import NODES as ASTRO
    from .plasma import NODES as PLASMA
    from .acoustics import NODES as ACOUSTICS
    
    return (
        CLASSICAL + EM + QUANTUM + RELATIVITY + THERMO +
        FLUIDS + OPTICS + NUCLEAR + CONDENSED + ASTRO + PLASMA + ACOUSTICS
    )

# For direct import
__all__ = ['get_all_equation_nodes']
