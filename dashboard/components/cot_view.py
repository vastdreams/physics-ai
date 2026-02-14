"""
Chain-of-Thought View Component.

Interactive CoT tree display.
"""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import html


def create_cot_view() -> dbc.Container:
    """Create chain-of-thought view component."""
    return dbc.Container(
        [
            html.H2("Chain-of-Thought Logs"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader("CoT Tree"),
                                    dbc.CardBody(
                                        [
                                            html.Div(id="cot-tree-display"),
                                            dbc.Button(
                                                "Refresh", color="primary", className="mt-3"
                                            ),
                                        ]
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
                                    dbc.CardHeader("CoT Statistics"),
                                    dbc.CardBody([html.Div(id="cot-statistics")]),
                                ]
                            )
                        ],
                        width=6,
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader("Recent Steps"),
                                    dbc.CardBody([html.Div(id="cot-recent-steps")]),
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
