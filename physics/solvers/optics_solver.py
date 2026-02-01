"""
PATH: physics/solvers/optics_solver.py
PURPOSE: Physical optics and diffraction simulations integrating POPPY concepts

WHY: Provides wavefront propagation, PSF calculation, and optical system
     modeling using Fourier optics methods from POPPY.

REFERENCES:
- POPPY: https://github.com/spacetelescope/poppy (BSD-3)
- WebbPSF uses POPPY for JWST simulations

FLOW:
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│ Define      │────>│ Propagate    │────>│ Compute PSF/    │
│ Optical     │     │ Wavefront    │     │ Diffraction     │
│ Elements    │     │ (Fraunhofer/ │     │ Pattern         │
│             │     │  Fresnel)    │     │                 │
└─────────────┘     └──────────────┘     └─────────────────┘

DEPENDENCIES:
- numpy: Numerical computations
- scipy: FFT, special functions
"""

from typing import Tuple, Optional, List, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import numpy as np
from scipy.fft import fft2, ifft2, fftshift, ifftshift
from scipy.special import j1  # Bessel function
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# PHYSICAL CONSTANTS
# ============================================================================

class OpticsConstants:
    """Optical and physical constants."""
    c = 299792458.0  # Speed of light [m/s]
    h = 6.62607015e-34  # Planck constant [J⋅s]
    
    # Common wavelengths (in meters)
    WAVELENGTH_UV = 365e-9
    WAVELENGTH_BLUE = 450e-9
    WAVELENGTH_GREEN = 550e-9
    WAVELENGTH_RED = 650e-9
    WAVELENGTH_IR = 1000e-9
    WAVELENGTH_H_ALPHA = 656.3e-9
    WAVELENGTH_JWST = 2e-6  # Near-IR for JWST


# ============================================================================
# WAVEFRONT CLASS (Inspired by POPPY)
# ============================================================================

@dataclass
class Wavefront:
    """
    Complex optical wavefront representation.
    
    Inspired by POPPY's Wavefront class.
    """
    wavelength: float  # Wavelength in meters
    npix: int  # Number of pixels per side
    pixelscale: float  # Pixel scale in meters/pixel (pupil) or radians/pixel (image)
    
    # Complex amplitude array
    amplitude: np.ndarray = field(init=False, default=None)
    
    # Location tracking
    planetype: str = field(default="pupil")  # 'pupil' or 'image'
    
    def __post_init__(self):
        """Initialize uniform amplitude."""
        if self.amplitude is None:
            self.amplitude = np.ones((self.npix, self.npix), dtype=complex)
    
    @property
    def intensity(self) -> np.ndarray:
        """Intensity = |amplitude|²."""
        return np.abs(self.amplitude)**2
    
    @property
    def phase(self) -> np.ndarray:
        """Phase of wavefront."""
        return np.angle(self.amplitude)
    
    @property
    def total_intensity(self) -> float:
        """Total integrated intensity."""
        return np.sum(self.intensity) * self.pixelscale**2
    
    def copy(self) -> 'Wavefront':
        """Create copy of wavefront."""
        wf = Wavefront(
            wavelength=self.wavelength,
            npix=self.npix,
            pixelscale=self.pixelscale,
            planetype=self.planetype
        )
        wf.amplitude = self.amplitude.copy()
        return wf
    
    def normalize(self) -> None:
        """Normalize to unit total intensity."""
        total = np.sqrt(self.total_intensity)
        if total > 0:
            self.amplitude /= total


# ============================================================================
# OPTICAL ELEMENTS (Inspired by POPPY)
# ============================================================================

class OpticalElement(ABC):
    """
    Abstract base class for optical elements.
    
    Inspired by POPPY's optics module.
    """
    
    @abstractmethod
    def get_transmission(self, wavefront: Wavefront) -> np.ndarray:
        """Return complex transmission function."""
        pass
    
    def apply(self, wavefront: Wavefront) -> Wavefront:
        """Apply optical element to wavefront."""
        wf = wavefront.copy()
        transmission = self.get_transmission(wavefront)
        wf.amplitude *= transmission
        return wf


