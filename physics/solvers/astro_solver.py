"""
PATH: physics/solvers/astro_solver.py
PURPOSE: Astrophysics and cosmology computations integrating AstroPy concepts

WHY: Provides coordinate transformations, cosmological calculations, and
     astronomical unit conversions using algorithms from AstroPy.

REFERENCES:
- AstroPy: https://github.com/astropy/astropy (BSD-3)
- SunPy: https://github.com/sunpy/sunpy (BSD-2)

FLOW:
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│ Define      │────>│ Transform    │────>│ Compute         │
│ Coordinates │     │ Systems      │     │ Physical Params │
└─────────────┘     └──────────────┘     └─────────────────┘

DEPENDENCIES:
- numpy: Numerical computations
- scipy: Integration, interpolation
"""

from typing import Tuple, Optional, Dict, Any, List, Union
from dataclasses import dataclass
from enum import Enum
import numpy as np
from scipy.integrate import quad, odeint
from scipy.interpolate import interp1d
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# PHYSICAL CONSTANTS (CODATA 2022 values, like AstroPy)
# ============================================================================

class AstroConstants:
    """Astronomical and physical constants."""
    
    # Fundamental
    c = 299792458.0  # Speed of light [m/s]
    G = 6.67430e-11  # Gravitational constant [m³/(kg⋅s²)]
    h = 6.62607015e-34  # Planck constant [J⋅s]
    hbar = 1.054571817e-34  # Reduced Planck constant [J⋅s]
    k_B = 1.380649e-23  # Boltzmann constant [J/K]
    sigma_sb = 5.670374419e-8  # Stefan-Boltzmann constant [W/(m²⋅K⁴)]
    
    # Astronomical
    au = 1.495978707e11  # Astronomical unit [m]
    pc = 3.0856775814913673e16  # Parsec [m]
    ly = 9.4607304725808e15  # Light-year [m]
    
    # Solar
    M_sun = 1.98841e30  # Solar mass [kg]
    R_sun = 6.957e8  # Solar radius [m]
    L_sun = 3.828e26  # Solar luminosity [W]
    T_sun = 5772  # Solar effective temperature [K]
    
    # Earth
    M_earth = 5.9722e24  # Earth mass [kg]
    R_earth = 6.371e6  # Earth mean radius [m]
    
    # Cosmological
    H_0 = 70.0  # Hubble constant [km/s/Mpc] (approximate)
    T_cmb = 2.7255  # CMB temperature [K]


# ============================================================================
# COORDINATE SYSTEMS (Inspired by AstroPy coordinates)
# ============================================================================

class CoordinateFrame(Enum):
    """Supported coordinate frames."""
    ICRS = "icrs"  # International Celestial Reference System
    GALACTIC = "galactic"
    ECLIPTIC = "ecliptic"
    ALTAZ = "altaz"  # Horizontal (altitude-azimuth)
    HELIOCENTRIC = "heliocentric"


