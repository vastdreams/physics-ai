"""
PATH: substrate/skills/physics_skills.py
PURPOSE: Core physics skills using the skill registry system

WHY: Provides discoverable, composable physics computations that leverage
     our solver modules (quantum, astro, optics) through a unified skill interface.

FLOW:
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│ Skill       │────>│ Solver       │────>│ Validated       │
│ Interface   │     │ Backend      │     │ Result          │
└─────────────┘     └──────────────┘     └─────────────────┘

DEPENDENCIES:
- physics.solvers: Backend computation modules
- skill_registry: Skill registration
"""

from typing import Dict, List, Tuple, Optional, Any
import numpy as np

from .skill_registry import skill, SkillDomain, SkillComplexity


# ============================================================================
# QUANTUM MECHANICS SKILLS
# ============================================================================

@skill(
    name="solve_schrodinger",
    description="Solve time-independent Schrodinger equation for arbitrary potential",
    domain=SkillDomain.QUANTUM,
    version="1.0.0",
    tags=["eigenvalue", "wavefunction", "energy-levels"],
    complexity=SkillComplexity.COMPLEX,
    equations=["Hψ = Eψ", "H = -ℏ²∇²/2m + V(x)"],
    assumptions=[
        "Single particle",
        "Time-independent potential",
        "Finite spatial domain with zero boundary conditions",
    ],
    limitations=[
        "Grid-based discretization limits resolution",
        "Numerical errors grow with grid size",
    ],
)
def solve_schrodinger(
    potential_func: callable,
    ndim: int = 1,
    grid_points: int = 256,
    extent: float = 20.0,
    n_states: int = 10,
    mass: float = 1.0,
) -> Dict[str, Any]:
    """
    Solve the time-independent Schrodinger equation.
    
    Args:
        potential_func: V(x) or V(x,y) or V(x,y,z) potential function
        ndim: Number of spatial dimensions (1, 2, or 3)
        grid_points: Number of grid points per dimension
        extent: Physical extent of domain in atomic units
        n_states: Number of eigenstates to compute
        mass: Particle mass in atomic units
        
    Returns:
        Dictionary with energies and wavefunctions
    """
    from physics.solvers.quantum_solver import QuantumGrid, Hamiltonian
    
    grid = QuantumGrid(ndim=ndim, N=grid_points, extent=extent)
    H = Hamiltonian(grid=grid, potential=potential_func, mass=mass)
    energies, states = H.solve_eigenstates(n_states=n_states)
    
    return {
        "energies": energies.tolist(),
        "states": states.tolist(),
        "grid": {
            "x": grid.x.tolist(),
            "dx": grid.dx,
            "extent": extent,
        },
        "units": "atomic_units",
    }


@skill(
    name="quantum_time_evolution",
    description="Evolve quantum state under time-dependent Schrodinger equation",
    domain=SkillDomain.QUANTUM,
    version="1.0.0",
    tags=["dynamics", "wavepacket", "propagation"],
    complexity=SkillComplexity.INTENSIVE,
    equations=["iℏ∂ψ/∂t = Hψ"],
    assumptions=[
        "Split-step Fourier method (separable H = T + V)",
        "Periodic boundary conditions",
    ],
)
def quantum_time_evolution(
    potential_func: callable,
    initial_state_func: callable,
    total_time: float,
    dt: float = 0.01,
    grid_points: int = 256,
    extent: float = 20.0,
    store_steps: int = 100,
) -> Dict[str, Any]:
    """
    Evolve wavefunction in time using split-step method.
    
    Args:
        potential_func: Potential energy function
        initial_state_func: Initial wavefunction psi(x)
        total_time: Total evolution time in atomic units
        dt: Time step
        grid_points: Grid resolution
        extent: Spatial extent
        store_steps: Number of snapshots to store
        
    Returns:
        Dictionary with times and wavefunctions
    """
    from physics.solvers.quantum_solver import (
        QuantumGrid, Hamiltonian, TimeEvolution, SolverMethod
    )
    
    grid = QuantumGrid(ndim=1, N=grid_points, extent=extent)
    H = Hamiltonian(grid=grid, potential=potential_func)
    
    # Create initial state
    psi0 = initial_state_func(grid.x)
    psi0 = psi0 / np.sqrt(np.sum(np.abs(psi0)**2) * grid.dx)  # Normalize
    
    # Evolve
    sim = TimeEvolution(H, method=SolverMethod.SPLIT_STEP)
    times, psi_t = sim.evolve(psi0, dt, total_time, store_steps)
    
    return {
        "times": times.tolist(),
        "states": [np.abs(psi)**2 for psi in psi_t],  # Probability densities
        "grid_x": grid.x.tolist(),
        "total_probability": [float(np.sum(np.abs(psi)**2) * grid.dx) for psi in psi_t],
    }


