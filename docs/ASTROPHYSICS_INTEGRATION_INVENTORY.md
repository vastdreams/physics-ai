# Beyond Frontier — Repo Understanding & Astrophysics Integration Inventory

> **Purpose**: Understand the current codebase and inventory code/concepts that can be lifted or integrated into an open-source project aligned with specialized astrophysics engines (REBOUND, RAMSES, pynbody) and Python libraries (Astropy, galpy, SunPy).

---

## 1. Repo Understanding

### 1.1 What This Repo Is

**Beyond Frontier** is a neurosymbolic, self-evolving system for physics:

- **Vision**: "The operating system for physics research" — unified infrastructure for discovery, validation, and computation.
- **Stack**: Python backend (Flask API, SymPy, NumPy/SciPy), React frontend (Vite, Tailwind), optional Pyodide for in-browser Python.
- **Core idea**: Combine neural (pattern/embedding) and symbolic (rules, equations) processing; maintain a **physics knowledge graph** of equations, constants, and relations; run simulations with conservation-law validation.

### 1.2 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  Core: NeurosymboticEngine (core/engine.py)                     │
│  Neural + Symbolic + Hybrid integration                        │
├─────────────────────────────────────────────────────────────────┤
│  Physics domain: equations, models, solvers, knowledge graph    │
│  Rules engine, Reasoning (4 types), Self-evolution              │
├─────────────────────────────────────────────────────────────────┤
│  API (Flask): simulate, nodes, rules, evolution, vector, cot…   │
│  Frontend: Dashboard, Chat, Simulations (Pendulum, Spring, etc.)│
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 Evidence (Key Paths)

| Concept | Location |
|--------|----------|
| Main engine | `core/engine.py` |
| Physics models (HarmonicOscillator, TwoBodyGravity, Pendulum, Projectile) | `physics/models.py` |
| Equation knowledge (orbital, stellar, cosmology, MHD) | `physics/knowledge/equations/` |
| Astro-style solver (coordinates, cosmology, stellar) | `physics/solvers/astro_solver.py` |
| Knowledge graph base (nodes, loader, relations) | `physics/knowledge/base/` |
| API simulate | `api/v1/simulate.py` (uses `PhysicsIntegrator`) |
| Frontend simulations | `frontend/src/components/simulations/` |

---

## 2. Full Code & Concept Inventory

### 2.1 Physics Knowledge Layer

**Base types** (`physics/knowledge/base/`):

- **Node types**: `KnowledgeNode`, `ConstantNode`, `EquationNode`, `TheoremNode`, `PrincipleNode`.
- **Metadata**: `id`, `name`, `domain`, `status` (FUNDAMENTAL, PROVEN, EXPERIMENTAL, EMPIRICAL, …), `derives_from`, `leads_to`, `uses`, `conditions`, LaTeX, SymPy strings.
- **Loader**: `NodeLoader` — discovers modules under `physics.knowledge`, loads `NODES` and optional `RELATIONS`, builds in-memory graph.

**Constants** (`physics/knowledge/constants/`):

- Universal, EM, thermodynamic, particle, atomic (CODATA-style).

**Equations by domain** (all under `physics/knowledge/equations/`):

| Domain | Files | Concepts (examples) |
|--------|-------|----------------------|
| **Classical** | newton, energy, momentum, oscillations, rotational, lagrangian, **orbital**, **gravitation** | F=ma, gravity, Kepler laws, vis-viva, Hohmann, Roche, Hill sphere, eccentricity vector |
| **Astrophysics** | **stellar**, **cosmology** | Mass–luminosity, hydrostatic equilibrium, Eddington, Chandrasekhar, TOV, Jeans mass/length, virial, pulsar spindown; Friedmann, Hubble, redshift, critical density, luminosity/angular-diameter distance, CMB, Saha, particle horizon |
| **Plasma / MHD** | **mhd**, plasma_fundamentals | MHD momentum, ideal Ohm, magnetic pressure, β, Alfvén speed, induction, Sweet–Parker, Grad–Shafranov |
| **Relativity** | special, general | Lorentz, E=mc², Schwarzschild radius (also in gravitation) |
| **Quantum** | schrodinger, hydrogen, angular_momentum, perturbation, scattering, … | TISE, hydrogen atom, spherical harmonics |
| **EM, thermo, fluids, optics, nuclear, condensed, acoustics** | (multiple files) | Maxwell, thermodynamics, Navier–Stokes, optics, nuclear, BCS, sound |

