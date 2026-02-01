"""
PATH: utilities/hot_reload.py
PURPOSE: Hot reload system for automatic code updates without manual restart

WHY: Enables rapid development by automatically detecting and reloading
     changed modules, eliminating the need for manual restarts.

FLOW:
┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
│ File        │────>│ Detect       │────>│ Reload Module   │
│ Watcher     │     │ Changes      │     │ & Notify        │
└─────────────┘     └──────────────┘     └─────────────────┘

DEPENDENCIES:
- watchdog: File system monitoring
- importlib: Module reloading
"""

from typing import Callable, Dict, List, Optional, Set, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import importlib
import importlib.util
import sys
import os
import time
import threading
import logging
import hashlib
import traceback

logger = logging.getLogger(__name__)


@dataclass
class ModuleState:
    """Track state of a watched module."""
    path: Path
    module_name: str
    last_modified: float
    content_hash: str
    reload_count: int = 0
    last_reload: Optional[datetime] = None
    last_error: Optional[str] = None


@dataclass
class ReloadEvent:
    """Event emitted when a module is reloaded."""
    module_name: str
    path: str
    timestamp: datetime
    success: bool
    error: Optional[str] = None
    reload_time_ms: float = 0.0


class HotReloader:
    """
    Hot reload system for Python modules.
    
    Watches specified directories for file changes and automatically
    reloads modified modules without requiring a full restart.
    
    Example:
        reloader = HotReloader(watch_dirs=['physics/', 'substrate/'])
        reloader.on_reload(lambda event: print(f"Reloaded: {event.module_name}"))
        reloader.start()
    """
    
    def __init__(
        self,
        watch_dirs: List[str] = None,
        exclude_patterns: List[str] = None,
        debounce_seconds: float = 0.5,
        auto_reload: bool = True,
    ):
        """
        Args:
            watch_dirs: Directories to watch for changes
            exclude_patterns: File patterns to ignore (e.g., '__pycache__', '.pyc')
            debounce_seconds: Wait time before reloading after change detected
            auto_reload: Whether to automatically reload on changes
        """
        self.watch_dirs = watch_dirs or ['.']
        self.exclude_patterns = exclude_patterns or [
            '__pycache__', '.pyc', '.pyo', '.git', '.env',
            'node_modules', 'venv', '.venv', 'dist', 'build'
        ]
        self.debounce_seconds = debounce_seconds
        self.auto_reload = auto_reload
        
        self._modules: Dict[str, ModuleState] = {}
        self._callbacks: List[Callable[[ReloadEvent], None]] = []
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._pending_reloads: Dict[str, float] = {}  # path -> change_time
        self._lock = threading.Lock()
        
        # Statistics
        self.total_reloads = 0
        self.failed_reloads = 0
        self.start_time: Optional[datetime] = None
    
    def _get_content_hash(self, path: Path) -> str:
        """Get hash of file content for change detection."""
        try:
            content = path.read_bytes()
            return hashlib.md5(content).hexdigest()
        except Exception:
            return ""
    
    def _should_watch(self, path: Path) -> bool:
        """Check if path should be watched."""
        path_str = str(path)
        
        # Must be a Python file
        if not path_str.endswith('.py'):
            return False
        
        # Check exclude patterns
        for pattern in self.exclude_patterns:
            if pattern in path_str:
                return False
        
        return True
    
    def _path_to_module_name(self, path: Path) -> Optional[str]:
        """Convert file path to Python module name."""
        try:
            # Get relative path from current directory
            rel_path = path.relative_to(Path.cwd())
            
            # Convert to module name
            parts = list(rel_path.parts)
            if parts[-1].endswith('.py'):
                parts[-1] = parts[-1][:-3]
            
            # Handle __init__.py
            if parts[-1] == '__init__':
                parts = parts[:-1]
            
            return '.'.join(parts) if parts else None
        except ValueError:
            return None
    
    def _scan_directory(self, dir_path: str) -> List[Path]:
        """Scan directory for Python files."""
        files = []
        root = Path(dir_path)
        
        if not root.exists():
            return files
        
        for path in root.rglob('*.py'):
            if self._should_watch(path):
                files.append(path)
        
        return files
    
    def _register_module(self, path: Path) -> None:
        """Register a module for watching."""
        module_name = self._path_to_module_name(path)
        if not module_name:
            return
        
        state = ModuleState(
            path=path,
            module_name=module_name,
            last_modified=path.stat().st_mtime,
            content_hash=self._get_content_hash(path),
        )
        
        self._modules[str(path)] = state
    
    def _check_for_changes(self) -> List[str]:
        """Check all watched modules for changes."""
        changed = []
        
        for path_str, state in self._modules.items():
            path = Path(path_str)
            
            if not path.exists():
                continue
            
            try:
                current_mtime = path.stat().st_mtime
                
                # Check if modified
                if current_mtime > state.last_modified:
                    # Verify content actually changed (not just touch)
                    new_hash = self._get_content_hash(path)
                    if new_hash != state.content_hash:
                        changed.append(path_str)
                        state.content_hash = new_hash
                    state.last_modified = current_mtime
                    
            except Exception as e:
                logger.debug(f"Error checking {path}: {e}")
        
        return changed
    
    def _reload_module(self, path_str: str) -> ReloadEvent:
        """Reload a single module."""
        state = self._modules.get(path_str)
        if not state:
            return ReloadEvent(
                module_name="unknown",
                path=path_str,
                timestamp=datetime.now(),
                success=False,
                error="Module not registered",
            )
        
        start_time = time.perf_counter()
        module_name = state.module_name
        
        try:
            # Check if module is loaded
            if module_name in sys.modules:
                module = sys.modules[module_name]
                
                # Reload the module
                importlib.reload(module)
                
                logger.info(f"Reloaded: {module_name}")
            else:
                # Module not loaded yet, just update state
                logger.debug(f"Module {module_name} not loaded, skipping reload")
            
            # Update state
            state.reload_count += 1
            state.last_reload = datetime.now()
            state.last_error = None
            self.total_reloads += 1
            
            elapsed = (time.perf_counter() - start_time) * 1000
            
            return ReloadEvent(
                module_name=module_name,
                path=path_str,
                timestamp=datetime.now(),
                success=True,
                reload_time_ms=elapsed,
            )
            
        except Exception as e:
            error_msg = f"{type(e).__name__}: {e}\n{traceback.format_exc()}"
            state.last_error = error_msg
            self.failed_reloads += 1
            
            elapsed = (time.perf_counter() - start_time) * 1000
            
            logger.error(f"Failed to reload {module_name}: {e}")
            
            return ReloadEvent(
                module_name=module_name,
                path=path_str,
                timestamp=datetime.now(),
                success=False,
                error=error_msg,
                reload_time_ms=elapsed,
            )
    
    def _reload_with_dependencies(self, path_str: str) -> List[ReloadEvent]:
        """
        Reload a module and its dependents.
        
        When a module changes, modules that import it may need reloading too.
        """
        events = []
        state = self._modules.get(path_str)
        
        if not state:
            return events
        
        # First reload the changed module
        event = self._reload_module(path_str)
        events.append(event)
        
        if not event.success:
            return events
        
        # Find and reload dependent modules
        # (This is a simplified version - full dependency tracking would be more complex)
        changed_module = state.module_name
        
        for other_path, other_state in self._modules.items():
            if other_path == path_str:
                continue
            
            other_module_name = other_state.module_name
            if other_module_name in sys.modules:
                other_module = sys.modules[other_module_name]
                
                # Check if this module imports the changed one
                # (Simplified check - looks at module dict)
                try:
                    module_dict = vars(other_module)
                    for value in module_dict.values():
                        if hasattr(value, '__module__') and value.__module__ == changed_module:
                            # This module depends on the changed one
                            dep_event = self._reload_module(other_path)
                            events.append(dep_event)
                            break
                except Exception:
                    pass
        
        return events
    
    def _watch_loop(self) -> None:
        """Main watch loop running in background thread."""
        while self._running:
            try:
                # Check for changes
                changed = self._check_for_changes()
                
                # Add to pending reloads with debounce
                current_time = time.time()
                with self._lock:
                    for path in changed:
                        self._pending_reloads[path] = current_time
                
                # Process pending reloads after debounce period
                to_reload = []
                with self._lock:
                    for path, change_time in list(self._pending_reloads.items()):
                        if current_time - change_time >= self.debounce_seconds:
                            to_reload.append(path)
                            del self._pending_reloads[path]
                
                # Reload changed modules
                if self.auto_reload:
                    for path in to_reload:
                        events = self._reload_with_dependencies(path)
                        
                        # Notify callbacks
                        for event in events:
                            for callback in self._callbacks:
                                try:
                                    callback(event)
                                except Exception as e:
                                    logger.error(f"Callback error: {e}")
                
                # Sleep before next check
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Watch loop error: {e}")
                time.sleep(1)
    
    def start(self) -> None:
        """Start the hot reload watcher."""
        if self._running:
            return
        
        logger.info("Starting hot reload watcher...")
        
        # Scan and register all modules
        for dir_path in self.watch_dirs:
            for path in self._scan_directory(dir_path):
                self._register_module(path)
        
        logger.info(f"Watching {len(self._modules)} Python files")
        
        self._running = True
        self.start_time = datetime.now()
        
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()
    
    def stop(self) -> None:
        """Stop the hot reload watcher."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None
        logger.info("Hot reload watcher stopped")
    
    def on_reload(self, callback: Callable[[ReloadEvent], None]) -> None:
        """Register a callback for reload events."""
        self._callbacks.append(callback)
    
    def reload_all(self) -> List[ReloadEvent]:
        """Force reload all watched modules."""
        events = []
        for path_str in self._modules:
            event = self._reload_module(path_str)
            events.append(event)
        return events
    
    def reload_module(self, module_name: str) -> Optional[ReloadEvent]:
        """Force reload a specific module by name."""
        for path_str, state in self._modules.items():
            if state.module_name == module_name:
                return self._reload_module(path_str)
        return None
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the hot reloader."""
        return {
            "running": self._running,
            "watched_files": len(self._modules),
            "total_reloads": self.total_reloads,
            "failed_reloads": self.failed_reloads,
            "pending_reloads": len(self._pending_reloads),
            "uptime_seconds": (
                (datetime.now() - self.start_time).total_seconds()
                if self.start_time else 0
            ),
            "watch_dirs": self.watch_dirs,
        }
    
    def get_module_states(self) -> List[Dict[str, Any]]:
        """Get state of all watched modules."""
        states = []
        for path_str, state in self._modules.items():
            states.append({
                "module": state.module_name,
                "path": path_str,
                "reload_count": state.reload_count,
                "last_reload": state.last_reload.isoformat() if state.last_reload else None,
                "has_error": state.last_error is not None,
            })
        return states


