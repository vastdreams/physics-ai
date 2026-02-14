"""
PATH: physics/inference/kernel.py
PURPOSE: Optimized physics computation kernels

Provides efficient matrix operations and numerical methods inspired
by DeepSeek's kernel.py patterns:
- Block-wise processing for large arrays
- Scaled matrix multiplication (physics_gemm)
- Conservation law checking
- Symmetry transformations
- Numerical integration (Euler, RK4, RK45)

DEPENDENCIES:
- numpy: Numerical computation
"""

from typing import Callable, Tuple

import numpy as np

# Block size for optimized block-wise operations
BLOCK_SIZE: int = 128


def physics_gemm(
    a: np.ndarray,
    b: np.ndarray,
    scale_a: np.ndarray | None = None,
    scale_b: np.ndarray | None = None
) -> np.ndarray:
    """
    Scaled matrix multiplication for physics equations.

    Computes C = (scale_a · A) @ (scale_b · B) using optimized BLAS.

    Args:
        a: First matrix (M × K)
        b: Second matrix (K × N)
        scale_a: Optional scaling factors for a
        scale_b: Optional scaling factors for b

    Returns:
        Result matrix (M × N)
    """
    assert a.ndim == 2 and b.ndim == 2, "Inputs must be 2D matrices"
    assert a.shape[1] == b.shape[0], "Matrix dimensions must be compatible"

    if scale_a is not None:
        a = a * scale_a
    if scale_b is not None:
        b = b * scale_b

    return np.dot(a, b)


def conservation_kernel(
    initial_values: np.ndarray,
    final_values: np.ndarray,
    tolerance: float = 1e-6,
    block_size: int = BLOCK_SIZE
) -> Tuple[bool, np.ndarray]:
    """
    Block-wise conservation law checking.

    Computes element-wise differences and checks that all are within
    tolerance, processing large arrays in blocks for cache efficiency.

    Args:
        initial_values: Initial conserved quantities
        final_values: Final conserved quantities
        tolerance: Tolerance for conservation check
        block_size: Block size for processing

    Returns:
        Tuple of (is_conserved, differences)
    """
    assert initial_values.shape == final_values.shape, "Shapes must match"

    differences = np.abs(final_values - initial_values)

    if len(differences) > block_size:
        max_diff = 0.0
        for i in range(0, len(differences), block_size):
            block = differences[i:i + block_size]
            max_diff = max(max_diff, float(np.max(block)))
        is_conserved = max_diff <= tolerance
    else:
        is_conserved = bool(np.max(differences) <= tolerance)

    return is_conserved, differences


def symmetry_kernel(
    state: np.ndarray,
    symmetry_operation: np.ndarray,
    block_size: int = BLOCK_SIZE
) -> np.ndarray:
    """
    Apply a symmetry transformation matrix to a state tensor.

    Processes large states in blocks for cache efficiency:
        state_out = state @ symmetry_operation^T

    Args:
        state: State vector or tensor
        symmetry_operation: Symmetry transformation matrix
        block_size: Block size for processing

    Returns:
        Transformed state
    """
    assert state.ndim >= 1, "State must be at least 1D"

    original_shape = state.shape
    state_flat = state.reshape(-1, state.shape[-1])

    if len(state_flat) > block_size:
        result_blocks = []
        for i in range(0, len(state_flat), block_size):
            block = state_flat[i:i + block_size]
            result_blocks.append(np.dot(block, symmetry_operation.T))
        result_flat = np.vstack(result_blocks)
    else:
        result_flat = np.dot(state_flat, symmetry_operation.T)

    return result_flat.reshape(original_shape)


def integration_kernel(
    derivative_func: Callable,
    initial_state: np.ndarray,
    time_points: np.ndarray,
    method: str = "rk4",
    block_size: int = BLOCK_SIZE
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Numerical integration kernel supporting multiple methods.

    Methods:
    - "euler": Forward Euler — y_{n+1} = y_n + dt·f(t_n, y_n)
    - "rk4":   Classical RK4  — 4th-order Runge-Kutta
    - "rk45":  Adaptive RK4/5 — (currently uses fixed-step RK4)

    Args:
        derivative_func: Function computing derivatives f(t, y) → dy/dt
        initial_state: Initial state vector
        time_points: Array of time points
        method: Integration method ("euler", "rk4", "rk45")
        block_size: Block size for processing

    Returns:
        Tuple of (time_points, state_history)
    """
    assert len(time_points) > 1, "Must have at least 2 time points"
    assert initial_state.ndim == 1, "Initial state must be 1D"

    n_steps = len(time_points) - 1
    state_dim = len(initial_state)

    state_history = np.zeros((n_steps + 1, state_dim))
    state_history[0] = initial_state

    current_state = initial_state.copy()
    dt = time_points[1] - time_points[0]

    for i in range(n_steps):
        t = time_points[i]

        if method == "euler":
            derivative = derivative_func(t, current_state)
            current_state = current_state + dt * derivative

        elif method in ("rk4", "rk45"):
            k1 = derivative_func(t, current_state)
            k2 = derivative_func(t + dt / 2, current_state + dt * k1 / 2)
            k3 = derivative_func(t + dt / 2, current_state + dt * k2 / 2)
            k4 = derivative_func(t + dt, current_state + dt * k3)
            current_state = current_state + dt * (k1 + 2 * k2 + 2 * k3 + k4) / 6

        else:
            raise ValueError(f"Unknown integration method: {method}")

        state_history[i + 1] = current_state

        if i < n_steps - 1:
            dt = time_points[i + 1] - time_points[i]

    return time_points, state_history
