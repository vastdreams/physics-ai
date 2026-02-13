/**
 * PATH: frontend/src/components/simulations/PhysicsCanvas.jsx
 * PURPOSE: 2D physics simulation canvas using Matter.js
 * 
 * WHY: Interactive physics simulations help users understand
 * physical concepts through visual, hands-on exploration.
 * 
 * FEATURES:
 * - Real-time 2D physics simulation
 * - Play/pause/reset controls
 * - Configurable gravity and time scale
 * - Interactive object creation
 * - Customizable world setup via props
 */

import { useEffect, useRef, useState, useCallback } from 'react';
import Matter from 'matter-js';
import { 
  Play, 
  Pause, 
  RotateCcw, 
  Settings,
  ChevronDown,
  ChevronUp,
  Maximize2,
  Minimize2
} from 'lucide-react';
import { clsx } from 'clsx';

const {
  Engine,
  Render,
  Runner,
  Bodies,
  Composite,
  Mouse,
  MouseConstraint,
  Events,
  World,
} = Matter;

/**
 * PhysicsCanvas - Interactive 2D physics simulation
 * 
 * @param {Object} props
 * @param {Function} props.setup - Function to set up initial world state
 * @param {Object} props.options - Engine options (gravity, timing)
 * @param {number} props.width - Canvas width (default: 800)
 * @param {number} props.height - Canvas height (default: 600)
 * @param {boolean} props.wireframes - Show wireframe mode (default: false)
 * @param {boolean} props.showControls - Show control panel (default: true)
 * @param {string} props.className - Additional CSS classes
 */
