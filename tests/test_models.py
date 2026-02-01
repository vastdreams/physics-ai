# tests/
"""
PATH: tests/test_models.py
PURPOSE: Tests for physics model simulations.

Tests cover:
- Model initialization
- Simulation execution
- Energy conservation
- Numerical accuracy against analytical solutions
"""

import unittest
import numpy as np
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from physics.models import (
    PhysicsModel, SimulationState, SimulationResult,
    HarmonicOscillator, Pendulum, TwoBodyGravity, ProjectileMotion,
    IntegrationMethod, create_model
)


class TestSimulationState(unittest.TestCase):
    """Tests for SimulationState."""
    
    def test_creation(self):
        """Test state creation."""
        state = SimulationState(
            time=0.0,
            variables={'x': 1.0, 'v': 0.0}
        )
        
        self.assertEqual(state.time, 0.0)
        self.assertEqual(state.variables['x'], 1.0)
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        state = SimulationState(
            time=1.0,
            variables={'x': 2.0},
            energy=5.0
        )
        
        d = state.to_dict()
        self.assertEqual(d['time'], 1.0)
        self.assertEqual(d['variables']['x'], 2.0)
        self.assertEqual(d['energy'], 5.0)
    
    def test_to_array(self):
        """Test conversion to numpy array."""
        state = SimulationState(
            time=0.0,
            variables={'x': 1.0, 'v': 2.0}
        )
        
        arr = state.to_array(['x', 'v'])
        np.testing.assert_array_equal(arr, [1.0, 2.0])
    
    def test_from_array(self):
        """Test creation from numpy array."""
        arr = np.array([3.0, 4.0])
        state = SimulationState.from_array(arr, ['x', 'v'], time=5.0)
        
        self.assertEqual(state.time, 5.0)
        self.assertEqual(state.variables['x'], 3.0)
        self.assertEqual(state.variables['v'], 4.0)


