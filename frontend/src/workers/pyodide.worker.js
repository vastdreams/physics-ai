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
      
      // Set up stdout/stderr capture + matplotlib plot capture
      await pyodide.runPythonAsync(`
import sys
from io import StringIO

class OutputCapture:
    def __init__(self):
        self.stdout = StringIO()
        self.stderr = StringIO()
        self._original_stdout = sys.stdout
        self._original_stderr = sys.stderr
        self.plots = []  # list of base64-encoded PNG images
    
    def start(self):
        self.stdout = StringIO()
        self.stderr = StringIO()
        self.plots = []
        sys.stdout = self.stdout
        sys.stderr = self.stderr
    
    def stop(self):
        sys.stdout = self._original_stdout
        sys.stderr = self._original_stderr
        return self.stdout.getvalue(), self.stderr.getvalue()
    
    def capture_plots(self):
        """Capture all open matplotlib figures as base64 PNG."""
        try:
            import matplotlib
            matplotlib.use('Agg')  # non-interactive backend
            import matplotlib.pyplot as plt
            import base64
            from io import BytesIO
            
            figs = [plt.figure(i) for i in plt.get_fignums()]
            for fig in figs:
                buf = BytesIO()
                fig.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                            facecolor='white', edgecolor='none')
                buf.seek(0)
                b64 = base64.b64encode(buf.read()).decode('utf-8')
                self.plots.append(f"data:image/png;base64,{b64}")
                buf.close()
            plt.close('all')
        except ImportError:
            pass  # matplotlib not loaded yet
        except Exception as e:
            print(f"[Plot capture warning]: {e}")
        return self.plots

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
 * Auto-detect and install missing imports before running code
 */
async function ensureDependencies(code) {
  const importPattern = /^\s*(?:import|from)\s+(\w+)/gm;
  const needed = new Set();
  let match;
  while ((match = importPattern.exec(code)) !== null) {
    needed.add(match[1]);
  }

  // Map import names to Pyodide package names
  const packageMap = {
    matplotlib: 'matplotlib',
    scipy: 'scipy',
    pandas: 'pandas',
    sklearn: 'scikit-learn',
    PIL: 'Pillow',
    cv2: 'opencv-python',
    networkx: 'networkx',
  };

  for (const mod of needed) {
    if (packageMap[mod]) {
      try {
        // Check if already importable
        await pyodide.runPythonAsync(`import ${mod}`);
      } catch {
        // Not available — install it
        postMessage({ type: 'status', status: 'loading', message: `Installing ${mod}...` });
        try {
          await pyodide.loadPackage(packageMap[mod]);
        } catch {
          try {
            const micropip = pyodide.pyimport('micropip');
            await micropip.install(packageMap[mod]);
          } catch (e) {
            console.warn(`Could not install ${mod}:`, e);
          }
        }
      }
    }
  }
}

/**
 * Run Python code and return results
 */
async function runPython(code, options = {}) {
  if (!isInitialized) {
    await initializePyodide();
  }
  
  const { captureOutput = true } = options;
  
  try {
    // Auto-install missing packages
    await ensureDependencies(code);

    // If code uses matplotlib, ensure Agg backend is set
    if (code.includes('matplotlib') || code.includes('plt')) {
      await pyodide.runPythonAsync(`
import matplotlib
matplotlib.use('Agg')
`);
    }

    // Start output capture
    if (captureOutput) {
      await pyodide.runPythonAsync('_output_capture.start()');
    }
    
    // Execute the code
    let result = await pyodide.runPythonAsync(code);
    
    // Stop capture and get output
    let stdout = '';
    let stderr = '';
    if (captureOutput) {
      const captured = await pyodide.runPythonAsync('_output_capture.stop()');
      stdout = captured.get(0);
      stderr = captured.get(1);
    }

    // Capture any matplotlib plots
    let plots = [];
    try {
      const pyPlots = await pyodide.runPythonAsync('_output_capture.capture_plots()');
      if (pyPlots && pyPlots.toJs) {
        plots = Array.from(pyPlots.toJs());
      } else if (Array.isArray(pyPlots)) {
        plots = pyPlots;
      }
    } catch {
      // No plots to capture
    }
    
    // Convert result to JavaScript
    let jsResult = null;
    if (result !== undefined && result !== null) {
      try {
        jsResult = result.toJs ? result.toJs() : result;
        if (jsResult instanceof Map) {
          jsResult = Object.fromEntries(jsResult);
        }
      } catch {
        jsResult = String(result);
      }
    }
    
    return {
      success: true,
      result: jsResult,
      stdout,
      stderr,
      plots,   // <-- base64 PNG images from matplotlib
    };
    
  } catch (error) {
    // Stop capture on error
    if (captureOutput) {
      try {
        await pyodide.runPythonAsync('_output_capture.stop()');
      } catch {
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