@dataclass
class SkyCoord:
    """
    Sky coordinate representation.
    
    Inspired by AstroPy's SkyCoord class.
    """
    lon: float  # Longitude/RA in degrees
    lat: float  # Latitude/Dec in degrees
    distance: Optional[float] = None  # Distance in parsec
    frame: CoordinateFrame = CoordinateFrame.ICRS
    
    @property
    def lon_rad(self) -> float:
        """Longitude in radians."""
        return np.radians(self.lon)
    
    @property
    def lat_rad(self) -> float:
        """Latitude in radians."""
        return np.radians(self.lat)
    
    def to_cartesian(self) -> Tuple[float, float, float]:
        """Convert to Cartesian coordinates."""
        r = self.distance if self.distance else 1.0
        x = r * np.cos(self.lat_rad) * np.cos(self.lon_rad)
        y = r * np.cos(self.lat_rad) * np.sin(self.lon_rad)
        z = r * np.sin(self.lat_rad)
        return x, y, z
    
    def transform_to(self, target_frame: CoordinateFrame) -> 'SkyCoord':
        """Transform to different coordinate frame."""
        if self.frame == target_frame:
            return self
        
        if self.frame == CoordinateFrame.ICRS and target_frame == CoordinateFrame.GALACTIC:
            return self._icrs_to_galactic()
        elif self.frame == CoordinateFrame.GALACTIC and target_frame == CoordinateFrame.ICRS:
            return self._galactic_to_icrs()
        else:
            raise NotImplementedError(f"Transform {self.frame} -> {target_frame} not implemented")
    
    def _icrs_to_galactic(self) -> 'SkyCoord':
        """Convert ICRS (RA, Dec) to Galactic (l, b)."""
        # Galactic pole in ICRS
        ra_ngp = np.radians(192.85948)  # RA of North Galactic Pole
        dec_ngp = np.radians(27.12825)  # Dec of North Galactic Pole
        l_ncp = np.radians(122.93192)   # Galactic longitude of North Celestial Pole
        
        ra = self.lon_rad
        dec = self.lat_rad
        
        # Spherical trigonometry transformations
        sin_b = np.sin(dec_ngp) * np.sin(dec) + np.cos(dec_ngp) * np.cos(dec) * np.cos(ra - ra_ngp)
        b = np.arcsin(sin_b)
        
        y = np.cos(dec) * np.sin(ra - ra_ngp)
        x = np.cos(dec_ngp) * np.sin(dec) - np.sin(dec_ngp) * np.cos(dec) * np.cos(ra - ra_ngp)
        l = l_ncp - np.arctan2(y, x)
        
        # Normalize to [0, 360)
        l = np.degrees(l) % 360
        b = np.degrees(b)
        
        return SkyCoord(lon=l, lat=b, distance=self.distance, frame=CoordinateFrame.GALACTIC)
    
    def _galactic_to_icrs(self) -> 'SkyCoord':
        """Convert Galactic (l, b) to ICRS (RA, Dec)."""
        # Inverse transformation
        ra_ngp = np.radians(192.85948)
        dec_ngp = np.radians(27.12825)
        l_ncp = np.radians(122.93192)
        
        l = self.lon_rad
        b = self.lat_rad
        
        sin_dec = np.sin(dec_ngp) * np.sin(b) + np.cos(dec_ngp) * np.cos(b) * np.cos(l_ncp - l)
        dec = np.arcsin(sin_dec)
        
        y = np.cos(b) * np.sin(l_ncp - l)
        x = np.cos(dec_ngp) * np.sin(b) - np.sin(dec_ngp) * np.cos(b) * np.cos(l_ncp - l)
        ra = ra_ngp + np.arctan2(y, x)
        
        ra = np.degrees(ra) % 360
        dec = np.degrees(dec)
        
        return SkyCoord(lon=ra, lat=dec, distance=self.distance, frame=CoordinateFrame.ICRS)
    
    def separation(self, other: 'SkyCoord') -> float:
        """
        Angular separation from another coordinate (in degrees).
        
        Uses Vincenty formula for accuracy at small separations.
        """
        # Ensure same frame
        if other.frame != self.frame:
            other = other.transform_to(self.frame)
        
        lat1, lon1 = self.lat_rad, self.lon_rad
        lat2, lon2 = other.lat_rad, other.lon_rad
        
        dlon = lon2 - lon1
        
        # Vincenty formula
        num = np.sqrt(
            (np.cos(lat2) * np.sin(dlon))**2 +
            (np.cos(lat1) * np.sin(lat2) - np.sin(lat1) * np.cos(lat2) * np.cos(dlon))**2
        )
        denom = np.sin(lat1) * np.sin(lat2) + np.cos(lat1) * np.cos(lat2) * np.cos(dlon)
        
        return np.degrees(np.arctan2(num, denom))


# ============================================================================
# COSMOLOGY (Inspired by AstroPy cosmology module)
# ============================================================================