class CircularAperture(OpticalElement):
    """
    Circular aperture (hard edge).
    
    Transmission = 1 inside radius, 0 outside.
    """
    
    def __init__(self, radius: float, center: Tuple[float, float] = (0, 0)):
        """
        Args:
            radius: Aperture radius in meters
            center: Center position (x, y) in meters
        """
        self.radius = radius
        self.center = center
    
    def get_transmission(self, wavefront: Wavefront) -> np.ndarray:
        """Create circular aperture mask."""
        n = wavefront.npix
        scale = wavefront.pixelscale
        
        # Coordinate arrays
        y, x = np.mgrid[-n//2:n//2, -n//2:n//2] * scale
        x -= self.center[0]
        y -= self.center[1]
        
        r = np.sqrt(x**2 + y**2)
        return (r <= self.radius).astype(float)


class AnnularAperture(OpticalElement):
    """Annular aperture with central obscuration."""
    
    def __init__(self, outer_radius: float, inner_radius: float):
        """
        Args:
            outer_radius: Outer aperture radius in meters
            inner_radius: Inner (obscuration) radius in meters
        """
        self.outer_radius = outer_radius
        self.inner_radius = inner_radius
    
    def get_transmission(self, wavefront: Wavefront) -> np.ndarray:
        """Create annular aperture mask."""
        n = wavefront.npix
        scale = wavefront.pixelscale
        
        y, x = np.mgrid[-n//2:n//2, -n//2:n//2] * scale
        r = np.sqrt(x**2 + y**2)
        
        return ((r <= self.outer_radius) & (r >= self.inner_radius)).astype(float)


class ThinLens(OpticalElement):
    """
    Thin lens with focal length f.
    
    Applies phase: exp(-i * k * r² / (2f))
    """
    
    def __init__(self, focal_length: float, radius: float):
        """
        Args:
            focal_length: Focal length in meters (positive = converging)
            radius: Lens radius in meters
        """
        self.focal_length = focal_length
        self.radius = radius
    
    def get_transmission(self, wavefront: Wavefront) -> np.ndarray:
        """Create thin lens transmission function."""
        n = wavefront.npix
        scale = wavefront.pixelscale
        k = 2 * np.pi / wavefront.wavelength
        
        y, x = np.mgrid[-n//2:n//2, -n//2:n//2] * scale
        r2 = x**2 + y**2
        
        # Aperture mask
        aperture = (np.sqrt(r2) <= self.radius).astype(float)
        
        # Phase from lens
        phase = -k * r2 / (2 * self.focal_length)
        
        return aperture * np.exp(1j * phase)


class ZernikeWFE(OpticalElement):
    """
    Zernike polynomial wavefront error.
    
    Adds phase aberrations defined by Zernike coefficients.
    """
    
    # Zernike polynomial names (Noll indexing)
    ZERNIKE_NAMES = {
        1: "Piston",
        2: "Tilt X",
        3: "Tilt Y",
        4: "Defocus",
        5: "Astigmatism 45°",
        6: "Astigmatism 0°",
        7: "Coma Y",
        8: "Coma X",
        9: "Trefoil Y",
        10: "Trefoil X",
        11: "Spherical",
    }
    
    def __init__(self, radius: float, coefficients: dict):
        """
        Args:
            radius: Aperture radius in meters
            coefficients: Dict of {noll_index: coefficient_in_waves}
        """
        self.radius = radius
        self.coefficients = coefficients
    
    def _zernike(self, n: int, m: int, rho: np.ndarray, phi: np.ndarray) -> np.ndarray:
        """
        Compute Zernike polynomial Z_n^m.
        
        Uses radial polynomial R_n^m(ρ) * angular function.
        """
        # Radial polynomial
        R = np.zeros_like(rho)
        for k in range((n - abs(m)) // 2 + 1):
            coef = ((-1)**k * np.math.factorial(n - k) /
                   (np.math.factorial(k) *
                    np.math.factorial((n + abs(m)) // 2 - k) *
                    np.math.factorial((n - abs(m)) // 2 - k)))
            R += coef * rho**(n - 2*k)
        
        # Angular part
        if m >= 0:
            return R * np.cos(m * phi)
        else:
            return R * np.sin(abs(m) * phi)
    
    def _noll_to_nm(self, j: int) -> Tuple[int, int]:
        """Convert Noll index j to (n, m)."""
        n = int(np.ceil((-3 + np.sqrt(9 + 8*(j-1))) / 2))
        m = 2*j - n*(n+2) - 1 if (n % 2 == j % 2) else -2*j + n*(n+2) + 1
        return n, abs(m) if (j % 2 == 0) else -abs(m)
    
    def get_transmission(self, wavefront: Wavefront) -> np.ndarray:
        """Create transmission with Zernike aberrations."""
        n = wavefront.npix
        scale = wavefront.pixelscale
        
        y, x = np.mgrid[-n//2:n//2, -n//2:n//2] * scale
        rho = np.sqrt(x**2 + y**2) / self.radius
        phi = np.arctan2(y, x)
        
        # Aperture mask
        aperture = (rho <= 1.0)
        
        # Sum Zernike contributions
        phase = np.zeros((n, n))
        for noll_j, coef in self.coefficients.items():
            n_z, m_z = self._noll_to_nm(noll_j)
            phase += coef * self._zernike(n_z, m_z, np.where(aperture, rho, 0), phi)
        
        # Convert waves to radians
        phase_rad = 2 * np.pi * phase
        
        return aperture * np.exp(1j * phase_rad)


class DoubleSlits(OpticalElement):
    """Double slit aperture for interference demonstration."""
    
    def __init__(self, slit_separation: float, slit_width: float, slit_height: float):
        """
        Args:
            slit_separation: Distance between slit centers in meters
            slit_width: Width of each slit in meters
            slit_height: Height of each slit in meters
        """
        self.separation = slit_separation
        self.width = slit_width
        self.height = slit_height
    
    def get_transmission(self, wavefront: Wavefront) -> np.ndarray:
        """Create double slit mask."""
        n = wavefront.npix
        scale = wavefront.pixelscale
        
        y, x = np.mgrid[-n//2:n//2, -n//2:n//2] * scale
        
        # Two rectangular slits
        slit1 = ((np.abs(x - self.separation/2) <= self.width/2) & 
                 (np.abs(y) <= self.height/2))
        slit2 = ((np.abs(x + self.separation/2) <= self.width/2) & 
                 (np.abs(y) <= self.height/2))
        
        return (slit1 | slit2).astype(float)


# ============================================================================
# PROPAGATION METHODS (Inspired by POPPY)
# ============================================================================

class FresnelPropagator:
    """
    Fresnel (near-field) diffraction propagation.
    
    Uses Angular Spectrum Method or direct Fresnel integral.
    """
    
    @staticmethod
    def propagate(wavefront: Wavefront, distance: float) -> Wavefront:
        """
        Propagate wavefront by distance z using Angular Spectrum Method.
        
        H(fx, fy) = exp(i*k*z*sqrt(1 - (λ*fx)² - (λ*fy)²))
        """
        wf = wavefront.copy()
        k = 2 * np.pi / wf.wavelength
        n = wf.npix
        
        # Spatial frequency grid
        df = 1.0 / (n * wf.pixelscale)
        fy, fx = np.mgrid[-n//2:n//2, -n//2:n//2] * df
        
        # Transfer function
        arg = 1 - (wf.wavelength * fx)**2 - (wf.wavelength * fy)**2
        
        # Evanescent waves (arg < 0) contribute no propagating field
        arg = np.where(arg > 0, arg, 0)
        H = np.exp(1j * k * distance * np.sqrt(arg))
        H = fftshift(H)
        
        # Propagate in Fourier space
        wf.amplitude = ifft2(H * fft2(wf.amplitude))
        
        return wf


class FraunhoferPropagator:
    """
    Fraunhofer (far-field) diffraction propagation.
    
    Valid when z >> D²/λ (Fraunhofer condition).
    Uses FFT since far-field pattern is Fourier transform of aperture.
    """
    
    @staticmethod
    def propagate(wavefront: Wavefront, focal_length: float) -> Wavefront:
        """
        Propagate to far-field (focal plane of lens with focal length f).
        
        The image plane pixelscale becomes λf/(N*Δx) in angular units.
        """
        wf = wavefront.copy()
        n = wf.npix
        
        # Fourier transform (with proper normalization)
        wf.amplitude = fftshift(fft2(ifftshift(wf.amplitude))) / n
        
        # Update pixelscale to angular (radians/pixel)
        wf.pixelscale = wf.wavelength / (n * wf.pixelscale)
        wf.planetype = "image"
        
        return wf
    
    @staticmethod
    def to_image_plane(wavefront: Wavefront, focal_length: float, 
                       detector_pixelscale: float) -> Wavefront:
        """
        Propagate to image plane with specified detector sampling.
        
        Uses zero-padding for oversampling.
        """
        wf = wavefront.copy()
        
        # Required oversampling
        native_scale = wf.wavelength * focal_length / (wf.npix * wf.pixelscale)
        oversample = int(np.ceil(native_scale / detector_pixelscale))
        
        if oversample > 1:
            # Zero-pad
            n_new = wf.npix * oversample
            padded = np.zeros((n_new, n_new), dtype=complex)
            offset = (n_new - wf.npix) // 2
            padded[offset:offset+wf.npix, offset:offset+wf.npix] = wf.amplitude
            wf.amplitude = padded
            wf.npix = n_new
        
        return FraunhoferPropagator.propagate(wf, focal_length)


# ============================================================================
# OPTICAL SYSTEM (Inspired by POPPY)
# ============================================================================

class OpticalSystem:
    """
    Complete optical system with multiple elements.
    
    Inspired by POPPY's OpticalSystem class.
    """
    
    def __init__(self, wavelength: float, npix: int = 256, pixelscale: float = 1e-3):
        """
        Args:
            wavelength: Wavelength in meters
            npix: Number of pixels
            pixelscale: Pixel scale in meters (pupil plane)
        """
        self.wavelength = wavelength
        self.npix = npix
        self.pixelscale = pixelscale
        self.elements: List[Tuple[OpticalElement, Optional[float]]] = []
    
    def add_optic(self, element: OpticalElement, distance: float = None):
        """
        Add optical element to system.
        
        Args:
            element: Optical element to add
            distance: Propagation distance after element (None = at current plane)
        """
        self.elements.append((element, distance))
    
    def calc_psf(self, normalize: bool = True) -> np.ndarray:
        """
        Calculate Point Spread Function.
        
        Returns:
            PSF intensity array
        """
        # Initialize wavefront
        wf = Wavefront(
            wavelength=self.wavelength,
            npix=self.npix,
            pixelscale=self.pixelscale,
            planetype="pupil"
        )
        
        # Apply each element and propagate
        for element, distance in self.elements:
            wf = element.apply(wf)
            
            if distance is not None:
                if wf.planetype == "pupil":
                    wf = FresnelPropagator.propagate(wf, distance)
        
        # Final propagation to image plane if still in pupil
        if wf.planetype == "pupil":
            wf = FraunhoferPropagator.propagate(wf, focal_length=1.0)
        
        psf = wf.intensity
        
        if normalize:
            psf /= psf.sum()
        
        return psf


# ============================================================================
# ANALYTICAL DIFFRACTION PATTERNS
# ============================================================================

class AnalyticalDiffraction:
    """
    Analytical diffraction patterns for comparison with numerical results.
    """
    
    @staticmethod
    def airy_pattern(theta: np.ndarray, diameter: float, wavelength: float) -> np.ndarray:
        """
        Airy diffraction pattern from circular aperture.
        
        I(θ) = (2*J₁(x)/x)² where x = πDsinθ/λ
        
        Args:
            theta: Angle array in radians
            diameter: Aperture diameter in meters
            wavelength: Wavelength in meters
            
        Returns:
            Normalized intensity pattern
        """
        x = np.pi * diameter * np.sin(theta) / wavelength
        
        # Handle x=0 (center)
        pattern = np.ones_like(x)
        nonzero = x != 0
        pattern[nonzero] = (2 * j1(x[nonzero]) / x[nonzero])**2
        
        return pattern
    
    @staticmethod
    def airy_radius(wavelength: float, diameter: float, focal_length: float) -> float:
        """
        First dark ring radius of Airy disk.
        
        r = 1.22 * λ * f / D
        """
        return 1.22 * wavelength * focal_length / diameter
    
    @staticmethod
    def rayleigh_criterion(wavelength: float, diameter: float) -> float:
        """
        Rayleigh criterion angular resolution.
        
        θ_min = 1.22 * λ / D
        
        Returns:
            Minimum resolvable angle in radians
        """
        return 1.22 * wavelength / diameter
    
    @staticmethod
    def double_slit_pattern(theta: np.ndarray, slit_separation: float, 
                            slit_width: float, wavelength: float) -> np.ndarray:
        """
        Double slit interference pattern.
        
        I = I_0 * cos²(πd*sinθ/λ) * sinc²(πa*sinθ/λ)
        
        Args:
            theta: Angle array in radians
            slit_separation: Distance between slits in meters
            slit_width: Width of each slit in meters
            wavelength: Wavelength in meters
        """
        # Interference term
        alpha = np.pi * slit_separation * np.sin(theta) / wavelength
        interference = np.cos(alpha)**2
        
        # Diffraction envelope (single slit)
        beta = np.pi * slit_width * np.sin(theta) / wavelength
        diffraction = np.sinc(beta / np.pi)**2  # np.sinc(x) = sin(πx)/(πx)
        
        return interference * diffraction
    
    @staticmethod
    def single_slit_minima(wavelength: float, slit_width: float) -> Callable:
        """
        Angular positions of single slit diffraction minima.
        
        sin(θ_m) = m * λ / a, m = ±1, ±2, ...
        """
        def minima(m: int) -> float:
            return np.arcsin(m * wavelength / slit_width)
        return minima
    
    @staticmethod
    def grating_maxima(wavelength: float, grating_spacing: float, order: int) -> float:
        """
        Diffraction grating maxima angles.
        
        d * sin(θ) = m * λ
        
        Returns:
            Angle in radians for given order
        """
        sin_theta = order * wavelength / grating_spacing
        if abs(sin_theta) > 1:
            return np.nan  # No solution
        return np.arcsin(sin_theta)


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def compute_psf_circular(diameter: float, wavelength: float, npix: int = 256,
                         oversampling: int = 4) -> np.ndarray:
    """
    Compute PSF for simple circular aperture.
    
    Args:
        diameter: Aperture diameter in meters
        wavelength: Wavelength in meters
        npix: Output array size
        oversampling: Oversampling factor
        
    Returns:
        Normalized PSF array
    """
    # Pupil sampling
    pupil_pixelscale = diameter / (npix // oversampling)
    
    system = OpticalSystem(
        wavelength=wavelength,
        npix=npix,
        pixelscale=pupil_pixelscale
    )
    
    system.add_optic(CircularAperture(radius=diameter/2))
    
    return system.calc_psf()


def compute_psf_with_aberrations(diameter: float, wavelength: float,
                                  zernike_coeffs: dict, npix: int = 256) -> np.ndarray:
    """
    Compute PSF with Zernike aberrations.
    
    Args:
        diameter: Aperture diameter in meters
        wavelength: Wavelength in meters
        zernike_coeffs: Dict of {noll_index: coefficient_in_waves}
        npix: Output array size
        
    Returns:
        Normalized PSF array
    """
    pupil_pixelscale = diameter * 2 / npix
    
    system = OpticalSystem(
        wavelength=wavelength,
        npix=npix,
        pixelscale=pupil_pixelscale
    )
    
    system.add_optic(CircularAperture(radius=diameter/2))
    system.add_optic(ZernikeWFE(radius=diameter/2, coefficients=zernike_coeffs))
    
    return system.calc_psf()
