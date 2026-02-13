/**
 * PATH: frontend/src/components/simulations/ProjectileSimulation.jsx
 * PURPOSE: Projectile motion physics simulation
 * 
 * WHY: Demonstrates kinematics and the independence
 * of horizontal and vertical motion.
 * 
 * PHYSICS:
 * - x(t) = v₀cos(θ)t
 * - y(t) = v₀sin(θ)t - ½gt²
 * - Range R = v₀²sin(2θ)/g
 * - Max height H = v₀²sin²(θ)/(2g)
 */

import { useState, useCallback, useRef } from 'react';
import PhysicsCanvas, { createBodies } from './PhysicsCanvas';
import Matter from 'matter-js';
import { Target, Crosshair } from 'lucide-react';
import { clsx } from 'clsx';

const { Composite, Body, Events } = Matter;

/**
 * ProjectileSimulation - Interactive projectile motion demonstration
 * 
 * @param {Object} props
 * @param {number} props.initialVelocity - Launch velocity (default: 15)
 * @param {number} props.initialAngle - Launch angle in degrees (default: 45)
 * @param {number} props.projectileRadius - Ball radius (default: 15)
 */
export default function ProjectileSimulation({
  initialVelocity = 15,
  initialAngle = 45,
  projectileRadius = 15,
  className,
}) {
  const [velocity, setVelocity] = useState(initialVelocity);
  const [angle, setAngle] = useState(initialAngle);
  const [trajectory, setTrajectory] = useState([]);
  const projectileRef = useRef(null);
  const engineRef = useRef(null);
  
  const setup = useCallback((engine, render, { Bodies, Composite }) => {
    const width = render.options.width;
    const height = render.options.height;
    
    engineRef.current = engine;
    
    // Launch platform
    const platformWidth = 80;
    const platformHeight = 20;
    const platform = Bodies.rectangle(
      60, 
      height - 50, 
      platformWidth, 
      platformHeight, 
      {
        isStatic: true,
        render: {
          fillStyle: '#475569',
          strokeStyle: '#64748b',
          lineWidth: 2,
        },
      }
    );
    
    // Create angled launcher visual
    const launcherLength = 60;
    const launcherAngleRad = (angle * Math.PI) / 180;
    const launcherX = 60 + (launcherLength / 2) * Math.cos(launcherAngleRad);
    const launcherY = height - 70 - (launcherLength / 2) * Math.sin(launcherAngleRad);
    
    const launcher = Bodies.rectangle(
      launcherX,
      launcherY,
      launcherLength,
      12,
      {
        isStatic: true,
        angle: -launcherAngleRad,
        render: {
          fillStyle: '#f97316',
          strokeStyle: '#ea580c',
          lineWidth: 2,
        },
      }
    );
    
    // Create projectile
    const projectile = Bodies.circle(
      60 + launcherLength * Math.cos(launcherAngleRad),
      height - 70 - launcherLength * Math.sin(launcherAngleRad),
      projectileRadius,
      {
        restitution: 0.6,
        friction: 0.01,
        frictionAir: 0.001,
        render: {
          fillStyle: '#ef4444',
          strokeStyle: '#dc2626',
          lineWidth: 2,
        },
      }
    );
    
    projectileRef.current = projectile;
    
    // Target
    const targetX = width - 100;
    const target = Bodies.rectangle(
      targetX,
      height - 80,
      40,
      80,
      {
        isStatic: true,
        render: {
          fillStyle: '#22c55e',
          strokeStyle: '#16a34a',
          lineWidth: 2,
        },
      }
    );
    
    // Add some obstacles
    const obstacle1 = Bodies.rectangle(
      width / 2,
      height - 150,
      20,
      100,
      {
        isStatic: true,
        render: {
          fillStyle: '#64748b',
          strokeStyle: '#94a3b8',
          lineWidth: 1,
        },
      }
    );
    
    Composite.add(engine.world, [platform, launcher, projectile, target, obstacle1]);
    
    // Track trajectory
    const trajectoryPoints = [];
    Events.on(engine, 'afterUpdate', () => {
      if (projectileRef.current) {
        const pos = projectileRef.current.position;
        trajectoryPoints.push({ x: pos.x, y: pos.y });
        
        // Keep only last 100 points
        if (trajectoryPoints.length > 100) {
          trajectoryPoints.shift();
        }
      }
    });
    
  }, [angle, projectileRadius]);
  
  // Launch the projectile
  const handleLaunch = useCallback(() => {
    if (!projectileRef.current || !engineRef.current) return;
    
    const angleRad = (angle * Math.PI) / 180;
    const vx = velocity * Math.cos(angleRad);
    const vy = -velocity * Math.sin(angleRad); // Negative because y increases downward
    
    Body.setVelocity(projectileRef.current, { x: vx, y: vy });
  }, [velocity, angle]);
  
  // Reset projectile position
  const handleReset = useCallback(() => {
    if (!projectileRef.current) return;
    
    const launcherLength = 60;
    const angleRad = (angle * Math.PI) / 180;
    
    Body.setPosition(projectileRef.current, {
      x: 60 + launcherLength * Math.cos(angleRad),
      y: 450 - 70 - launcherLength * Math.sin(angleRad),
    });
    Body.setVelocity(projectileRef.current, { x: 0, y: 0 });
    Body.setAngularVelocity(projectileRef.current, 0);
  }, [angle]);
  
  return (
    <div className={className}>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-slate-800 mb-1">Projectile Motion</h3>
        <p className="text-sm text-slate-600">
          Adjust velocity and angle, then launch!
        </p>
      </div>
      
      {/* Controls */}
      <div className="flex flex-wrap gap-6 mb-4 p-4 bg-slate-50 rounded-lg">
        {/* Velocity slider */}
        <div className="flex items-center gap-3">
          <label className="text-sm text-slate-600 w-20">Velocity</label>
          <input
            type="range"
            min="5"
            max="25"
            step="1"
            value={velocity}
            onChange={(e) => setVelocity(parseFloat(e.target.value))}
            className="w-32 accent-orange-500"
          />
          <span className="text-sm text-slate-700 w-16">{velocity} m/s</span>
        </div>
        
        {/* Angle slider */}
        <div className="flex items-center gap-3">
          <label className="text-sm text-slate-600 w-20">Angle</label>
          <input
            type="range"
            min="10"
            max="80"
            step="5"
            value={angle}
            onChange={(e) => setAngle(parseFloat(e.target.value))}
            className="w-32 accent-orange-500"
          />
          <span className="text-sm text-slate-700 w-16">{angle}°</span>
        </div>
        
        {/* Launch button */}
        <button
          onClick={handleLaunch}
          className="px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors flex items-center gap-2"
        >
          <Target size={16} />
          Launch
        </button>
      </div>
      
      {/* Physics info */}
      <div className="mb-4 p-3 bg-blue-50 rounded-lg text-sm">
        <div className="grid grid-cols-2 gap-4 text-slate-700">
          <div>
            <span className="text-slate-500">Horizontal velocity:</span>{' '}
            {(velocity * Math.cos(angle * Math.PI / 180)).toFixed(2)} m/s
          </div>
          <div>
            <span className="text-slate-500">Vertical velocity:</span>{' '}
            {(velocity * Math.sin(angle * Math.PI / 180)).toFixed(2)} m/s
          </div>
          <div>
            <span className="text-slate-500">Max height:</span>{' '}
            {((velocity * velocity * Math.sin(angle * Math.PI / 180) ** 2) / (2 * 9.81)).toFixed(2)} m
          </div>
          <div>
            <span className="text-slate-500">Range:</span>{' '}
            {((velocity * velocity * Math.sin(2 * angle * Math.PI / 180)) / 9.81).toFixed(2)} m
          </div>
        </div>
      </div>
      
      <PhysicsCanvas
        setup={setup}
        width={700}
        height={500}
        options={{
          gravity: { y: 1, scale: 0.001 }
        }}
      />
    </div>
  );
}
