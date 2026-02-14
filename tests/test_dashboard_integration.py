"""Integration tests for Dashboard system."""

from __future__ import annotations

import unittest


class TestDashboardIntegration(unittest.TestCase):
    """Test Dashboard integration."""

    def test_dashboard_import(self) -> None:
        """Test dashboard module imports."""
        try:
            from dashboard.app import create_app
            from dashboard.components import (
                create_cot_view,
                create_evolution_view,
                create_node_graph_view,
                create_performance_view,
                create_simulation_view,
                create_vector_view,
            )

            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"Failed to import dashboard components: {e}")

    def test_dashboard_app_creation(self) -> None:
        """Test dashboard app creation."""
        try:
            from dashboard.app import create_app

            app = create_app()
            self.assertIsNotNone(app)
        except Exception as e:
            self.fail(f"Failed to create dashboard app: {e}")

    def test_view_components(self) -> None:
        """Test view component creation."""
        try:
            from dashboard.components.cot_view import create_cot_view
            from dashboard.components.evolution_view import create_evolution_view
            from dashboard.components.node_graph_view import create_node_graph_view
            from dashboard.components.performance_view import create_performance_view
            from dashboard.components.simulation_view import create_simulation_view
            from dashboard.components.vector_view import create_vector_view

            views = [
                create_simulation_view(),
                create_cot_view(),
                create_node_graph_view(),
                create_vector_view(),
                create_performance_view(),
                create_evolution_view(),
            ]

            for view in views:
                self.assertIsNotNone(view)
        except Exception as e:
            self.fail(f"Failed to create view components: {e}")


if __name__ == "__main__":
    unittest.main()