@skill(
    name="lindblad_evolution",
    description="Evolve open quantum system using Lindblad master equation",
    domain=SkillDomain.QUANTUM,
    version="1.0.0",
    tags=["decoherence", "dissipation", "density-matrix"],
    complexity=SkillComplexity.COMPLEX,
    equations=["dρ/dt = -i[H,ρ] + Σ γ(LρL† - ½{L†L,ρ})"],
    assumptions=[
        "Markovian dynamics (no memory effects)",
        "Weak system-bath coupling",
    ],
)
def lindblad_evolution(
    hamiltonian: np.ndarray,
    collapse_ops: List[Tuple[np.ndarray, float]],
    rho0: np.ndarray,
    times: np.ndarray,
) -> Dict[str, Any]:
    """
    Evolve density matrix under Lindblad equation.
    
    Args:
        hamiltonian: System Hamiltonian matrix
        collapse_ops: List of (operator, rate) tuples
        rho0: Initial density matrix
        times: Array of times to compute
        
    Returns:
        Dictionary with density matrices and observables
    """
    from physics.solvers.quantum_solver import OpenQuantumSystem
    
    system = OpenQuantumSystem(hamiltonian, collapse_ops)
    rho_t = system.evolve(rho0, times)
    
    # Compute observables
    populations = [np.diag(rho).real.tolist() for rho in rho_t]
    purity = [float(np.trace(rho @ rho).real) for rho in rho_t]
    
    return {
        "times": times.tolist(),
        "populations": populations,
        "purity": purity,
        "steady_state_purity": purity[-1] if len(purity) > 0 else None,
    }


# ============================================================================
# CLASSICAL MECHANICS SKILLS
# ============================================================================

@skill(
    name="solve_lagrangian",
    description="Solve equations of motion from Lagrangian mechanics",
    domain=SkillDomain.CLASSICAL,
    version="1.0.0",
    tags=["euler-lagrange", "generalized-coordinates", "dynamics"],
    complexity=SkillComplexity.MODERATE,
    equations=["d/dt(∂L/∂q̇) - ∂L/∂q = 0", "L = T - V"],
)
def solve_lagrangian(
    kinetic_func: callable,
    potential_func: callable,
    initial_q: List[float],
    initial_qdot: List[float],
    t_span: Tuple[float, float],
    t_eval: Optional[np.ndarray] = None,
) -> Dict[str, Any]:
    """
    Solve equations of motion from Lagrangian.
    
    Uses numerical differentiation to compute Euler-Lagrange equations.
    
    Args:
        kinetic_func: T(q, qdot) kinetic energy
        potential_func: V(q) potential energy
        initial_q: Initial generalized coordinates
        initial_qdot: Initial generalized velocities
        t_span: (t_start, t_end)
        t_eval: Times to evaluate solution
        
    Returns:
        Dictionary with trajectories
    """
    from scipy.integrate import solve_ivp
    from scipy.misc import derivative
    
    n_dof = len(initial_q)
    
    def equations(t, y):
        """Compute accelerations from Lagrangian."""
        q = y[:n_dof]
        qdot = y[n_dof:]
        
        # Numerical derivatives
        eps = 1e-8
        
        # ∂V/∂q
        dV_dq = np.zeros(n_dof)
        for i in range(n_dof):
            q_plus = q.copy()
            q_minus = q.copy()
            q_plus[i] += eps
            q_minus[i] -= eps
            dV_dq[i] = (potential_func(q_plus) - potential_func(q_minus)) / (2 * eps)
        
        # For simple T = (1/2)m*qdot^2, acceleration = -∂V/∂q / m
        # More general case requires ∂²T/∂qdot² (mass matrix)
        qddot = -dV_dq  # Assuming unit mass
        
        return np.concatenate([qdot, qddot])
    
    y0 = np.array(initial_q + initial_qdot)
    
    if t_eval is None:
        t_eval = np.linspace(t_span[0], t_span[1], 1000)
    
    sol = solve_ivp(equations, t_span, y0, t_eval=t_eval, method='RK45')
    
    return {
        "times": sol.t.tolist(),
        "coordinates": sol.y[:n_dof].tolist(),
        "velocities": sol.y[n_dof:].tolist(),
        "success": sol.success,
    }


