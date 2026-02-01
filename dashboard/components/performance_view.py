# dashboard/components/
"""
Performance View Component.

System performance monitoring.
"""

from dash import dcc, html
import dash_bootstrap_components as dbc
import plotly.graph_objs as go
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def create_performance_view():
    """Create performance view component."""
    return dbc.Container([
        html.H2("Performance Monitoring"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Performance Metrics"),
                    dbc.CardBody([
                        dcc.Graph(id='performance-metrics-graph')
                    ])
                ])
            ], width=12)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Recent Alerts"),
                    dbc.CardBody([
                        html.Div(id='performance-alerts')
                    ])
                ])
            ], width=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Performance Statistics"),
                    dbc.CardBody([
                        html.Div(id='performance-statistics')
                    ])
                ])
            ], width=6)
        ], className="mt-3")
    ], fluid=True)

