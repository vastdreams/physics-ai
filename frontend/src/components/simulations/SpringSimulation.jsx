/**
 * PATH: frontend/src/components/simulations/SpringSimulation.jsx
 * PURPOSE: Spring/mass oscillation physics simulation
 * 
 * WHY: Demonstrates Hooke's law and simple harmonic motion
 * through interactive visualization.
 * 
 * PHYSICS:
 * - Hooke's Law: F = -kx
 * - Period T = 2π√(m/k)
 * - Energy oscillates between kinetic and potential
 */

import { useCallback } from 'react';
import PhysicsCanvas from './PhysicsCanvas';
import Matter from 'matter-js';

const { Constraint, Composite, Bodies } = Matter;

/**
 * SpringSimulation - Interactive spring-mass demonstration
 * 
 * @param {Object} props
 * @param {number} props.stiffness - Spring constant (default: 0.04)
 * @param {number} props.damping - Damping coefficient (default: 0.05)
 * @param {number} props.restLength - Rest length of spring (default: 150)
 * @param {number} props.massSize - Mass box size (default: 50)
 */
export default function SpringSimulation({
  stiffness = 0.04,
  damping = 0.05,
  restLength = 150,
  massSize = 50,
  className,
}) {
  const setup = useCallback((engine, render) => {
    const width = render.options.width;
    const height = render.options.height;
    
    // Anchor point at top
    const anchorX = width / 2;
    const anchorY = 60;
    
    // Create anchor (fixed point)
    const anchor = Bodies.rectangle(anchorX, anchorY, 100, 20, {
      isStatic: true,
      render: {
        fillStyle: '#475569',
        strokeStyle: '#64748b',
        lineWidth: 2,
      },
    });
    
    // Create mass (the hanging box)
    const mass = Bodies.rectangle(
      anchorX, 
      anchorY + restLength + 80, // Start stretched
      massSize, 
      massSize, 
      {
        restitution: 0.3,
        friction: 0.1,
        frictionAir: damping,
        render: {
          fillStyle: '#3b82f6',
          strokeStyle: '#2563eb',
          lineWidth: 3,
        },
      }
    );
    
    // Create spring constraint
    const spring = Constraint.create({
      bodyA: anchor,
      pointA: { x: 0, y: 10 },
      bodyB: mass,
      pointB: { x: 0, y: -massSize / 2 },
      stiffness: stiffness,
      damping: damping * 0.1,
      length: restLength,
      render: {
        strokeStyle: '#f97316',
        lineWidth: 4,
        type: 'spring',
        anchors: true,
      },
    });
    
    // Add equilibrium line indicator
    const equilibriumY = anchorY + restLength + 10;
    const equilibriumLine = Bodies.rectangle(
      anchorX, 
      equilibriumY, 
      200, 
      2, 
      {
        isStatic: true,
        isSensor: true, // No collision
        render: {
          fillStyle: '#22c55e',
          opacity: 0.5,
        },
      }
    );
    
    // Add to world
    Composite.add(engine.world, [anchor, mass, spring, equilibriumLine]);
    
    // Create visual spring coils (decorative)
    const coilCount = 8;
    for (let i = 1; i < coilCount; i++) {
      const coilY = anchorY + (restLength * i / coilCount);
      const coil = Bodies.circle(
        anchorX + (i % 2 === 0 ? 15 : -15), 
        coilY, 
        3, 
        {
          isStatic: true,
          isSensor: true,
          render: {
            fillStyle: '#f97316',
            opacity: 0.3,
          },
        }
      );
      Composite.add(engine.world, coil);
    }
    
  }, [stiffness, damping, restLength, massSize]);
  
  return (
    <div className={className}>
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-slate-800 mb-1">Spring-Mass System</h3>
        <p className="text-sm text-slate-600">
          Drag the mass to stretch. Hooke's Law: F = -kx
        </p>
        <div className="mt-2 text-xs text-slate-500">
          <span className="inline-block mr-4">Stiffness k = {stiffness}</span>
          <span className="inline-block">Damping = {damping}</span>
        </div>
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