@skill(
    name="orbital_mechanics",
    description="Compute orbital parameters and trajectories",
    domain=SkillDomain.CLASSICAL,
    version="1.0.0",
    tags=["kepler", "gravity", "two-body"],
    complexity=SkillComplexity.MODERATE,
    equations=[
        "T² = 4π²a³/GM",
        "v² = GM(2/r - 1/a)",
        "E = -GMm/2a",
    ],
)
def orbital_mechanics(
    semi_major_axis: float,
    eccentricity: float,
    central_mass: float,
    compute_trajectory: bool = False,
    n_points: int = 360,
) -> Dict[str, Any]:
    """
    Compute orbital mechanics parameters.
    
    Args:
        semi_major_axis: Semi-major axis in meters
        eccentricity: Orbital eccentricity (0 = circular)
        central_mass: Central body mass in kg
        compute_trajectory: Whether to compute full orbit
        n_points: Number of points for trajectory
        
    Returns:
        Dictionary with orbital parameters
    """
    from physics.solvers.astro_solver import OrbitalMechanics, AstroConstants
    
    G = AstroConstants.G
    a = semi_major_axis
    e = eccentricity
    M = central_mass
    
    # Orbital period
    period = OrbitalMechanics.kepler_period(a, M)
    
    # Perihelion and aphelion
    r_peri = a * (1 - e)
    r_apo = a * (1 + e)
    
    # Velocities at perihelion and aphelion
    v_peri = OrbitalMechanics.vis_viva(r_peri, a, M)
    v_apo = OrbitalMechanics.vis_viva(r_apo, a, M)
    
    # Specific orbital energy
    energy = -G * M / (2 * a)
    
    result = {
        "period_seconds": period,
        "period_days": period / 86400,
        "semi_major_axis_m": a,
        "eccentricity": e,
        "perihelion_m": r_peri,
        "aphelion_m": r_apo,
        "velocity_perihelion_m_s": v_peri,
        "velocity_aphelion_m_s": v_apo,
        "specific_energy_J_kg": energy,
    }
    
    if compute_trajectory:
        # Compute trajectory using true anomaly
        theta = np.linspace(0, 2 * np.pi, n_points)
        r = a * (1 - e**2) / (1 + e * np.cos(theta))
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        result["trajectory"] = {"x": x.tolist(), "y": y.tolist()}
    
    return result


# ============================================================================
# ASTROPHYSICS SKILLS
# ============================================================================

@skill(
    name="cosmological_distance",
    description="Calculate cosmological distances using ΛCDM model",
    domain=SkillDomain.ASTROPHYSICS,
    version="1.0.0",
    tags=["cosmology", "redshift", "hubble"],
    complexity=SkillComplexity.MODERATE,
    equations=[
        "D_C = c/H₀ ∫dz/E(z)",
        "E(z) = √(Ωm(1+z)³ + ΩΛ)",
    ],
    assumptions=["Flat ΛCDM cosmology", "No radiation contribution"],
)
def cosmological_distance(
    redshift: float,
    cosmology: str = "Planck18",
) -> Dict[str, Any]:
    """
    Calculate cosmological distances to a given redshift.
    
    Args:
        redshift: Cosmological redshift z
        cosmology: Cosmology model ("Planck18" or "WMAP9")
        
    Returns:
        Dictionary with various distance measures
    """
    from physics.solvers.astro_solver import Planck18, WMAP9
    
    cosmo = Planck18 if cosmology == "Planck18" else WMAP9
    
    return {
        "redshift": redshift,
        "cosmology": cosmology,
        "comoving_distance_Mpc": cosmo.comoving_distance(redshift),
        "luminosity_distance_Mpc": cosmo.luminosity_distance(redshift),
        "angular_diameter_distance_Mpc": cosmo.angular_diameter_distance(redshift),
        "distance_modulus": cosmo.distance_modulus(redshift),
        "lookback_time_Gyr": cosmo.lookback_time(redshift),
        "hubble_parameter_km_s_Mpc": cosmo.H(redshift),
    }