**Reasoning** (`physics/knowledge/reasoning/`):

- **Tree index**: Hierarchical navigation of physics topics (domain → topic → concepts).
- **Reasoner**: LLM-guided retrieval over the tree (domain selection → topic narrowing → concept/relation following); returns `ReasoningPath` with steps and final nodes.
- **Retrieval**: Combines tree-based reasoning with optional vector/embedding.

**Lift value for astrophysics**: The **equation graph** (orbital, stellar, cosmology, MHD) and **constant system** are directly reusable. The **reasoner** can drive “which equations/parameters does this problem need?” for REBOUND/galpy/Astropy workflows.

---

### 2.2 Solvers

| Solver | Path | Capabilities |
|--------|------|---------------|
| **astro_solver** | `physics/solvers/astro_solver.py` | **Astropy/SunPy-inspired**: `AstroConstants` (c, G, h, au, pc, ly, M_sun, R_sun, L_sun, H_0, T_cmb); `CoordinateFrame` (ICRS, Galactic, Ecliptic, AltAz, Heliocentric); `SkyCoord` (lon/lat/distance, to_cartesian, transform_to ICRS↔Galactic, separation via Vincenty); **Cosmology** (ΛCDM: H0, Om0, Ode0, comoving_distance, luminosity_distance, angular_diameter_distance, lookback_time, age, critical_density, distance_modulus); **StellarPhysics** (Stefan–Boltzmann luminosity, main-sequence L(M), lifetime, Schwarzschild radius, Eddington L, Wien λ_max, Planck spectrum); **SolarPhysics** (differential rotation, Carrington rotation, B0, solar constant); **OrbitalMechanics** (kepler_period, orbital_velocity, escape_velocity, hill_sphere, vis_viva, hohmann_transfer_dv). Presets: Planck18, WMAP9. |
| **quantum_solver** | `physics/solvers/quantum_solver.py` | Hydrogen, harmonic oscillator potential, etc. |
| **optics_solver** | `physics/solvers/optics_solver.py` | Optics computations. |
| **differential_solver** | Used by `PhysicsIntegrator` | Euler, etc. |

**Lift value**: `astro_solver` is the **main bridge** to Astropy/galpy/SunPy: same concepts (coordinates, cosmology, stellar/orbital mechanics). Can be refactored to **wrap or delegate** to `astropy.coordinates`, `astropy.cosmology`, `galpy`, `sunpy` where we want full compatibility, while keeping our equation graph and reasoning on top.

---

### 2.3 Simulation Models (ODE-Based)

**Location**: `physics/models.py`.

**Abstract base**: `PhysicsModel` — `state_variables`, `derivatives(state)`, `energy(state)`, `momentum(state)`, `simulate(initial_conditions, t_start, t_end, dt, method)` → `SimulationResult` (states, times, conservation_violations). Integration: Euler, RK4, RK45, adaptive.

**Concrete models**:

| Model | State | Notes |
|-------|-------|--------|
| **HarmonicOscillator** | x, v | Spring-mass; energy checked. |
| **Pendulum** | θ, ω | Arbitrary amplitude; energy checked. |
| **TwoBodyGravity** | x, y, vx, vy | **Reduced-mass 2-body** in plane; μ = G(m1+m2); energy and angular momentum checked. |
| **ProjectileMotion** | x, y, vx, vy | With optional drag (Cd, A, ρ). |

**Factory**: `create_model(model_type, **kwargs)` for `harmonic_oscillator`, `pendulum`, `two_body_gravity`, `projectile_motion`.

**Gap**: The **API** `POST /api/v1/simulate` uses `PhysicsIntegrator`, which does **not** call `create_model` or these classes; it uses a placeholder ODE. So the production simulation path for two-body (and others) is not yet wired in the API.