class TestHarmonicOscillator(unittest.TestCase):
    """Tests for HarmonicOscillator model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.oscillator = HarmonicOscillator(mass=1.0, spring_constant=1.0, damping=0.0)
    
    def test_initialization(self):
        """Test model initialization."""
        self.assertEqual(self.oscillator.model_type, "harmonic_oscillator")
        self.assertEqual(self.oscillator.mass, 1.0)
        self.assertEqual(self.oscillator.spring_constant, 1.0)
        self.assertAlmostEqual(self.oscillator.omega, 1.0, places=5)
    
    def test_derivatives(self):
        """Test derivative computation."""
        state = SimulationState(time=0.0, variables={'x': 1.0, 'v': 0.0})
        derivs = self.oscillator.derivatives(state)
        
        # dx/dt = v = 0
        self.assertEqual(derivs['x'], 0.0)
        # dv/dt = -k/m * x = -1
        self.assertEqual(derivs['v'], -1.0)
    
    def test_energy(self):
        """Test energy computation."""
        state = SimulationState(time=0.0, variables={'x': 1.0, 'v': 0.0})
        energy = self.oscillator.energy(state)
        
        # E = 0.5*k*x^2 + 0.5*m*v^2 = 0.5*1*1 + 0 = 0.5
        self.assertAlmostEqual(energy, 0.5, places=5)
    
    def test_energy_conservation(self):
        """Test that energy is conserved in undamped oscillator."""
        result = self.oscillator.simulate(
            initial_conditions={'x': 1.0, 'v': 0.0},
            t_start=0.0,
            t_end=10.0,
            dt=0.001,
            method=IntegrationMethod.RK4
        )
        
        self.assertTrue(result.success)
        
        # Check energy conservation
        initial_energy = result.states[0].energy
        final_energy = result.states[-1].energy
        
        # Energy should be conserved within 1%
        relative_error = abs(final_energy - initial_energy) / initial_energy
        self.assertLess(relative_error, 0.01)
    
    def test_analytical_solution(self):
        """Test against analytical solution."""
        x0, v0 = 1.0, 0.0
        t = 2.0 * np.pi  # One complete period
        
        # Simulate
        result = self.oscillator.simulate(
            initial_conditions={'x': x0, 'v': v0},
            t_start=0.0,
            t_end=t,
            dt=0.001,
            method=IntegrationMethod.RK4
        )
        
        # Get analytical solution at t = 2*pi (should return to initial state)
        analytical = self.oscillator.analytical_solution(x0, v0, t)
        
        # Compare
        final_state = result.states[-1]
        self.assertAlmostEqual(final_state.variables['x'], analytical['x'], places=2)
    
    def test_damped_oscillator(self):
        """Test damped oscillator loses energy."""
        damped = HarmonicOscillator(mass=1.0, spring_constant=1.0, damping=0.1)
        
        result = damped.simulate(
            initial_conditions={'x': 1.0, 'v': 0.0},
            t_start=0.0,
            t_end=20.0,
            dt=0.01,
            method=IntegrationMethod.RK4
        )
        
        initial_energy = result.states[0].energy
        final_energy = result.states[-1].energy
        
        # Energy should decrease in damped system
        self.assertLess(final_energy, initial_energy)


class TestPendulum(unittest.TestCase):
    """Tests for Pendulum model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.pendulum = Pendulum(length=1.0, mass=1.0, gravity=9.81, damping=0.0)
    
    def test_initialization(self):
        """Test model initialization."""
        self.assertEqual(self.pendulum.model_type, "pendulum")
        self.assertEqual(self.pendulum.length, 1.0)
        self.assertEqual(self.pendulum.gravity, 9.81)
    
    def test_derivatives_at_equilibrium(self):
        """Test derivatives at equilibrium position."""
        state = SimulationState(time=0.0, variables={'theta': 0.0, 'omega': 0.0})
        derivs = self.pendulum.derivatives(state)
        
        # At equilibrium, derivatives should be zero
        self.assertAlmostEqual(derivs['theta'], 0.0, places=10)
        self.assertAlmostEqual(derivs['omega'], 0.0, places=10)
    
    def test_energy_conservation(self):
        """Test energy conservation for undamped pendulum."""
        result = self.pendulum.simulate(
            initial_conditions={'theta': 0.1, 'omega': 0.0},  # Small angle
            t_start=0.0,
            t_end=10.0,
            dt=0.001,
            method=IntegrationMethod.RK4
        )
        
        self.assertTrue(result.success)
        
        initial_energy = result.states[0].energy
        final_energy = result.states[-1].energy
        
        relative_error = abs(final_energy - initial_energy) / initial_energy
        self.assertLess(relative_error, 0.01)
    
    def test_small_angle_period(self):
        """Test period matches small angle approximation."""
        # For small angles, period T ≈ 2*pi*sqrt(L/g)
        expected_period = 2 * np.pi * np.sqrt(self.pendulum.length / self.pendulum.gravity)
        
        result = self.pendulum.simulate(
            initial_conditions={'theta': 0.05, 'omega': 0.0},  # Very small angle
            t_start=0.0,
            t_end=expected_period * 2,
            dt=0.001,
            method=IntegrationMethod.RK4
        )
        
        # Find zero crossings to measure period
        thetas = [s.variables['theta'] for s in result.states]
        times = [s.time for s in result.states]
        
        zero_crossings = []
        for i in range(1, len(thetas)):
            if thetas[i-1] * thetas[i] < 0 and thetas[i] > 0:  # Positive zero crossing
                zero_crossings.append(times[i])
        
        if len(zero_crossings) >= 2:
            measured_period = zero_crossings[1] - zero_crossings[0]
            # Should be close to theoretical period
            self.assertAlmostEqual(measured_period, expected_period, places=1)


