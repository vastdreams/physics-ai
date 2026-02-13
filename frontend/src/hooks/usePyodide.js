/**
 * PATH: frontend/src/hooks/usePyodide.js
 * PURPOSE: React hook for Pyodide Python execution in browser
 * 
 * WHY: Provides a clean React interface to execute Python code
 * in a Web Worker, preventing UI blocking.
 * 
 * FEATURES:
 * - Async Python code execution
 * - Package installation
 * - Loading state management
 * - Output capture (stdout/stderr)
 * - Error handling
 */

import { useState, useEffect, useCallback, useRef } from 'react';

// Message ID counter for tracking responses
let messageId = 0;

/**
 * React hook for using Pyodide in browser
 * 
 * @returns {Object} - { runPython, installPackage, isReady, isLoading, error }
 */
export function usePyodide() {
  const [isReady, setIsReady] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [loadingMessage, setLoadingMessage] = useState('Initializing...');
  const [error, setError] = useState(null);
  
  const workerRef = useRef(null);
  const pendingMessages = useRef(new Map());
  
  // Initialize worker
  useEffect(() => {
    // Create worker
    const worker = new Worker(
      new URL('../workers/pyodide.worker.js', import.meta.url),
      { type: 'classic' }
    );
    
    workerRef.current = worker;
    
    // Handle messages from worker
    worker.onmessage = (event) => {
      const { type, id, ...data } = event.data;
      
      // Handle status updates
      if (type === 'status') {
        setLoadingMessage(data.message || 'Loading...');
        return;
      }
      
      // Handle ready state
      if (type === 'ready') {
        setIsReady(true);
        setIsLoading(false);
        setLoadingMessage('');
        return;
      }
      
      // Handle errors
      if (type === 'error') {
        setError(data.error);
        setIsLoading(false);
        return;
      }
      
      // Handle response to specific message
      if (id !== undefined && pendingMessages.current.has(id)) {
        const { resolve, reject } = pendingMessages.current.get(id);
        pendingMessages.current.delete(id);
        
        if (data.success === false && data.error) {
          reject(new Error(data.error));
        } else {
          resolve(data);
        }
      }
    };
    
    // Handle worker errors
    worker.onerror = (event) => {
      console.error('Pyodide worker error:', event);
      setError(event.message || 'Worker error');
      setIsLoading(false);
    };
    
    // Cleanup
    return () => {
      worker.terminate();
      workerRef.current = null;
    };
  }, []);
  
  /**
   * Send message to worker and wait for response
   */
  const sendMessage = useCallback((type, data = {}) => {
    return new Promise((resolve, reject) => {
      if (!workerRef.current) {
        reject(new Error('Pyodide worker not initialized'));
        return;
      }
      
      const id = messageId++;
      pendingMessages.current.set(id, { resolve, reject });
      
      workerRef.current.postMessage({ type, id, ...data });
    });
  }, []);
  
  /**
   * Run Python code
   * 
   * @param {string} code - Python code to execute
   * @param {Object} options - Execution options
   * @returns {Promise<Object>} - { success, result, stdout, stderr } or { success, error }
   */
  const runPython = useCallback(async (code, options = {}) => {
    if (!isReady) {
      throw new Error('Pyodide is not ready yet');
    }
    
    try {
      const result = await sendMessage('run', { code, options });
      return result;
    } catch (error) {
      return {
        success: false,
        error: error.message,
      };
    }
  }, [isReady, sendMessage]);
  
  /**
   * Install a Python package
   * 
   * @param {string} packageName - Package to install
   * @returns {Promise<Object>} - { success, package } or { success, error }
   */
  const installPackage = useCallback(async (packageName) => {
    if (!isReady) {
      throw new Error('Pyodide is not ready yet');
    }
    
    try {
      return await sendMessage('install', { package: packageName });
    } catch (error) {
      return {
        success: false,
        error: error.message,
      };
    }
  }, [isReady, sendMessage]);
  
  /**
   * Get environment info
   */
  const getEnvironmentInfo = useCallback(async () => {
    if (!isReady) {
      throw new Error('Pyodide is not ready yet');
    }
    
    return await sendMessage('env');
  }, [isReady, sendMessage]);
  
  return {
    runPython,
    installPackage,
    getEnvironmentInfo,
    isReady,
    isLoading,
    loadingMessage,
    error,
  };
}

/**
 * Helper to format Python execution output for display
 * 
 * @param {Object} result - Result from runPython
 * @returns {string} - Formatted output string
 */
export function formatPythonOutput(result) {
  if (!result) return '';
  
  const parts = [];
  
  // Add stdout
  if (result.stdout) {
    parts.push(result.stdout);
  }
  
  // Add result value
  if (result.result !== null && result.result !== undefined) {
    const resultStr = typeof result.result === 'object' 
      ? JSON.stringify(result.result, null, 2)
      : String(result.result);
    
    if (resultStr && resultStr !== 'None' && resultStr !== 'undefined') {
      parts.push(resultStr);
    }
  }
  
  // Add stderr as warning
  if (result.stderr) {
    parts.push(`[Warning]\n${result.stderr}`);
  }
  
  return parts.join('\n').trim();
}

/**
 * Helper to format Python error for display
 * 
 * @param {Object} result - Result from runPython with error
 * @returns {string} - Formatted error string
 */
export function formatPythonError(result) {
  if (!result || result.success !== false) return '';
  
  let errorMsg = result.error || 'Unknown error';
  
  // Clean up traceback if present
  if (result.traceback) {
    // Extract just the relevant error message from full traceback
    const lines = result.traceback.split('\n');
    const errorLine = lines.find(line => 
      line.includes('Error:') || line.includes('Exception:')
    );
    if (errorLine) {
      errorMsg = errorLine;
    }
  }
  
  return errorMsg;
}

export default usePyodide;