**Lift value for N-body**:  
- **TwoBodyGravity** is a 2-body kernel; conceptually the same physics as REBOUND’s 2-body case.  
- **PhysicsModel** pattern (state → derivatives → integrate → validate conservation) is the right abstraction for “wrap REBOUND/pynbody as a PhysicsModel” or “compare our 2-body with REBOUND”.  
- We can add an **N-body model** that either (a) calls REBOUND/pynbody under the hood, or (b) uses our equation graph to configure them (e.g. units, G, initial conditions from vis-viva/Kepler).

---

### 2.4 Integration & API Layer

**PhysicsIntegrator** (`physics/integration/physics_integrator.py`):

- `simulate(scenario, initial_conditions, time_span, num_steps)`.
- Currently: theory selection (energy/velocity) → placeholder derivative → Euler → validation stub. **Does not** use `physics.models` or `create_model`.

**Simulate API** (`api/v1/simulate.py`):

- `POST /api/v1/simulate`: body has `scenario`, `initial_conditions`, `time_span`, `num_steps`; calls `integrator.simulate(...)`.

**Lift value**: Once we wire `PhysicsIntegrator` to `create_model` (and optionally to REBOUND/pynbody), the same API can drive 2-body, N-body, and later MHD “scenarios” with a single contract (initial conditions, time span, validation).

---

### 2.5 Core Engine & Reasoning

- **NeurosymboticEngine** (`core/engine.py`): Neural + symbolic + hybrid; processes physics-style inputs (e.g. mass, velocity) and applies rules.  
- **Reasoning** (`core/reasoning.py`): Deductive, inductive, abductive, analogical.  
- **Rule engine**: Pattern matching, conflict resolution (separate from knowledge graph).  

**Lift value**: Reasoning and rules can drive “which engine to use” (e.g. REBOUND for N-body, RAMSES for MHD) and “which equations/constants to pass” (from our knowledge graph).

---

### 2.6 AI / Agents / LLM

- **LLM**: Config, provider (local, DeepSeek), router, manager (`ai/llm/`).  
- **Agents**: Base, gatekeeper, workhorse, orchestrator (`ai/agents/`).  
- **Evolution**: Proposals, validation, tracker (`ai/evolution/`).  
- **Rubric**: Quality gate, evaluator (`ai/rubric/`).  

**Lift value**: Orchestrator can choose “run REBOUND for this query” vs “run Astropy for this query”; quality gate can check outputs against our equation graph (e.g. energy conservation, units).

---

### 2.7 Frontend

- **Simulations**: `PhysicsCanvas`, `PendulumSimulation`, `SpringSimulation`, `ProjectileSimulation` (Matter.js / custom); `usePyodide` + worker for in-browser Python.  
- **Chat**: ChatInterface, MarkdownRenderer, QualityBadge, ReasoningFlowChart.  
- **Other**: Dashboard, Models, Evolution, Settings, layout, panels.  

**Lift value**: Same UI patterns can show “Orbital” or “N-body” scenarios driven by backend (or Pyodide) calling our models or REBOUND/pynbody; visualization of orbits/trajectories already exists for 2D.

---

## 3. What to Lift and Integrate (By External Tool)

### 3.1 REBOUND (N-body planetary dynamics)

| What we have | How to use it |
|--------------|----------------|
| **Orbital equation graph** (Kepler, vis-viva, Hohmann, Hill, Roche, etc.) | Use to **set initial conditions** (a, e, M, ω, Ω, i) and **validate** REBOUND outputs (energy, period, eccentricity). |
| **TwoBodyGravity** (2-body, reduced mass) | **Baseline**: Run our 2-body and REBOUND 2-body; compare energy/angular momentum. **Bridge**: Same μ = G(M+m); expose our `initial_conditions` ↔ REBOUND Cartesian/Kepler. |
| **AstroConstants** (G, au, M_sun, etc.) | Use as **default units** when building REBOUND sim (e.g. au, yr, M_sun). |
| **PhysicsModel** + `SimulationResult` | Add a **ReboundModel** (or **NBodyModel**) that (a) builds a REBOUND simulation from scenario + initial_conditions, (b) runs it, (c) maps outputs to `SimulationResult` and runs conservation checks using our orbital equations. |
| **Reasoner / tree index** | “N-body planetary” → select orbital + classical equations; suggest which bodies/parameters to pass to REBOUND. |