@dataclass
class Cosmology:
    """
    Cosmological model for distance and time calculations.
    
    Implements ΛCDM model like AstroPy's FlatLambdaCDM.
    """
    H0: float = 70.0  # Hubble constant [km/s/Mpc]
    Om0: float = 0.3  # Matter density parameter
    Ode0: float = 0.7  # Dark energy density parameter
    Ob0: float = 0.05  # Baryon density parameter
    Tcmb0: float = 2.7255  # CMB temperature today [K]
    
    def __post_init__(self):
        """Compute derived quantities."""
        self.Ok0 = 1.0 - self.Om0 - self.Ode0  # Curvature
        self.h = self.H0 / 100.0
        self.H0_si = self.H0 * 1000 / (AstroConstants.pc * 1e6)  # SI units [s⁻¹]
    
    def _E(self, z: float) -> float:
        """
        Dimensionless Hubble parameter E(z) = H(z)/H0.
        
        E(z) = sqrt(Ωm(1+z)³ + Ωk(1+z)² + ΩΛ)
        """
        return np.sqrt(
            self.Om0 * (1 + z)**3 +
            self.Ok0 * (1 + z)**2 +
            self.Ode0
        )
    
    def H(self, z: float) -> float:
        """Hubble parameter H(z) in km/s/Mpc."""
        return self.H0 * self._E(z)
    
    def comoving_distance(self, z: float) -> float:
        """
        Comoving distance to redshift z in Mpc.
        
        D_C = c/H0 * ∫₀ᶻ dz'/E(z')
        """
        c_H0 = AstroConstants.c / 1000 / self.H0  # Hubble distance in Mpc
        
        result, _ = quad(lambda zp: 1.0 / self._E(zp), 0, z)
        return c_H0 * result
    
    def luminosity_distance(self, z: float) -> float:
        """Luminosity distance in Mpc: D_L = (1+z) * D_C."""
        return (1 + z) * self.comoving_distance(z)
    
    def angular_diameter_distance(self, z: float) -> float:
        """Angular diameter distance in Mpc: D_A = D_C / (1+z)."""
        return self.comoving_distance(z) / (1 + z)
    
    def lookback_time(self, z: float) -> float:
        """
        Lookback time to redshift z in Gyr.
        
        t_L = 1/H0 * ∫₀ᶻ dz' / [(1+z')E(z')]
        """
        H0_inv_Gyr = 1 / self.H0_si / (3600 * 24 * 365.25 * 1e9)  # 1/H0 in Gyr
        
        result, _ = quad(lambda zp: 1.0 / ((1 + zp) * self._E(zp)), 0, z)
        return H0_inv_Gyr * result
    
    def age(self, z: float = 0) -> float:
        """Age of universe at redshift z in Gyr."""
        # Integrate from z to infinity
        H0_inv_Gyr = 1 / self.H0_si / (3600 * 24 * 365.25 * 1e9)
        
        result, _ = quad(lambda zp: 1.0 / ((1 + zp) * self._E(zp)), z, np.inf)
        return H0_inv_Gyr * result
    
    def critical_density(self, z: float = 0) -> float:
        """Critical density at redshift z in kg/m³."""
        H_z = self.H(z) * 1000 / (AstroConstants.pc * 1e6)  # SI
        return 3 * H_z**2 / (8 * np.pi * AstroConstants.G)
    
    def distance_modulus(self, z: float) -> float:
        """Distance modulus μ = 5*log10(D_L/10pc)."""
        D_L_pc = self.luminosity_distance(z) * 1e6  # Mpc to pc
        return 5 * np.log10(D_L_pc / 10)


# ============================================================================
# STELLAR PHYSICS (Inspired by SunPy for solar and stellar computations)
# ============================================================================

