"""
Node Graph View Component.

Nodal vectorization graph visualization.
"""

from __future__ import annotations

import dash_bootstrap_components as dbc
from dash import html


def create_node_graph_view() -> dbc.Container:
    """Create node graph view component."""
    return dbc.Container(
        [
            html.H2("Nodal Graph Visualization"),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader("Graph Visualization"),
                                    dbc.CardBody(
                                        [
                                            html.Div(id="node-graph-display"),
                                            dbc.Button(
                                                "Refresh Graph",
                                                color="primary",
                                                className="mt-3",
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
                                    dbc.CardHeader("Graph Statistics"),
                                    dbc.CardBody([html.Div(id="node-graph-statistics")]),
                                ]
                            )
                        ],
                        width=6,
                    ),
                    dbc.Col(
                        [
                            dbc.Card(
                                [
                                    dbc.CardHeader("Node Details"),
                                    dbc.CardBody([html.Div(id="node-details")]),
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
