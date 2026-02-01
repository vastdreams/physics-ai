/**
 * PATH: frontend/src/components/panels/ResizablePanel.jsx
 * PURPOSE: Reusable resizable panel component with drag handles
 * 
 * FEATURES:
 * - Horizontal or vertical resizing
 * - Min/max size constraints
 * - Smooth drag interaction
 * - Collapse/expand functionality
 */

import { useState, useRef, useCallback, useEffect } from 'react';
import { clsx } from 'clsx';
import { GripVertical, GripHorizontal, ChevronLeft, ChevronRight, ChevronUp, ChevronDown } from 'lucide-react';

export default function ResizablePanel({
  children,
  direction = 'horizontal', // 'horizontal' (left-right) or 'vertical' (top-bottom)
  position = 'end', // 'start' or 'end' - where the resize handle is
  defaultSize = 320,
  minSize = 200,
  maxSize = 600,
  collapsed = false,
  onCollapse,
  collapsedSize = 0,
  className = '',
  handleClassName = '',
  showCollapseButton = true,
}) {
  const [size, setSize] = useState(defaultSize);
  const [isResizing, setIsResizing] = useState(false);
  const panelRef = useRef(null);
  const startPosRef = useRef(0);
  const startSizeRef = useRef(0);

  const isHorizontal = direction === 'horizontal';
  const isStart = position === 'start';

  const handleMouseDown = useCallback((e) => {
    e.preventDefault();
    setIsResizing(true);
    startPosRef.current = isHorizontal ? e.clientX : e.clientY;
    startSizeRef.current = size;
  }, [isHorizontal, size]);

  const handleMouseMove = useCallback((e) => {
    if (!isResizing) return;

    const currentPos = isHorizontal ? e.clientX : e.clientY;
    const delta = currentPos - startPosRef.current;
    
    // Adjust delta based on position
    const adjustedDelta = isStart ? delta : -delta;
    
    let newSize = startSizeRef.current + adjustedDelta;
    newSize = Math.max(minSize, Math.min(maxSize, newSize));
    
    setSize(newSize);
  }, [isResizing, isHorizontal, isStart, minSize, maxSize]);

  const handleMouseUp = useCallback(() => {
    setIsResizing(false);
  }, []);

  useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = isHorizontal ? 'col-resize' : 'row-resize';
      document.body.style.userSelect = 'none';
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
      document.body.style.cursor = '';
      document.body.style.userSelect = '';
    };
  }, [isResizing, handleMouseMove, handleMouseUp, isHorizontal]);

  const actualSize = collapsed ? collapsedSize : size;

  const handleStyle = isHorizontal
    ? { width: '6px', cursor: 'col-resize' }
    : { height: '6px', cursor: 'row-resize' };

  const GripIcon = isHorizontal ? GripVertical : GripHorizontal;
  
  const CollapseIcon = isHorizontal
    ? (isStart ? (collapsed ? ChevronRight : ChevronLeft) : (collapsed ? ChevronLeft : ChevronRight))
    : (isStart ? (collapsed ? ChevronDown : ChevronUp) : (collapsed ? ChevronUp : ChevronDown));

  return (
    <div
      ref={panelRef}
      className={clsx(
        'relative flex-shrink-0 transition-all',
        isResizing ? 'transition-none' : 'duration-200',
        className
      )}
      style={{
        [isHorizontal ? 'width' : 'height']: `${actualSize}px`,
      }}
    >
      {/* Resize Handle */}
      {!collapsed && (
        <div
          className={clsx(
            'absolute z-20 flex items-center justify-center group',
            isHorizontal
              ? 'top-0 bottom-0 hover:bg-accent-primary/20'
              : 'left-0 right-0 hover:bg-accent-primary/20',
            isStart
              ? (isHorizontal ? 'right-0' : 'bottom-0')
              : (isHorizontal ? 'left-0' : 'top-0'),
            handleClassName
          )}
          style={handleStyle}
          onMouseDown={handleMouseDown}
        >
          <div className={clsx(
            'opacity-0 group-hover:opacity-100 transition-opacity',
            isHorizontal ? 'py-8' : 'px-8'
          )}>
            <GripIcon size={12} className="text-light-400" />
          </div>
          
          {/* Visual indicator line */}
          <div className={clsx(
            'absolute bg-light-300 group-hover:bg-accent-primary transition-colors',
            isHorizontal
              ? 'w-px h-full'
              : 'h-px w-full'
          )} />
        </div>
      )}

      {/* Collapse Button */}
      {showCollapseButton && onCollapse && (
        <button
          onClick={onCollapse}
          className={clsx(
            'absolute z-30 p-1 bg-light-100 hover:bg-light-200 border border-light-300 rounded-md transition-colors',
            isHorizontal
              ? 'top-1/2 -translate-y-1/2'
              : 'left-1/2 -translate-x-1/2',
            isHorizontal
              ? (isStart ? '-right-3' : '-left-3')
              : (isStart ? '-bottom-3' : '-top-3')
          )}
        >
          <CollapseIcon size={14} className="text-light-500" />
        </button>
      )}

      {/* Panel Content */}
      <div className={clsx(
        'h-full w-full overflow-hidden',
        collapsed && 'hidden'
      )}>
        {children}
      </div>
    </div>
  );
}