class StellarPhysics:
    """
    Stellar physics calculations.
    
    Implements common stellar relations and solar physics computations.
    """
    
    @staticmethod
    def stefan_boltzmann_luminosity(radius: float, temperature: float) -> float:
        """
        Calculate luminosity from Stefan-Boltzmann law.
        
        L = 4πR²σT⁴
        
        Args:
            radius: Stellar radius in meters
            temperature: Effective temperature in Kelvin
            
        Returns:
            Luminosity in Watts
        """
        return 4 * np.pi * radius**2 * AstroConstants.sigma_sb * temperature**4
    
    @staticmethod
    def main_sequence_luminosity(mass: float) -> float:
        """
        Estimate luminosity from mass using mass-luminosity relation.
        
        L/L_sun ≈ (M/M_sun)^3.5 for main sequence stars
        
        Args:
            mass: Stellar mass in solar masses
            
        Returns:
            Luminosity in solar luminosities
        """
        return mass**3.5
    
    @staticmethod
    def main_sequence_lifetime(mass: float) -> float:
        """
        Estimate main sequence lifetime.
        
        τ ≈ (M/L) * τ_sun ≈ M^(-2.5) * 10 Gyr
        
        Args:
            mass: Stellar mass in solar masses
            
        Returns:
            Lifetime in Gyr
        """
        return 10.0 * mass**(-2.5)
    
    @staticmethod
    def schwarzschild_radius(mass: float) -> float:
        """
        Schwarzschild radius: r_s = 2GM/c²
        
        Args:
            mass: Mass in kg
            
        Returns:
            Schwarzschild radius in meters
        """
        return 2 * AstroConstants.G * mass / AstroConstants.c**2
    
    @staticmethod
    def eddington_luminosity(mass: float) -> float:
        """
        Eddington luminosity limit.
        
        L_Edd = 4πGMm_p c / σ_T
        
        Args:
            mass: Mass in solar masses
            
        Returns:
            Eddington luminosity in solar luminosities
        """
        m_p = 1.67262192369e-27  # Proton mass [kg]
        sigma_T = 6.6524587321e-29  # Thomson cross-section [m²]
        
        L_Edd = 4 * np.pi * AstroConstants.G * (mass * AstroConstants.M_sun) * m_p * AstroConstants.c / sigma_T
        return L_Edd / AstroConstants.L_sun
    
    @staticmethod
    def wien_peak_wavelength(temperature: float) -> float:
        """
        Wien's displacement law: λ_max * T = b
        
        Args:
            temperature: Temperature in Kelvin
            
        Returns:
            Peak wavelength in meters
        """
        b = 2.897771955e-3  # Wien displacement constant [m⋅K]
        return b / temperature
    
    @staticmethod
    def planck_spectrum(wavelength: np.ndarray, temperature: float) -> np.ndarray:
        """
        Planck blackbody spectrum.
        
        B_λ(T) = (2hc²/λ⁵) / (exp(hc/λkT) - 1)
        
        Args:
            wavelength: Wavelength array in meters
            temperature: Temperature in Kelvin
            
        Returns:
            Spectral radiance in W/(m²⋅sr⋅m)
        """
        h, c, k = AstroConstants.h, AstroConstants.c, AstroConstants.k_B
        
        x = h * c / (wavelength * k * temperature)
        # Handle overflow
        x = np.clip(x, 0, 700)
        
        return (2 * h * c**2 / wavelength**5) / (np.exp(x) - 1)


# ============================================================================
# SOLAR PHYSICS (Inspired by SunPy)
# ============================================================================

class SolarPhysics:
    """
    Solar-specific physics calculations.
    
    Inspired by SunPy's solar physics functionality.
    """
    
    # Solar differential rotation parameters (sidereal)
    A = 14.713  # deg/day
    B = -2.396  # deg/day
    C = -1.787  # deg/day
    
    @classmethod
    def differential_rotation_rate(cls, latitude: float) -> float:
        """
        Solar differential rotation rate.
        
        ω(θ) = A + B*sin²(θ) + C*sin⁴(θ)
        
        Args:
            latitude: Heliographic latitude in degrees
            
        Returns:
            Rotation rate in degrees per day
        """
        sin_lat = np.sin(np.radians(latitude))
        return cls.A + cls.B * sin_lat**2 + cls.C * sin_lat**4
    
    @staticmethod
    def carrington_rotation_number(jd: float) -> float:
        """
        Calculate Carrington rotation number from Julian Date.
        
        Args:
            jd: Julian Date
            
        Returns:
            Carrington rotation number
        """
        # Carrington rotation 1 started at JD 2398167.4
        jd_cr1 = 2398167.4
        carrington_period = 27.2753  # days
        
        return 1 + (jd - jd_cr1) / carrington_period
    
    @staticmethod
    def solar_b0_angle(day_of_year: int) -> float:
        """
        Approximate solar B0 angle (tilt of solar rotation axis toward Earth).
        
        Args:
            day_of_year: Day of year (1-365)
            
        Returns:
            B0 angle in degrees
        """
        # Simplified formula
        return 7.25 * np.sin(np.radians((day_of_year - 80) * 360 / 365))
    
    @staticmethod
    def solar_constant(distance_au: float = 1.0) -> float:
        """
        Solar irradiance at given distance.
        
        Args:
            distance_au: Distance from Sun in AU
            
        Returns:
            Irradiance in W/m²
        """
        S_0 = 1361  # Solar constant at 1 AU [W/m²]
        return S_0 / distance_au**2


