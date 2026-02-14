"""
Performance View Component.

System performance monitoring.
"""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dcc, html


def create_performance_view() -> dbc.Container:
    """Create performance view component."""
    return dbc.Container(
        [
            html.H2("Performance Monitoring"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader("Performance Metrics"),
                                    dbc.CardBody(
                                        [dcc.Graph(id="performance-metrics-graph")]
                                    ),
                                ]
                            )
                        ],
                        width=12,
                    )
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader("Recent Alerts"),
                                    dbc.CardBody([html.Div(id="performance-alerts")]),
                                ]
                            )
                        ],
                        width=6,
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader("Performance Statistics"),
                                    dbc.CardBody([html.Div(id="performance-statistics")]),
                                ]
                            )
                        ],
                        width=6,
                    ),
                ],
                className="mt-3",
            ),
        ],
        fluid=True,
    )
