# dashboard/components/
"""
VECTOR Framework View Component.

VECTOR metrics and statistics visualization.
"""

from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def create_vector_view():
    """Create VECTOR view component."""
    return dbc.Container([
        html.H2("VECTOR Framework Metrics"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Delta Factors"),
                    dbc.CardBody([
                        html.Div(id='vector-delta-factors')
                    ])
                ])
            ], width=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Variance Statistics"),
                    dbc.CardBody([
                        dcc.Graph(id='vector-variance-graph')
                    ])
                ])
            ], width=6)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("VECTOR Statistics"),
                    dbc.CardBody([
                        html.Div(id='vector-statistics')
                    ])
                ])
            ], width=12)
        ], className="mt-3")
    ], fluid=True)

