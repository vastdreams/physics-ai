/**
 * PATH: frontend/src/workers/pyodide.worker.js
 * PURPOSE: Web Worker for Pyodide Python execution
 * 
 * WHY: Running Python in the browser is CPU-intensive.
 * Web Workers prevent blocking the main UI thread.
 * 
 * FEATURES:
 * - Load Pyodide from CDN
 * - Execute Python code asynchronously
 * - Install packages via micropip
 * - Capture stdout/stderr
 * - Support matplotlib plots (base64 encoded)
 */

// eslint-disable-next-line no-undef
importScripts('https://cdn.jsdelivr.net/pyodide/v0.26.1/full/pyodide.js');

let pyodide = null;
let isInitialized = false;
let initPromise = null;

// Standard packages to preload
const PRELOADED_PACKAGES = [
  'numpy',
  'sympy',
];

// Additional packages that can be installed on demand
const AVAILABLE_PACKAGES = [
  'scipy',
  'pandas',
  'matplotlib',
  'networkx',
];

/**
 * Initialize Pyodide and preload packages
 */
async function initializePyodide() {
  if (initPromise) return initPromise;
  
  initPromise = (async () => {
    try {
      postMessage({ type: 'status', status: 'loading', message: 'Loading Pyodide...' });
      
      // Load Pyodide
      // eslint-disable-next-line no-undef
      pyodide = await loadPyodide({
        indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.26.1/full/'
      });
      
      postMessage({ type: 'status', status: 'loading', message: 'Installing packages...' });
      
      // Load micropip for package management
      await pyodide.loadPackage('micropip');
      
      // Preload common packages
      for (const pkg of PRELOADED_PACKAGES) {
        try {
          await pyodide.loadPackage(pkg);
          postMessage({ type: 'status', status: 'loading', message: `Installed ${pkg}` });
        } catch (e) {
          console.warn(`Failed to preload ${pkg}:`, e);
        }
      }
      
      // Set up stdout/stderr capture
      await pyodide.runPythonAsync(`
import sys
from io import StringIO

class OutputCapture:
    def __init__(self):
        self.stdout = StringIO()
        self.stderr = StringIO()
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
    
    def start(self):
        self.stdout = StringIO()
        self.stderr = StringIO()
        sys.stdout = self.stdout
        sys.stderr = self.stderr
    
    def stop(self):
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr
        return self.stdout.getvalue(), self.stderr.getvalue()

_output_capture = OutputCapture()
      `);
      
      isInitialized = true;
      postMessage({ type: 'ready' });
      
    } catch (error) {
      postMessage({ type: 'error', error: error.message });
      throw error;
    }
  })();
  
  return initPromise;
}

/**
 * Run Python code and return results
 */
async function runPython(code, options = {}) {
  if (!isInitialized) {
    await initializePyodide();
  }
  
  const { captureOutput = true, returnExpression = false } = options;
  
  try {
    // Start output capture
    if (captureOutput) {
      await pyodide.runPythonAsync('_output_capture.start()');
    }
    
    // Run the code
    let result;
    if (returnExpression) {
      // Evaluate as expression (for single expressions like "2+2")
      result = await pyodide.runPythonAsync(code);
    } else {
      // Execute as statements
      result = await pyodide.runPythonAsync(code);
    }
    
    // Stop capture and get output
    let stdout = '';
    let stderr = '';
    if (captureOutput) {
      const captured = await pyodide.runPythonAsync('_output_capture.stop()');
      stdout = captured.get(0);
      stderr = captured.get(1);
    }
    
    // Convert result to JavaScript
    let jsResult = null;
    if (result !== undefined && result !== null) {
      try {
        jsResult = result.toJs ? result.toJs() : result;
        // Handle complex types
        if (jsResult instanceof Map) {
          jsResult = Object.fromEntries(jsResult);
        }
      } catch (e) {
        jsResult = String(result);
      }
    }
    
    return {
      success: true,
      result: jsResult,
      stdout,
      stderr,
    };
    
  } catch (error) {
    // Stop capture on error
    if (captureOutput) {
      try {
        await pyodide.runPythonAsync('_output_capture.stop()');
      } catch (e) {
        // Ignore
      }
    }
    
    return {
      success: false,
      error: error.message,
      traceback: error.stack,
    };
  }
}

/**
 * Install a package via micropip
 */
async function installPackage(packageName) {
  if (!isInitialized) {
    await initializePyodide();
  }
  
  try {
    // Check if it's a pure Python package (use micropip)
    const micropip = pyodide.pyimport('micropip');
    await micropip.install(packageName);
    
    return { success: true, package: packageName };
  } catch (error) {
    // Try loading as built-in Pyodide package
    try {
      await pyodide.loadPackage(packageName);
      return { success: true, package: packageName };
    } catch (e) {
      return { success: false, error: error.message };
    }
  }
}

/**
 * Get information about the Python environment
 */
async function getEnvironmentInfo() {
  if (!isInitialized) {
    await initializePyodide();
  }
  
  const info = await pyodide.runPythonAsync(`
import sys
import json

info = {
    'python_version': sys.version,
    'platform': sys.platform,
    'modules': list(sys.modules.keys())[:50],  # First 50 loaded modules
}
json.dumps(info)
  `);
  
  return JSON.parse(info);
}

// Message handler
self.onmessage = async function(event) {
  const { type, id, ...data } = event.data;
  
  try {
    let response;
    
    switch (type) {
      case 'init':
        await initializePyodide();
        response = { type: 'init_complete' };
        break;
        
      case 'run':
        response = await runPython(data.code, data.options);
        break;
        
      case 'install':
        response = await installPackage(data.package);
        break;
        
      case 'env':
        response = await getEnvironmentInfo();
        break;
        
      default:
        response = { error: `Unknown message type: ${type}` };
    }
    
    postMessage({ id, ...response });
    
  } catch (error) {
    postMessage({ id, success: false, error: error.message });
  }
};

// Auto-initialize when worker starts
initializePyodide().catch(console.error);