class TestProjectileMotion(unittest.TestCase):
    """Tests for ProjectileMotion model."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.projectile = ProjectileMotion(mass=1.0, gravity=9.81, drag_coefficient=0.0)
    
    def test_initialization(self):
        """Test model initialization."""
        self.assertEqual(self.projectile.model_type, "projectile_motion")
        self.assertEqual(self.projectile.gravity, 9.81)
    
    def test_no_drag_trajectory(self):
        """Test trajectory without drag matches analytical solution."""
        v0 = 10.0
        angle = np.pi / 4  # 45 degrees
        
        vx0 = v0 * np.cos(angle)
        vy0 = v0 * np.sin(angle)
        
        result = self.projectile.simulate(
            initial_conditions={'x': 0, 'y': 0, 'vx': vx0, 'vy': vy0},
            t_start=0.0,
            t_end=2.0,
            dt=0.01,
            method=IntegrationMethod.RK4
        )
        
        # Check range at t = 1.0 (halfway through flight)
        t = 1.0
        idx = int(t / 0.01)
        state = result.states[idx]
        
        # Analytical: x = vx0 * t, y = vy0 * t - 0.5 * g * t^2
        expected_x = vx0 * t
        expected_y = vy0 * t - 0.5 * 9.81 * t**2
        
        self.assertAlmostEqual(state.variables['x'], expected_x, places=1)
        self.assertAlmostEqual(state.variables['y'], expected_y, places=1)
    
    def test_with_drag(self):
        """Test that drag reduces range."""
        v0 = 20.0
        angle = np.pi / 4
        vx0 = v0 * np.cos(angle)
        vy0 = v0 * np.sin(angle)
        
        # Without drag
        no_drag = ProjectileMotion(gravity=9.81, drag_coefficient=0.0)
        result_no_drag = no_drag.simulate(
            initial_conditions={'x': 0, 'y': 0, 'vx': vx0, 'vy': vy0},
            t_start=0.0,
            t_end=5.0,
            dt=0.01,
            method=IntegrationMethod.RK4
        )
        
        # With drag
        with_drag = ProjectileMotion(gravity=9.81, drag_coefficient=0.5, cross_section=0.1)
        result_with_drag = with_drag.simulate(
            initial_conditions={'x': 0, 'y': 0, 'vx': vx0, 'vy': vy0},
            t_start=0.0,
            t_end=5.0,
            dt=0.01,
            method=IntegrationMethod.RK4
        )
        
        # Find max x reached
        max_x_no_drag = max(s.variables['x'] for s in result_no_drag.states)
        max_x_with_drag = max(s.variables['x'] for s in result_with_drag.states)
        
        # Range with drag should be less
        self.assertLess(max_x_with_drag, max_x_no_drag)


class TestTwoBodyGravity(unittest.TestCase):
    """Tests for TwoBodyGravity model."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Earth-Sun like system (scaled)
        self.two_body = TwoBodyGravity(mass1=1e24, mass2=1e30, G=6.67430e-11)
    
    def test_initialization(self):
        """Test model initialization."""
        self.assertEqual(self.two_body.model_type, "two_body_gravity")
        self.assertIsNotNone(self.two_body.mu)
    
    def test_circular_orbit_energy(self):
        """Test energy conservation in circular orbit."""
        # For circular orbit: v = sqrt(mu/r)
        r = 1e11  # 100 million km
        v = np.sqrt(self.two_body.mu / r)
        
        result = self.two_body.simulate(
            initial_conditions={'x': r, 'y': 0, 'vx': 0, 'vy': v},
            t_start=0.0,
            t_end=1e7,  # Part of orbit
            dt=1e4,
            method=IntegrationMethod.RK4
        )
        
        self.assertTrue(result.success)
        
        # Check energy conservation
        if result.states[0].energy and result.states[-1].energy:
            initial_energy = result.states[0].energy
            final_energy = result.states[-1].energy
            
            if initial_energy != 0:
                relative_error = abs(final_energy - initial_energy) / abs(initial_energy)
                self.assertLess(relative_error, 0.1)


class TestModelFactory(unittest.TestCase):
    """Tests for model factory function."""
    
    def test_create_harmonic_oscillator(self):
        """Test creating harmonic oscillator."""
        model = create_model('harmonic_oscillator', mass=2.0, spring_constant=8.0)
        
        self.assertIsInstance(model, HarmonicOscillator)
        self.assertEqual(model.mass, 2.0)
        self.assertEqual(model.spring_constant, 8.0)
    
    def test_create_pendulum(self):
        """Test creating pendulum."""
        model = create_model('pendulum', length=2.0, mass=0.5)
        
        self.assertIsInstance(model, Pendulum)
        self.assertEqual(model.length, 2.0)
    
    def test_unknown_model(self):
        """Test error on unknown model type."""
        with self.assertRaises(ValueError):
            create_model('unknown_model')


class TestIntegrationMethods(unittest.TestCase):
    """Tests comparing different integration methods."""
    
    def test_euler_vs_rk4(self):
        """Test that RK4 is more accurate than Euler."""
        oscillator = HarmonicOscillator()
        
        # Euler method
        result_euler = oscillator.simulate(
            initial_conditions={'x': 1.0, 'v': 0.0},
            t_start=0.0,
            t_end=10.0,
            dt=0.01,
            method=IntegrationMethod.EULER
        )
        
        # RK4 method
        result_rk4 = oscillator.simulate(
            initial_conditions={'x': 1.0, 'v': 0.0},
            t_start=0.0,
            t_end=10.0,
            dt=0.01,
            method=IntegrationMethod.RK4
        )
        
        # Compare energy conservation
        euler_energy_error = abs(result_euler.states[-1].energy - result_euler.states[0].energy)
        rk4_energy_error = abs(result_rk4.states[-1].energy - result_rk4.states[0].energy)
        
        # RK4 should have smaller error
        self.assertLess(rk4_energy_error, euler_energy_error)


if __name__ == '__main__':
    unittest.main()
