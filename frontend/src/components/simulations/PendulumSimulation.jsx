/**
 * PATH: frontend/src/components/simulations/PendulumSimulation.jsx
 * PURPOSE: Simple pendulum physics simulation
 * 
 * WHY: Demonstrates fundamental harmonic motion concepts
 * through interactive visualization.
 * 
 * PHYSICS:
 * - Period T = 2π√(L/g) for small angles
 * - Conservation of energy
 * - Damping effects
 */

import { useCallback } from 'react';
import PhysicsCanvas, { createBodies } from './PhysicsCanvas';
import Matter from 'matter-js';

const { Constraint, Composite, Body } = Matter;

/**
 * PendulumSimulation - Interactive pendulum demonstration
 * 
 * @param {Object} props
 * @param {number} props.length - Pendulum length (default: 200)
 * @param {number} props.bobRadius - Bob radius (default: 25)
 * @param {number} props.initialAngle - Initial angle in degrees (default: 45)
 * @param {number} props.damping - Air resistance (default: 0.001)
 */
export default function PendulumSimulation({
  length = 200,
  bobRadius = 25,
  initialAngle = 45,
  damping = 0.001,
  className,
}) {
  const setup = useCallback((engine, render, { Bodies, Composite }) => {
    const width = render.options.width;
    const height = render.options.height;
    
    // Pivot point (fixed anchor)
    const pivotX = width / 2;
    const pivotY = 80;
    
    // Calculate bob position based on initial angle
    const angleRad = (initialAngle * Math.PI) / 180;
    const bobX = pivotX + length * Math.sin(angleRad);
    const bobY = pivotY + length * Math.cos(angleRad);
    
    // Create anchor point (static)
    const anchor = Bodies.circle(pivotX, pivotY, 8, {
      isStatic: true,
      render: {
        fillStyle: '#64748b',
        strokeStyle: '#94a3b8',
        lineWidth: 2,
      },
    });
    
    // Create pendulum bob
    const bob = Bodies.circle(bobX, bobY, bobRadius, {
      restitution: 0.9,
      friction: 0.0001,
      frictionAir: damping,
      render: {
        fillStyle: '#f97316',
        strokeStyle: '#ea580c',
        lineWidth: 3,
      },
    });
    
    // Create the rope/rod constraint
    const rope = Constraint.create({
      bodyA: anchor,
      bodyB: bob,
      length: length,
      stiffness: 1,
      render: {
        strokeStyle: '#94a3b8',
        lineWidth: 3,
        type: 'line',
      },
    });
    
    // Add to world
    Composite.add(engine.world, [anchor, bob, rope]);
    
    // Add trace effect (optional - show path)
    const tracePoints = [];
    Matter.Events.on(engine, 'afterUpdate', () => {
      // Could add path tracing here
    });
    
  }, [length, bobRadius, initialAngle, damping]);
  
  return (
    <div className={className}>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-slate-800 mb-1">Simple Pendulum</h3>
        <p className="text-sm text-slate-600">
          Drag the bob to set initial position. Period T = 2π√(L/g)
        </p>
      </div>
      <PhysicsCanvas
        setup={setup}
        width={600}
        height={500}
        options={{
          gravity: { y: 1, scale: 0.001 }
        }}
      />
    </div>
  );
}