**Concrete lift**:  
- New module e.g. `physics/integration/rebound_bridge.py`: input (bodies, t_end, units) → output (trajectories, energy, L); optional wrapper implementing the same interface as `PhysicsModel.simulate`.  
- Wire `create_model('n_body_gravity', ...)` or `scenario.model = 'rebound'` in API to use this bridge.

---

### 3.2 RAMSES (Magneto-hydrodynamics)

| What we have | How to use it |
|--------------|----------------|
| **MHD equation graph** (mhd.py: momentum, Ohm, induction, Alfvén, β, Sweet–Parker, etc.) | **Documentation and validation**: Map RAMSES variables (ρ, v, B, p) to our nodes; use equations to explain outputs (e.g. Alfvén speed, plasma β). |
| **Plasma fundamentals** (Debye, plasma frequency) | Same: units, scaling, sanity checks. |
| **Stellar equations** (hydrostatic equilibrium, radiative transfer) | For stellar/structure problems that feed or post-process RAMSES (e.g. initial profiles). |
| **Reasoner** | “MHD problem” → retrieve MHD + fluids nodes; suggest initial conditions or dimensionless numbers (R_m, β). |

**Concrete lift**:  
- No need to run RAMSES inside Python necessarily; we can add a **RAMSES adapter** that (a) reads RAMSES output (or config), (b) computes derived quantities using our MHD/plasma equations and constants, (c) exposes them via the same API or dashboard.  
- Optionally: small “MHD scenario” type in the API that returns which equations and constants apply (for setting up or validating RAMSES runs).

---

### 3.3 pynbody (N-body simulations analysis)

| What we have | How to use it |
|--------------|----------------|
| **Orbital / gravitation equations** | **Validation**: From pynbody snapshots (positions, velocities, masses), compute E, L, a, e via our equations; compare with our knowledge graph. |
| **AstroConstants + units** | Convert pynbody units to SI or to our internal representation; use same G, M_sun, etc. |
| **Cosmology** (astro_solver) | If pynbody is used for cosmological boxes: redshift ↔ scale factor, distances (comoving, luminosity) via our Cosmology class. |
| **StellarPhysics** | If analyzing stellar/gas in snapshots: L(M), T(R), etc. for quick estimates. |

**Concrete lift**:  
- Module e.g. `physics/integration/pynbody_bridge.py`: load snapshot → extract m, r, v → compute orbital elements / energy / angular momentum using our orbital equations and constants; optionally compare with pynbody’s own analysis.  
- Reasoning: “Analyze this N-body snapshot” → suggest which equations (Kepler, virial, Jeans) to apply.

---

### 3.4 Astropy

| What we have | How to use it |
|--------------|----------------|
| **astro_solver** (SkyCoord, Cosmology, OrbitalMechanics, StellarPhysics) | **Already aligned**. Replace or wrap: (1) Use `astropy.coordinates.SkyCoord` and `astropy.coordinates` transforms instead of our custom ICRS↔Galactic. (2) Use `astropy.cosmology.FlatLambdaCDM` (and others) instead of our Cosmology class, keeping our equation graph for *explanation* and validation. (3) Use `astropy.units` throughout. |
| **Equation graph** (orbital, cosmology, stellar) | Keep as the **semantic layer**: which equations apply, derivation chain, LaTeX/SymPy; Astropy does the numerical work. |
| **Constants** | Align with `astropy.constants` (G, c, M_sun, etc.) and use them in our nodes and solvers. |

**Concrete lift**:  
- Add optional dependency `astropy`.  
- Refactor `astro_solver` to use `astropy.coordinates`, `astropy.cosmology`, `astropy.constants` where available; fallback to current implementation if not installed.  
- Document “Beyond Frontier equation graph + Astropy computation” as the supported path for coordinates/cosmology/orbits.

---

### 3.5 galpy (Orbital mechanics, potentials, DF)

