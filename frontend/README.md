# Beyond Frontier Frontend

A modern web interface for managing and interacting with the Beyond Frontier system, inspired by Notion, Cursor, and ChatGPT.

## Features

- **Dashboard**: System overview with stats, quick actions, and real-time status
- **AI Chat**: ChatGPT-style conversational interface for physics queries
- **Simulations**: Run and visualize physics simulations with interactive controls
- **Equations**: Symbolic equation solver with step-by-step solutions
- **Rules**: Manage inference rules with pattern matching
- **Evolution**: Track AI self-evolution and code improvements
- **Reasoning**: Explore four types of logical reasoning
- **Logs**: Real-time system logs with filtering
- **Metrics**: Performance analytics and monitoring

## Tech Stack

- **React** - UI framework
- **Vite** - Build tool and dev server
- **Tailwind CSS v4** - Styling
- **React Router** - Navigation
- **Recharts** - Data visualization
- **Lucide React** - Icons
- **Radix UI** - Accessible components

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The app will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

Build output will be in the `dist/` directory.

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── layout/         # Layout components (Sidebar, Header)
│   │   ├── chat/           # Chat interface components
│   │   ├── dashboard/      # Dashboard components
│   │   ├── simulation/     # Simulation components
│   │   ├── rules/          # Rule management components
│   │   └── common/         # Shared components
│   ├── pages/              # Page components
│   │   ├── Dashboard.jsx
│   │   ├── Chat.jsx
│   │   ├── Simulations.jsx
│   │   ├── Equations.jsx
│   │   ├── Rules.jsx
│   │   ├── Evolution.jsx
│   │   ├── Reasoning.jsx
│   │   ├── Logs.jsx
│   │   ├── Metrics.jsx
│   │   └── Settings.jsx
│   ├── hooks/              # Custom React hooks
│   ├── services/           # API services
│   ├── App.jsx             # Main app component
│   ├── main.jsx            # Entry point
│   └── index.css           # Global styles
├── index.html
├── vite.config.js
├── tailwind.config.js
└── package.json
```

## API Connection

The frontend connects to the Beyond Frontier backend API at `http://localhost:5002` by default.

To start the backend:

```bash
# From project root
python -m api.app
```

## Design System

### Colors

- **Dark Theme**: Custom dark palette inspired by Cursor IDE
- **Accent Colors**: Primary green (#10a37f), Purple, Blue

### Components

- **Cards**: Container with border and rounded corners
- **Buttons**: Primary, Secondary, Ghost variants
- **Inputs**: Dark styled with focus states
- **Badges**: Status indicators with color coding

## Contributing

See the main project [CONTRIBUTING.md](../CONTRIBUTING.md) for guidelines.
