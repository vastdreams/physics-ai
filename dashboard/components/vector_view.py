"""
VECTOR Framework View Component.

VECTOR metrics and statistics visualization.
"""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import dcc, html


def create_vector_view() -> dbc.Container:
    """Create VECTOR view component."""
    return dbc.Container(
        [
            html.H2("VECTOR Framework Metrics"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader("Delta Factors"),
                                    dbc.CardBody([html.Div(id="vector-delta-factors")]),
                                ]
                            )
                        ],
                        width=6,
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader("Variance Statistics"),
                                    dbc.CardBody(
                                        [dcc.Graph(id="vector-variance-graph")]
                                    ),
                                ]
                            )
                        ],
                        width=6,
                    ),
                ]
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader("VECTOR Statistics"),
                                    dbc.CardBody([html.Div(id="vector-statistics")]),
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