@skill(
    name="stellar_evolution",
    description="Estimate stellar properties from mass",
    domain=SkillDomain.ASTROPHYSICS,
    version="1.0.0",
    tags=["stars", "luminosity", "lifetime"],
    complexity=SkillComplexity.SIMPLE,
    equations=[
        "L ∝ M^3.5 (main sequence)",
        "τ ∝ M/L ∝ M^-2.5",
    ],
    assumptions=[
        "Main sequence star",
        "Solar metallicity",
    ],
)
def stellar_evolution(mass_solar: float) -> Dict[str, Any]:
    """
    Estimate stellar properties for main sequence star.
    
    Args:
        mass_solar: Stellar mass in solar masses
        
    Returns:
        Dictionary with stellar parameters
    """
    from physics.solvers.astro_solver import StellarPhysics, AstroConstants
    
    # Mass-luminosity relation
    luminosity_solar = StellarPhysics.main_sequence_luminosity(mass_solar)
    
    # Main sequence lifetime
    lifetime_gyr = StellarPhysics.main_sequence_lifetime(mass_solar)
    
    # Eddington luminosity
    eddington_solar = StellarPhysics.eddington_luminosity(mass_solar)
    
    # Estimate temperature using L ∝ R²T⁴ and R ∝ M^0.8
    radius_solar = mass_solar**0.8
    temperature_K = AstroConstants.T_sun * (luminosity_solar / radius_solar**2)**0.25
    
    # Peak wavelength
    peak_wavelength_nm = StellarPhysics.wien_peak_wavelength(temperature_K) * 1e9
    
    return {
        "mass_solar": mass_solar,
        "luminosity_solar": luminosity_solar,
        "radius_solar": radius_solar,
        "temperature_K": temperature_K,
        "main_sequence_lifetime_Gyr": lifetime_gyr,
        "eddington_luminosity_solar": eddington_solar,
        "peak_wavelength_nm": peak_wavelength_nm,
        "spectral_class": _estimate_spectral_class(temperature_K),
    }


def _estimate_spectral_class(temperature: float) -> str:
    """Estimate spectral class from temperature."""
    if temperature > 30000:
        return "O"
    elif temperature > 10000:
        return "B"
    elif temperature > 7500:
        return "A"
    elif temperature > 6000:
        return "F"
    elif temperature > 5200:
        return "G"
    elif temperature > 3700:
        return "K"
    else:
        return "M"


# ============================================================================
# OPTICS SKILLS
# ============================================================================

