"""
Simulation View Component.

Real-time physics simulation visualization.
"""

from __future__ import annotations

import dash_bootstrap_components as dbc
import plotly.graph_objs as go
from dash import dcc, html

from loggers.system_logger import SystemLogger

_logger = SystemLogger()


def create_simulation_view() -> dbc.Container:
    """Create simulation view component."""
    return dbc.Container(
        [
            html.H2("Physics Simulations"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader("Active Simulations"),
                                    dbc.CardBody(
                                        [
                                            html.Div(id="simulation-list"),
                                            dbc.Button(
                                                "Start New Simulation",
                                                color="primary",
                                                className="mt-3",
                                            ),
                                        ]
                                    ),
                                ]
                            )
                        ],
                        width=4,
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader("Simulation Visualization"),
                                    dbc.CardBody([dcc.Graph(id="simulation-graph")]),
                                ]
                            )
                        ],
                        width=8,
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader("Simulation Parameters"),
                                    dbc.CardBody([html.Div(id="simulation-parameters")]),
                                ]
                            )
                        ],
                        width=12,
                    )
                ],
                className="mt-3",
            ),
        ],
        fluid=True,
    )


def update_simulation_graph(n_intervals: int) -> go.Figure:
    """Update simulation graph with real-time data.

    Args:
        n_intervals: Callback interval counter.

    Returns:
        Updated plotly figure.
    """
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=[0, 1, 2, 3, 4],
            y=[0, 1, 4, 9, 16],
            mode="lines+markers",
            name="Simulation Data",
        )
    )
    fig.update_layout(
        title="Real-Time Simulation",
        xaxis_title="Time",
        yaxis_title="Value",
    )
    return fig
