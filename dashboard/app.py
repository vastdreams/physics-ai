# dashboard/
"""
Main Dash application.

Inspired by DREAM architecture - real-time dashboards for monitoring.

First Principle Analysis:
- Dash app: Multi-page application with routing
- Real-time updates: WebSocket integration
- Component-based: Modular visualization components
- Mathematical foundation: Data visualization, interactive charts
- Architecture: Flask + Dash with WebSocket support
"""

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from flask import Flask
import sys
import os
import json
import requests
import plotly.graph_objs as go
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from loggers.system_logger import SystemLogger
from dashboard.components.simulation_view import create_simulation_view
from dashboard.components.cot_view import create_cot_view
from dashboard.components.node_graph_view import create_node_graph_view
from dashboard.components.vector_view import create_vector_view
from dashboard.components.performance_view import create_performance_view
from dashboard.components.evolution_view import create_evolution_view

logger = SystemLogger()

# Initialize Flask app
flask_app = Flask(__name__)
flask_app.config['SECRET_KEY'] = 'physics-ai-dashboard-secret-key'

# Initialize Dash app
app = dash.Dash(
    __name__,
    server=flask_app,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

# App layout
app.layout = dbc.Container([
    dcc.Location(id='url', refresh=False),
    
    # Navigation bar
    dbc.NavbarSimple(
        children=[
            dbc.NavItem(dbc.NavLink("Simulations", href="/dashboard/simulations")),
            dbc.NavItem(dbc.NavLink("Chain-of-Thought", href="/dashboard/cot")),
            dbc.NavItem(dbc.NavLink("Node Graph", href="/dashboard/nodes")),
            dbc.NavItem(dbc.NavLink("VECTOR", href="/dashboard/vector")),
            dbc.NavItem(dbc.NavLink("Performance", href="/dashboard/performance")),
            dbc.NavItem(dbc.NavLink("Evolution", href="/dashboard/evolution")),
        ],
        brand="Physics AI Dashboard",
        brand_href="/dashboard",
        color="primary",
        dark=True,
    ),
    
    # Content area
    html.Div(id='page-content', style={'margin-top': '20px'}),
    
    # Store for real-time data
    dcc.Store(id='store-simulation-data'),
    dcc.Store(id='store-cot-data'),
    dcc.Store(id='store-node-data'),
    
    # Interval component for updates
    dcc.Interval(
        id='interval-component',
        interval=2000,  # Update every 2 seconds
        n_intervals=0
    ),
], fluid=True)

# Validation layout to allow callbacks to reference components in other pages
app.validation_layout = html.Div([
    app.layout,
    create_simulation_view(),
    create_cot_view(),
    create_node_graph_view(),
    create_vector_view(),
    create_performance_view(),
    create_evolution_view(),
])


@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    """Route to appropriate page based on URL."""
    if pathname in [None, '/', '/dashboard', '/dashboard/']:
        return html.Div([
            html.H1("Physics AI Dashboard"),
            html.P("Welcome to the Physics AI Dashboard. Select a view from the navigation bar."),
            dbc.Card([
                dbc.CardBody([
                    html.H4("System Overview"),
                    html.P("Real-time monitoring and visualization of the Physics AI system."),
                    html.Ul([
                        html.Li("Simulations: Real-time physics simulation visualization"),
                        html.Li("Chain-of-Thought: Interactive CoT tree display"),
                        html.Li("Node Graph: Nodal vectorization graph visualization"),
                        html.Li("VECTOR: VECTOR framework metrics and statistics"),
                        html.Li("Performance: System performance monitoring"),
                        html.Li("Evolution: Code evolution history and tracking"),
                    ])
                ])
            ])
        ])
    
    elif pathname == '/dashboard/simulations':
        from dashboard.components.simulation_view import create_simulation_view
        return create_simulation_view()
    
    elif pathname == '/dashboard/cot':
        from dashboard.components.cot_view import create_cot_view
        return create_cot_view()
    
    elif pathname == '/dashboard/nodes':
        from dashboard.components.node_graph_view import create_node_graph_view
        return create_node_graph_view()
    
    elif pathname == '/dashboard/vector':
        from dashboard.components.vector_view import create_vector_view
        return create_vector_view()
    
    elif pathname == '/dashboard/performance':
        from dashboard.components.performance_view import create_performance_view
        return create_performance_view()
    
    elif pathname == '/dashboard/evolution':
        from dashboard.components.evolution_view import create_evolution_view
        return create_evolution_view()
    
    else:
        return html.Div([
            html.H1("404 - Page Not Found"),
            html.P(f"Path '{pathname}' not found.")
        ])

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5002/api/v1/substrate")


def _fetch_json(path: str, default=None):
    try:
        resp = requests.get(f"{BACKEND_URL}{path}", timeout=3)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return default if default is not None else {}


# ---------------------------------------------------------------------------
# Callbacks
# ---------------------------------------------------------------------------

@app.callback(
    Output('node-graph-statistics', 'children'),
    Output('node-graph-display', 'children'),
    Output('node-details', 'children'),
    Input('interval-component', 'n_intervals'),
)
def update_node_graph(_):
    stats = _fetch_json("/graph/stats", default={})
    edges = _fetch_json("/graph/edges", default={"edges": []})
    formulas = _fetch_json("/formulas", default={"formulas": []})

    stats_block = html.Pre(json.dumps(stats, indent=2))
    display_block = html.Pre(f"Edges: {len(edges.get('edges', []))}")
    detail_items = formulas.get("formulas", [])[:5]
    details_block = html.Ul([html.Li(f"{f.get('name')} ({f.get('domain')})") for f in detail_items]) if detail_items else "No formulas loaded"
    return stats_block, display_block, details_block


@app.callback(
    Output('performance-metrics-graph', 'figure'),
    Output('performance-alerts', 'children'),
    Output('performance-statistics', 'children'),
    Input('interval-component', 'n_intervals'),
)
def update_performance(_):
    stats = _fetch_json("/stats", default={})
    graph_stats = stats.get("graph", {})
    traces_stats = stats.get("traces", {})
    evolution_stats = stats.get("evolution", {})

    labels = ["Formulas", "Edges", "Traces", "Actions"]
    values = [
        graph_stats.get("total_formulas", 0),
        graph_stats.get("total_edges", 0),
        traces_stats.get("count", 0),
        evolution_stats.get("total_actions", 0),
    ]
    fig = go.Figure(data=[go.Bar(x=labels, y=values, marker_color="steelblue")])
    fig.update_layout(title="System Metrics", yaxis_title="Count")

    alerts = html.Ul([
        html.Li(f"Evolution success rate: {evolution_stats.get('success_rate', 0):.2f}") if evolution_stats else html.Li("No evolution data"),
        html.Li(f"Trace success rate: {traces_stats.get('success_rate', 0):.2f}") if traces_stats else html.Li("No trace data"),
    ])
    stats_block = html.Pre(json.dumps(stats, indent=2))
    return fig, alerts, stats_block


@app.callback(
    Output('evolution-timeline', 'children'),
    Output('evolution-statistics', 'children'),
    Output('evolution-recent', 'children'),
    Input('interval-component', 'n_intervals'),
)
def update_evolution(_):
    stats = _fetch_json("/evolution/stats", default={})
    results = _fetch_json("/evolution/results", default={"results": []})

    timeline_items = []
    for r in results.get("results", [])[:5]:
        timeline_items.append(html.Li(f"{r.get('cycle_id')} - actions: {r.get('actions_applied')} succeeded: {r.get('actions_succeeded')}"))
    timeline = html.Ul(timeline_items) if timeline_items else "No evolution runs yet"

    stats_block = html.Pre(json.dumps(stats, indent=2))
    recent_block = html.Pre(json.dumps(results.get("results", [])[:3], indent=2))
    return timeline, stats_block, recent_block


@app.callback(
    Output('vector-delta-factors', 'children'),
    Output('vector-variance-graph', 'figure'),
    Output('vector-statistics', 'children'),
    Input('interval-component', 'n_intervals'),
)
def update_vector(_):
    critics = _fetch_json("/critics/stats", default={})

    # Simple placeholder graph using critic analysis counts
    logic_count = critics.get("logic_critic", {}).get("analysis_count", 0)
    code_count = critics.get("code_critic", {}).get("analysis_count", 0)
    meta_count = critics.get("meta_critic", {}).get("tracked_critics", 0)
    fig = go.Figure(data=[go.Bar(x=["Logic", "Code", "Meta"], y=[logic_count, code_count, meta_count], marker_color="purple")])
    fig.update_layout(title="Critic Activity", yaxis_title="Count")

    delta_block = html.Pre(json.dumps(critics, indent=2))
    stats_block = html.Pre("VECTOR metrics are placeholder; connect to backend metrics as available.")
    return delta_block, fig, stats_block


@app.callback(
    Output('cot-tree-display', 'children'),
    Output('cot-statistics', 'children'),
    Output('cot-recent-steps', 'children'),
    Input('interval-component', 'n_intervals'),
)
def update_cot(_):
    traces = _fetch_json("/traces", default={"traces": []})
    count = traces.get("count", 0)
    recent = traces.get("traces", [])[:3]
    tree = html.Pre(json.dumps(recent, indent=2)) if recent else "No traces yet"
    stats_block = html.Div([
        html.P(f"Recent traces: {count}"),
    ])
    recent_block = html.Pre(json.dumps(recent, indent=2)) if recent else "No recent steps"
    return tree, stats_block, recent_block


@app.callback(
    Output('simulation-list', 'children'),
    Output('simulation-graph', 'figure'),
    Output('simulation-parameters', 'children'),
    Input('interval-component', 'n_intervals'),
)
def update_simulation(_):
    graph_stats = _fetch_json("/graph/stats", default={})
    list_block = html.Ul([
        html.Li(f"Formulas: {graph_stats.get('total_formulas', 0)}"),
        html.Li(f"Edges: {graph_stats.get('total_edges', 0)}"),
    ])
    # Simple quadratic as placeholder
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0, 1, 2, 3, 4], y=[0, 1, 4, 9, 16], mode='lines+markers', name='Sample'))
    fig.update_layout(title="Sample Simulation", xaxis_title="t", yaxis_title="value")
    params_block = html.Pre(json.dumps(graph_stats, indent=2))
    return list_block, fig, params_block

def create_app():
    """
    Create and return Dash application.
    
    Returns:
        Dash application instance
    """
    logger.log("Dash dashboard application created", level="INFO")
    return app


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8052)

