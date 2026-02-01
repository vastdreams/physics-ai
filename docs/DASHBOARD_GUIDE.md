# Dashboard Guide

## Overview

The Physics AI Dashboard is a real-time visualization system built with Dash, providing interactive views of simulations, chain-of-thought logs, nodal graphs, VECTOR metrics, performance monitoring, and evolution history.

## Architecture

### Technology Stack
- **Dash**: Web framework for Python
- **Dash Bootstrap Components**: UI components
- **Plotly**: Interactive charts
- **Flask-SocketIO**: WebSocket support for real-time updates

### Component Structure

```
dashboard/
├── app.py                 # Main Dash application
└── components/
    ├── simulation_view.py    # Simulation visualization
    ├── cot_view.py           # Chain-of-thought display
    ├── node_graph_view.py    # Nodal graph visualization
    ├── vector_view.py        # VECTOR metrics
    ├── performance_view.py  # Performance monitoring
    └── evolution_view.py     # Evolution history
```

## Views

### 1. Simulation View
Real-time physics simulation visualization.

**Features**:
- Active simulations list
- Simulation visualization (Plotly charts)
- Simulation parameters display
- Start new simulation button

**URL**: `/dashboard/simulations`

**Components**:
- Simulation list card
- Simulation graph (Plotly)
- Parameters card

### 2. Chain-of-Thought View
Interactive CoT tree display.

**Features**:
- CoT tree visualization
- CoT statistics
- Recent steps display
- Refresh button

**URL**: `/dashboard/cot`

**Components**:
- CoT tree card
- Statistics card
- Recent steps card

### 3. Node Graph View
Nodal vectorization graph visualization.

**Features**:
- Graph visualization
- Graph statistics
- Node details
- Refresh graph button

**URL**: `/dashboard/nodes`

**Components**:
- Graph display card
- Statistics card
- Node details card

### 4. VECTOR View
VECTOR framework metrics and statistics.

**Features**:
- Delta factors display
- Variance statistics graph
- VECTOR statistics
- Real-time updates

**URL**: `/dashboard/vector`

**Components**:
- Delta factors card
- Variance graph (Plotly)
- Statistics card

### 5. Performance View
System performance monitoring.

**Features**:
- Performance metrics graph
- Recent alerts
- Performance statistics
- Real-time updates

**URL**: `/dashboard/performance`

**Components**:
- Metrics graph (Plotly)
- Alerts card
- Statistics card

### 6. Evolution View
Code evolution history and tracking.

**Features**:
- Evolution timeline
- Evolution statistics
- Recent evolutions
- History tracking

**URL**: `/dashboard/evolution`

**Components**:
- Timeline card
- Statistics card
- Recent evolutions card

## Running the Dashboard

### Local Development

```bash
# Start dashboard
python dashboard/app.py

# Dashboard will be available at
# http://localhost:8050
```

### With Flask API

```bash
# Start Flask API (port 5000)
python api/app.py

# Start Dashboard (port 8050)
python dashboard/app.py
```

## WebSocket Integration

The dashboard supports real-time updates via WebSocket.

### Event Types

- `simulation_update` - Simulation data updates
- `cot_update` - Chain-of-thought updates
- `node_update` - Node graph updates
- `performance_update` - Performance metrics
- `vector_update` - VECTOR framework updates
- `evolution_update` - Evolution updates
- `context_update` - Context memory updates

### Client-Side Integration

```javascript
// Connect to WebSocket
const socket = io('http://localhost:5000');

// Subscribe to events
socket.emit('subscribe', {
    event_types: ['simulation_update', 'cot_update']
});

// Listen for updates
socket.on('simulation_update', (data) => {
    // Update dashboard
    updateSimulationGraph(data);
});
```

## API Integration

### Fetching Data

```python
import requests

# Get simulation data
response = requests.get('http://localhost:5000/api/v1/simulate')

# Get CoT tree
response = requests.get('http://localhost:5000/api/v1/cot/tree')

# Get node graph
response = requests.get('http://localhost:5000/api/v1/nodes/graph/statistics')
```

### Real-Time Updates

The dashboard uses WebSocket for real-time updates. Data is automatically pushed from the server when changes occur.

## Customization

### Adding New Views

1. Create component file in `dashboard/components/`
2. Implement `create_*_view()` function
3. Add route in `dashboard/app.py`
4. Add navigation link

Example:
```python
# dashboard/components/custom_view.py
def create_custom_view():
    return dbc.Container([
        html.H2("Custom View"),
        # ... components ...
    ], fluid=True)

# dashboard/app.py
elif pathname == '/dashboard/custom':
    from dashboard.components.custom_view import create_custom_view
    return create_custom_view()
```

### Styling

The dashboard uses Bootstrap for styling. Customize by:
- Modifying `external_stylesheets` in `app.py`
- Using Dash Bootstrap Components
- Adding custom CSS

## Performance Optimization

1. **Lazy Loading**: Load data only when view is accessed
2. **Caching**: Cache frequently accessed data
3. **Debouncing**: Debounce rapid updates
4. **Pagination**: Paginate large datasets
5. **WebSocket**: Use WebSocket for real-time updates instead of polling

## Best Practices

1. **Component Isolation**: Keep components independent
2. **Error Handling**: Handle API errors gracefully
3. **Loading States**: Show loading indicators
4. **Responsive Design**: Make dashboard mobile-friendly
5. **Accessibility**: Follow accessibility guidelines

## Troubleshooting

### Dashboard Not Loading
- Check if port 8050 is available
- Verify Dash installation
- Check for import errors

### WebSocket Not Connecting
- Verify Flask-SocketIO is running
- Check CORS settings
- Verify WebSocket endpoint

### Data Not Updating
- Check API endpoints
- Verify WebSocket connection
- Check browser console for errors

## Future Enhancements

1. **Advanced Visualizations**: 3D graphs, interactive plots
2. **Custom Dashboards**: User-configurable layouts
3. **Export Features**: PDF/PNG export
4. **Mobile App**: Native mobile application
5. **Collaboration**: Multi-user dashboards