@skill(
    name="diffraction_pattern",
    description="Calculate analytical diffraction patterns",
    domain=SkillDomain.OPTICS,
    version="1.0.0",
    tags=["wave-optics", "interference", "fourier"],
    complexity=SkillComplexity.SIMPLE,
    equations=[
        "I_airy = (2J₁(x)/x)²",
        "I_slit = sinc²(πa·sinθ/λ)",
    ],
)
def diffraction_pattern(
    pattern_type: str,
    wavelength: float,
    aperture_size: float,
    angles_deg: Optional[List[float]] = None,
    slit_separation: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Calculate diffraction pattern for various apertures.
    
    Args:
        pattern_type: "airy", "single_slit", or "double_slit"
        wavelength: Wavelength in meters
        aperture_size: Aperture diameter or slit width in meters
        angles_deg: Angles to compute (optional)
        slit_separation: For double slit, separation in meters
        
    Returns:
        Dictionary with intensity pattern
    """
    from physics.solvers.optics_solver import AnalyticalDiffraction
    
    if angles_deg is None:
        angles_deg = np.linspace(-5, 5, 1000)
    
    angles_rad = np.radians(angles_deg)
    
    if pattern_type == "airy":
        intensity = AnalyticalDiffraction.airy_pattern(angles_rad, aperture_size, wavelength)
        rayleigh_deg = np.degrees(AnalyticalDiffraction.rayleigh_criterion(wavelength, aperture_size))
        extra = {"rayleigh_criterion_deg": rayleigh_deg}
        
    elif pattern_type == "single_slit":
        beta = np.pi * aperture_size * np.sin(angles_rad) / wavelength
        intensity = np.sinc(beta / np.pi)**2
        extra = {"first_minimum_deg": np.degrees(np.arcsin(wavelength / aperture_size))}
        
    elif pattern_type == "double_slit":
        if slit_separation is None:
            slit_separation = 5 * aperture_size  # Default
        intensity = AnalyticalDiffraction.double_slit_pattern(
            angles_rad, slit_separation, aperture_size, wavelength
        )
        fringe_spacing_deg = np.degrees(np.arcsin(wavelength / slit_separation))
        extra = {"fringe_spacing_deg": fringe_spacing_deg}
    else:
        raise ValueError(f"Unknown pattern type: {pattern_type}")
    
    return {
        "pattern_type": pattern_type,
        "wavelength_m": wavelength,
        "aperture_size_m": aperture_size,
        "angles_deg": angles_deg.tolist() if hasattr(angles_deg, 'tolist') else list(angles_deg),
        "intensity": intensity.tolist(),
        **extra,
    }


@skill(
    name="optical_system_psf",
    description="Compute Point Spread Function for optical system",
    domain=SkillDomain.OPTICS,
    version="1.0.0",
    tags=["psf", "imaging", "aberrations", "zernike"],
    complexity=SkillComplexity.COMPLEX,
    equations=["PSF = |FT{pupil × exp(iφ)}|²"],
    assumptions=["Scalar diffraction theory", "Monochromatic light"],
)
def optical_system_psf(
    diameter: float,
    wavelength: float,
    zernike_coeffs: Optional[Dict[int, float]] = None,
    npix: int = 256,
    obscuration_ratio: float = 0.0,
) -> Dict[str, Any]:
    """
    Compute PSF for optical system with aberrations.
    
    Args:
        diameter: Aperture diameter in meters
        wavelength: Wavelength in meters
        zernike_coeffs: Zernike aberration coefficients (Noll index -> waves)
        npix: Output array size
        obscuration_ratio: Central obscuration ratio (0-1)
        
    Returns:
        Dictionary with PSF and metrics
    """
    from physics.solvers.optics_solver import (
        OpticalSystem, CircularAperture, AnnularAperture,
        ZernikeWFE, AnalyticalDiffraction
    )
    
    pupil_pixelscale = diameter * 2 / npix
    
    system = OpticalSystem(
        wavelength=wavelength,
        npix=npix,
        pixelscale=pupil_pixelscale
    )
    
    # Add aperture
    if obscuration_ratio > 0:
        system.add_optic(AnnularAperture(
            outer_radius=diameter/2,
            inner_radius=diameter/2 * obscuration_ratio
        ))
    else:
        system.add_optic(CircularAperture(radius=diameter/2))
    
    # Add aberrations
    if zernike_coeffs:
        system.add_optic(ZernikeWFE(radius=diameter/2, coefficients=zernike_coeffs))
    
    psf = system.calc_psf()
    
    # Compute metrics
    airy_radius = AnalyticalDiffraction.airy_radius(wavelength, diameter, focal_length=1.0)
    strehl_ratio = psf.max() / (1.0 / psf.size)  # Approximate Strehl
    
    return {
        "psf": psf.tolist(),
        "psf_max": float(psf.max()),
        "strehl_ratio_approx": float(strehl_ratio),
        "airy_radius_rad": airy_radius,
        "wavelength_m": wavelength,
        "diameter_m": diameter,
        "zernike_coeffs": zernike_coeffs,
    }


# ============================================================================
# ELECTROMAGNETISM SKILLS
# ============================================================================

@skill(
    name="maxwell_solver",
    description="Solve Maxwell's equations for simple geometries",
    domain=SkillDomain.ELECTROMAGNETISM,
    version="1.0.0",
    tags=["electromagnetic", "field", "boundary-conditions"],
    complexity=SkillComplexity.MODERATE,
    equations=[
        "∇·E = ρ/ε₀",
        "∇×B = μ₀J + μ₀ε₀∂E/∂t",
    ],
)
def maxwell_solver(
    geometry: str,
    parameters: Dict[str, float],
) -> Dict[str, Any]:
    """
    Solve Maxwell's equations for standard geometries.
    
    Args:
        geometry: "point_charge", "line_charge", "plane_wave", "dipole"
        parameters: Geometry-specific parameters
        
    Returns:
        Field solutions at specified points
    """
    import numpy as np
    
    epsilon_0 = 8.854187817e-12  # F/m
    mu_0 = 4 * np.pi * 1e-7  # H/m
    c = 1 / np.sqrt(epsilon_0 * mu_0)
    
    if geometry == "point_charge":
        Q = parameters.get("charge", 1e-9)  # Coulombs
        r = np.array(parameters.get("position", [0.1, 0, 0]))  # meters
        r_mag = np.linalg.norm(r)
        
        # Coulomb field
        E_mag = Q / (4 * np.pi * epsilon_0 * r_mag**2)
        E = E_mag * r / r_mag
        
        return {
            "geometry": geometry,
            "E_field_V_m": E.tolist(),
            "E_magnitude_V_m": float(E_mag),
            "potential_V": float(Q / (4 * np.pi * epsilon_0 * r_mag)),
        }
    
    elif geometry == "plane_wave":
        E0 = parameters.get("amplitude", 1.0)  # V/m
        omega = parameters.get("frequency", 1e9) * 2 * np.pi  # rad/s
        k = omega / c  # wavenumber
        z = parameters.get("z", 0)  # position
        t = parameters.get("t", 0)  # time
        
        E_x = E0 * np.cos(k * z - omega * t)
        B_y = E0 / c * np.cos(k * z - omega * t)
        
        return {
            "geometry": geometry,
            "E_x_V_m": float(E_x),
            "B_y_T": float(B_y),
            "wavelength_m": 2 * np.pi / k,
            "phase_velocity_m_s": float(c),
            "poynting_W_m2": float(E_x * B_y / mu_0),
        }
    
    else:
        raise ValueError(f"Unknown geometry: {geometry}")


# ============================================================================
# THERMODYNAMICS SKILLS
# ============================================================================

@skill(
    name="thermodynamic_process",
    description="Analyze thermodynamic processes for ideal gas",
    domain=SkillDomain.THERMODYNAMICS,
    version="1.0.0",
    tags=["heat", "work", "entropy", "ideal-gas"],
    complexity=SkillComplexity.SIMPLE,
    equations=[
        "PV = nRT",
        "ΔU = Q - W",
        "W = ∫PdV",
    ],
    assumptions=["Ideal gas behavior", "Quasi-static process"],
)
def thermodynamic_process(
    process_type: str,
    initial_state: Dict[str, float],
    final_parameter: Dict[str, float],
    n_moles: float = 1.0,
    gamma: float = 1.4,
) -> Dict[str, Any]:
    """
    Analyze thermodynamic process.
    
    Args:
        process_type: "isothermal", "isobaric", "isochoric", "adiabatic"
        initial_state: {P: Pa, V: m³, T: K} (any two)
        final_parameter: Final condition (depends on process)
        n_moles: Number of moles
        gamma: Heat capacity ratio (Cp/Cv)
        
    Returns:
        Dictionary with work, heat, entropy change
    """
    R = 8.314  # J/(mol·K)
    
    # Get initial state
    P1 = initial_state.get("P")
    V1 = initial_state.get("V")
    T1 = initial_state.get("T")
    
    # Complete initial state using PV = nRT
    if P1 is None:
        P1 = n_moles * R * T1 / V1
    elif V1 is None:
        V1 = n_moles * R * T1 / P1
    elif T1 is None:
        T1 = P1 * V1 / (n_moles * R)
    
    Cv = R / (gamma - 1) * n_moles
    
    if process_type == "isothermal":
        T2 = T1
        V2 = final_parameter.get("V", V1 * 2)
        P2 = n_moles * R * T2 / V2
        W = n_moles * R * T1 * np.log(V2 / V1)
        Q = W  # ΔU = 0
        delta_S = n_moles * R * np.log(V2 / V1)
        
    elif process_type == "isobaric":
        P2 = P1
        T2 = final_parameter.get("T", T1 * 2)
        V2 = n_moles * R * T2 / P2
        W = P1 * (V2 - V1)
        Q = n_moles * gamma * R / (gamma - 1) * (T2 - T1)  # Cp * ΔT
        delta_S = n_moles * gamma * R / (gamma - 1) * np.log(T2 / T1)
        
    elif process_type == "isochoric":
        V2 = V1
        T2 = final_parameter.get("T", T1 * 2)
        P2 = n_moles * R * T2 / V2
        W = 0
        Q = Cv * (T2 - T1)
        delta_S = Cv * np.log(T2 / T1)
        
    elif process_type == "adiabatic":
        Q = 0
        V2 = final_parameter.get("V", V1 * 2)
        T2 = T1 * (V1 / V2)**(gamma - 1)
        P2 = P1 * (V1 / V2)**gamma
        W = Cv * (T1 - T2)  # -ΔU since Q = 0
        delta_S = 0  # Reversible adiabatic
        
    else:
        raise ValueError(f"Unknown process: {process_type}")
    
    return {
        "process": process_type,
        "initial": {"P_Pa": P1, "V_m3": V1, "T_K": T1},
        "final": {"P_Pa": P2, "V_m3": V2, "T_K": T2},
        "work_J": float(W),
        "heat_J": float(Q),
        "entropy_change_J_K": float(delta_S),
        "internal_energy_change_J": float(Q - W),
    }