# Global instance for easy access
_global_reloader: Optional[HotReloader] = None


def get_reloader() -> HotReloader:
    """Get the global hot reloader instance."""
    global _global_reloader
    if _global_reloader is None:
        _global_reloader = HotReloader()
    return _global_reloader


def start_hot_reload(
    watch_dirs: List[str] = None,
    on_reload: Callable[[ReloadEvent], None] = None,
) -> HotReloader:
    """
    Start hot reload for the application.
    
    Args:
        watch_dirs: Directories to watch (default: physics/, substrate/, api/, etc.)
        on_reload: Optional callback for reload events
        
    Returns:
        HotReloader instance
    """
    global _global_reloader
    
    if watch_dirs is None:
        watch_dirs = [
            'physics',
            'substrate',
            'api',
            'core',
            'rules',
            'evolution',
            'utilities',
        ]
    
    _global_reloader = HotReloader(watch_dirs=watch_dirs)
    
    if on_reload:
        _global_reloader.on_reload(on_reload)
    
    # Default logging callback
    def log_reload(event: ReloadEvent):
        if event.success:
            print(f"🔄 Reloaded: {event.module_name} ({event.reload_time_ms:.1f}ms)")
        else:
            print(f"❌ Reload failed: {event.module_name} - {event.error[:100] if event.error else 'Unknown error'}")
    
    _global_reloader.on_reload(log_reload)
    _global_reloader.start()
    
    return _global_reloader


def stop_hot_reload() -> None:
    """Stop the global hot reloader."""
    global _global_reloader
    if _global_reloader:
        _global_reloader.stop()
        _global_reloader = None