export default function PhysicsCanvas({
  setup,
  options = {},
  width = 800,
  height = 600,
  wireframes = false,
  showControls = true,
  className,
}) {
  const canvasRef = useRef(null);
  const engineRef = useRef(null);
  const renderRef = useRef(null);
  const runnerRef = useRef(null);
  
  const [isRunning, setIsRunning] = useState(true);
  const [showSettings, setShowSettings] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const [gravity, setGravity] = useState(options.gravity?.y ?? 1);
  const [timeScale, setTimeScale] = useState(options.timing?.timeScale ?? 1);
  
  /**
   * Initialize Matter.js engine and renderer
   */
  const initEngine = useCallback(() => {
    if (!canvasRef.current) return;
    
    // Create engine with configurable gravity
    const engine = Engine.create({
      gravity: {
        x: options.gravity?.x ?? 0,
        y: gravity,
        scale: options.gravity?.scale ?? 0.001,
      },
    });
    
    engine.timing.timeScale = timeScale;
    
    // Create renderer
    const render = Render.create({
      element: canvasRef.current,
      engine: engine,
      options: {
        width: isExpanded ? window.innerWidth - 100 : width,
        height: isExpanded ? window.innerHeight - 200 : height,
        wireframes: wireframes,
        background: '#1e293b',
        wireframeBackground: '#0f172a',
        showVelocity: false,
        showAngleIndicator: false,
      },
    });
    
    // Create runner for physics updates
    const runner = Runner.create();
    
    // Add mouse interaction
    const mouse = Mouse.create(render.canvas);
    const mouseConstraint = MouseConstraint.create(engine, {
      mouse: mouse,
      constraint: {
        stiffness: 0.2,
        render: {
          visible: true,
          strokeStyle: '#f97316',
          lineWidth: 2,
        },
      },
    });
    
    Composite.add(engine.world, mouseConstraint);
    render.mouse = mouse;
    
    // Add ground and walls
    const wallOptions = { 
      isStatic: true, 
      render: { 
        fillStyle: '#334155',
        strokeStyle: '#475569',
        lineWidth: 1,
      } 
    };
    
    const currentWidth = isExpanded ? window.innerWidth - 100 : width;
    const currentHeight = isExpanded ? window.innerHeight - 200 : height;
    
    Composite.add(engine.world, [
      // Ground
      Bodies.rectangle(currentWidth / 2, currentHeight + 30, currentWidth + 100, 60, wallOptions),
      // Left wall
      Bodies.rectangle(-30, currentHeight / 2, 60, currentHeight + 100, wallOptions),
      // Right wall
      Bodies.rectangle(currentWidth + 30, currentHeight / 2, 60, currentHeight + 100, wallOptions),
      // Ceiling (optional)
      Bodies.rectangle(currentWidth / 2, -30, currentWidth + 100, 60, wallOptions),
    ]);
    
    // Run custom setup if provided
    if (setup) {
      setup(engine, render, { Bodies, Composite, Matter });
    }
    
    // Store references
    engineRef.current = engine;
    renderRef.current = render;
    runnerRef.current = runner;
    
    // Start
    Render.run(render);
    Runner.run(runner, engine);
    
  }, [setup, options, width, height, wireframes, gravity, timeScale, isExpanded]);
  
  /**
   * Cleanup Matter.js instances
   */
  const cleanup = useCallback(() => {
    if (renderRef.current) {
      Render.stop(renderRef.current);
      if (renderRef.current.canvas) {
        renderRef.current.canvas.remove();
      }
      renderRef.current.textures = {};
    }
    if (runnerRef.current) {
      Runner.stop(runnerRef.current);
    }
    if (engineRef.current) {
      World.clear(engineRef.current.world, false);
      Engine.clear(engineRef.current);
    }
  }, []);
  
  /**
   * Reset simulation
   */
  const handleReset = useCallback(() => {
    cleanup();
    initEngine();
    setIsRunning(true);
  }, [cleanup, initEngine]);
  
  /**
   * Toggle play/pause
   */
  const handlePlayPause = useCallback(() => {
    if (!engineRef.current) return;
    
    if (isRunning) {
      engineRef.current.timing.timeScale = 0;
    } else {
      engineRef.current.timing.timeScale = timeScale;
    }
    setIsRunning(!isRunning);
  }, [isRunning, timeScale]);
  
  /**
   * Update gravity
   */
  const handleGravityChange = useCallback((newGravity) => {
    setGravity(newGravity);
    if (engineRef.current) {
      engineRef.current.gravity.y = newGravity;
    }
  }, []);
  
  /**
   * Update time scale
   */
  const handleTimeScaleChange = useCallback((newTimeScale) => {
    setTimeScale(newTimeScale);
    if (engineRef.current && isRunning) {
      engineRef.current.timing.timeScale = newTimeScale;
    }
  }, [isRunning]);
  
  // Initialize on mount
  useEffect(() => {
    initEngine();
    return cleanup;
  }, [initEngine, cleanup]);
  
  return (
    <div className={clsx(
      'physics-canvas rounded-xl overflow-hidden border border-slate-700 bg-slate-900',
      isExpanded && 'fixed inset-4 z-50',
      className
    )}>
      {/* Header */}
      {showControls && (
        <div className="flex items-center justify-between px-4 py-2 bg-slate-800 border-b border-slate-700">
          <div className="flex items-center gap-2">
            <span className="text-sm font-medium text-slate-300">Physics Simulation</span>
          </div>
          
          <div className="flex items-center gap-2">
            {/* Play/Pause */}
            <button
              onClick={handlePlayPause}
              className={clsx(
                'p-1.5 rounded transition-colors',
                isRunning 
                  ? 'bg-amber-500/20 text-amber-400 hover:bg-amber-500/30'
                  : 'bg-green-500/20 text-green-400 hover:bg-green-500/30'
              )}
              title={isRunning ? 'Pause' : 'Play'}
            >
              {isRunning ? <Pause size={16} /> : <Play size={16} />}
            </button>
            
            {/* Reset */}
            <button
              onClick={handleReset}
              className="p-1.5 rounded bg-slate-700 text-slate-300 hover:bg-slate-600 transition-colors"
              title="Reset"
            >
              <RotateCcw size={16} />
            </button>
            
            {/* Settings */}
            <button
              onClick={() => setShowSettings(!showSettings)}
              className={clsx(
                'p-1.5 rounded transition-colors',
                showSettings 
                  ? 'bg-orange-500/20 text-orange-400'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              )}
              title="Settings"
            >
              <Settings size={16} />
            </button>
            
            {/* Expand */}
            <button
              onClick={() => setIsExpanded(!isExpanded)}
              className="p-1.5 rounded bg-slate-700 text-slate-300 hover:bg-slate-600 transition-colors"
              title={isExpanded ? 'Minimize' : 'Expand'}
            >
              {isExpanded ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
            </button>
          </div>
        </div>
      )}
      
      {/* Settings Panel */}
      {showSettings && (
        <div className="px-4 py-3 bg-slate-800/50 border-b border-slate-700 flex flex-wrap gap-6">
          {/* Gravity slider */}
          <div className="flex items-center gap-3">
            <label className="text-xs text-slate-400 w-16">Gravity</label>
            <input
              type="range"
              min="0"
              max="3"
              step="0.1"
              value={gravity}
              onChange={(e) => handleGravityChange(parseFloat(e.target.value))}
              className="w-24 accent-orange-500"
            />
            <span className="text-xs text-slate-300 w-8">{gravity.toFixed(1)}</span>
          </div>
          
          {/* Time scale slider */}
          <div className="flex items-center gap-3">
            <label className="text-xs text-slate-400 w-16">Speed</label>
            <input
              type="range"
              min="0.1"
              max="3"
              step="0.1"
              value={timeScale}
              onChange={(e) => handleTimeScaleChange(parseFloat(e.target.value))}
              className="w-24 accent-orange-500"
            />
            <span className="text-xs text-slate-300 w-8">{timeScale.toFixed(1)}x</span>
          </div>
        </div>
      )}
      
      {/* Canvas Container */}
      <div 
        ref={canvasRef} 
        className="physics-canvas-container"
        style={{ 
          width: isExpanded ? 'calc(100vw - 100px)' : width,
          height: isExpanded ? 'calc(100vh - 200px)' : height,
        }}
      />
    </div>
  );
}

/**
 * Helper function to create common physics bodies
 */
export const createBodies = {
  /**
   * Create a ball
   */
  ball: (x, y, radius, options = {}) => Bodies.circle(x, y, radius, {
    restitution: options.restitution ?? 0.8,
    friction: options.friction ?? 0.005,
    render: {
      fillStyle: options.color ?? '#f97316',
      strokeStyle: '#ea580c',
      lineWidth: 2,
    },
    ...options,
  }),
  
  /**
   * Create a box
   */
  box: (x, y, width, height, options = {}) => Bodies.rectangle(x, y, width, height, {
    restitution: options.restitution ?? 0.6,
    friction: options.friction ?? 0.1,
    render: {
      fillStyle: options.color ?? '#3b82f6',
      strokeStyle: '#2563eb',
      lineWidth: 2,
    },
    ...options,
  }),
  
  /**
   * Create a polygon
   */
  polygon: (x, y, sides, radius, options = {}) => Bodies.polygon(x, y, sides, radius, {
    restitution: options.restitution ?? 0.7,
    friction: options.friction ?? 0.05,
    render: {
      fillStyle: options.color ?? '#a855f7',
      strokeStyle: '#9333ea',
      lineWidth: 2,
    },
    ...options,
  }),
  
  /**
   * Create a static platform
   */
  platform: (x, y, width, height, angle = 0, options = {}) => Bodies.rectangle(x, y, width, height, {
    isStatic: true,
    angle: angle,
    render: {
      fillStyle: options.color ?? '#475569',
      strokeStyle: '#64748b',
      lineWidth: 1,
    },
    ...options,
  }),
};