# ============================================================================
# ORBITAL MECHANICS
# ============================================================================

class OrbitalMechanics:
    """
    Orbital mechanics calculations.
    """
    
    @staticmethod
    def kepler_period(semi_major_axis: float, central_mass: float) -> float:
        """
        Kepler's third law: T² = (4π²/GM) * a³
        
        Args:
            semi_major_axis: Semi-major axis in meters
            central_mass: Central body mass in kg
            
        Returns:
            Orbital period in seconds
        """
        return 2 * np.pi * np.sqrt(semi_major_axis**3 / (AstroConstants.G * central_mass))
    
    @staticmethod
    def orbital_velocity(radius: float, central_mass: float) -> float:
        """
        Circular orbital velocity: v = √(GM/r)
        
        Args:
            radius: Orbital radius in meters
            central_mass: Central body mass in kg
            
        Returns:
            Orbital velocity in m/s
        """
        return np.sqrt(AstroConstants.G * central_mass / radius)
    
    @staticmethod
    def escape_velocity(radius: float, mass: float) -> float:
        """
        Escape velocity: v_esc = √(2GM/r)
        
        Args:
            radius: Distance from center in meters
            mass: Body mass in kg
            
        Returns:
            Escape velocity in m/s
        """
        return np.sqrt(2 * AstroConstants.G * mass / radius)
    
    @staticmethod
    def hill_sphere(semi_major_axis: float, mass_ratio: float) -> float:
        """
        Hill sphere radius: r_H ≈ a * (m/3M)^(1/3)
        
        Args:
            semi_major_axis: Orbital semi-major axis in meters
            mass_ratio: m/M (orbiting body / central body)
            
        Returns:
            Hill sphere radius in meters
        """
        return semi_major_axis * (mass_ratio / 3)**(1/3)
    
    @staticmethod
    def vis_viva(radius: float, semi_major_axis: float, central_mass: float) -> float:
        """
        Vis-viva equation: v² = GM(2/r - 1/a)
        
        Args:
            radius: Current distance in meters
            semi_major_axis: Semi-major axis in meters
            central_mass: Central body mass in kg
            
        Returns:
            Orbital speed in m/s
        """
        GM = AstroConstants.G * central_mass
        return np.sqrt(GM * (2/radius - 1/semi_major_axis))
    
    @staticmethod
    def hohmann_transfer_dv(r1: float, r2: float, central_mass: float) -> Tuple[float, float]:
        """
        Delta-v for Hohmann transfer orbit.
        
        Args:
            r1: Initial circular orbit radius in meters
            r2: Final circular orbit radius in meters
            central_mass: Central body mass in kg
            
        Returns:
            (dv1, dv2) - Delta-v at each burn in m/s
        """
        GM = AstroConstants.G * central_mass
        
        # Initial and final circular velocities
        v1 = np.sqrt(GM / r1)
        v2 = np.sqrt(GM / r2)
        
        # Transfer orbit semi-major axis
        a_transfer = (r1 + r2) / 2
        
        # Velocities on transfer orbit
        v_transfer_1 = np.sqrt(GM * (2/r1 - 1/a_transfer))
        v_transfer_2 = np.sqrt(GM * (2/r2 - 1/a_transfer))
        
        dv1 = abs(v_transfer_1 - v1)
        dv2 = abs(v2 - v_transfer_2)
        
        return dv1, dv2


# Standard cosmologies (like AstroPy presets)
Planck18 = Cosmology(H0=67.4, Om0=0.315, Ode0=0.685, Ob0=0.0493, Tcmb0=2.7255)
WMAP9 = Cosmology(H0=69.3, Om0=0.286, Ode0=0.714, Ob0=0.0463, Tcmb0=2.725)