| What we have | How to use it |
|--------------|----------------|
| **Orbital equations** (Kepler, vis-viva, Hohmann, Hill, etc.) | **Validation and interpretation**: galpy gives orbits in potentials; we use our equations to (a) set initial conditions (e.g. from a, e), (b) check consistency (e.g. E, L from our formulas vs galpy). |
| **TwoBodyGravity** | 2-body limit; same as REBOUND: compare or feed galpy. |
| **AstroConstants** | Units (e.g. kpc, km/s, G) for galpy’s unit system. |

**Concrete lift**:  
- **galpy bridge**: For “galactic orbit” scenario, (a) use our OrbitalMechanics / equation graph to get (a, e, E, L), (b) call galpy to integrate in a potential, (c) optionally compare energy conservation with our orbital_energy node.  
- Reasoner: “Galactic dynamics” → classical + orbital + (if we add) galactic potential nodes.

---

### 3.6 SunPy (Solar physics)

| What we have | How to use it |
|--------------|----------------|
| **SolarPhysics** (differential rotation, Carrington, B0, solar constant) | Already SunPy-inspired. **Integrate**: Use SunPy’s coordinate and time utilities where available; keep our equations for derivation/teaching. |
| **StellarPhysics** (Eddington, Wien, Planck) | Applicable to Sun; use for quick checks and explanations. |
| **MHD equations** | Solar corona/flares: Alfvén speed, Sweet–Parker, reconnection; use as semantic layer on top of SunPy data or models. |

**Concrete lift**:  
- Optional dependency `sunpy`; in `astro_solver` or a new `solar_solver`, call SunPy for Carrington/time/coordinates when available.  
- Add “solar” scenario type that returns relevant equations (SolarPhysics + MHD) and optionally runs SunPy-based computations.

---

## 4. Summary: Repo vs. Astrophysics Stack

| Area | In this repo | Integrate with |
|------|----------------|-----------------|
| **Orbital / 2-body** | Orbital equation graph, TwoBodyGravity, OrbitalMechanics in astro_solver | REBOUND (N-body), galpy (potentials), Astropy (coordinates/units) |
| **Stellar / solar** | Stellar + Solar equation nodes, StellarPhysics, SolarPhysics | SunPy (solar data/time), Astropy (units/constants) |
| **Cosmology** | Cosmology nodes, Cosmology class in astro_solver | Astropy cosmology, pynbody (redshift/box) |
| **MHD / plasma** | MHD equation graph, plasma fundamentals | RAMSES (validation/interpretation) |
| **N-body** | TwoBodyGravity only | REBOUND (run), pynbody (analyze) |
| **Knowledge layer** | Nodes, loader, relations, reasoner, tree index | All: drive configuration, validation, and explanation for external engines |

---

## 5. Suggested Implementation Order

1. **Wire existing models to API**: Connect `POST /api/v1/simulate` to `create_model` and existing `PhysicsModel.simulate` (harmonic_oscillator, pendulum, two_body_gravity, projectile_motion) so production path uses real ODEs and conservation checks.  
2. **Add optional Astropy**: Refactor `astro_solver` to use `astropy` where installed (coordinates, cosmology, constants); keep equation graph as semantic layer.  
3. **REBOUND bridge**: New `physics/integration/rebound_bridge.py` and optional `rebound` dependency; N-body scenario type in API; conservation validation from our orbital equations.  
4. **galpy bridge**: Optional `galpy`; “galactic orbit” scenario using our orbital equations + galpy potential integration.  
5. **pynbody bridge**: Load snapshots; compute E, L, orbital elements with our equations; optional comparison with pynbody.  
6. **RAMSES / MHD**: Adapter that takes RAMSES config or output and runs our MHD/plasma equations for validation and explanation.  
7. **SunPy**: Optional solar module using SunPy for time/coordinates; our SolarPhysics + MHD for semantics.

This keeps the repo’s identity (neurosymbolic, equation graph, validation) while making it a **single entry point** that can delegate to REBOUND, RAMSES, pynbody, Astropy, galpy, and SunPy and unify their use under one knowledge and reasoning layer.
