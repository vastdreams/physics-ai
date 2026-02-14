"""
Evolution View Component.

Code evolution history and tracking.
"""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import html


def create_evolution_view() -> dbc.Container:
    """Create evolution view component."""
    return dbc.Container(
        [
            html.H2("Code Evolution History"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader("Evolution Timeline"),
                                    dbc.CardBody([html.Div(id="evolution-timeline")]),
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
                                    dbc.CardHeader("Evolution Statistics"),
                                    dbc.CardBody([html.Div(id="evolution-statistics")]),
                                ]
                            )
                        ],
                        width=6,
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader("Recent Evolutions"),
                                    dbc.CardBody([html.Div(id="evolution-recent")]),
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
