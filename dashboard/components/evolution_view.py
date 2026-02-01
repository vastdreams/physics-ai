# dashboard/components/
"""
Evolution View Component.

Code evolution history and tracking.
"""

from dash import dcc, html
import dash_bootstrap_components as dbc
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def create_evolution_view():
    """Create evolution view component."""
    return dbc.Container([
        html.H2("Code Evolution History"),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Evolution Timeline"),
                    dbc.CardBody([
                        html.Div(id='evolution-timeline')
                    ])
                ])
            ], width=12)
        ]),
        
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Evolution Statistics"),
                    dbc.CardBody([
                        html.Div(id='evolution-statistics')
                    ])
                ])
            ], width=6),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Recent Evolutions"),
                    dbc.CardBody([
                        html.Div(id='evolution-recent')
                    ])
                ])
            ], width=6)
        ], className="mt-3")
    ], fluid=True)

