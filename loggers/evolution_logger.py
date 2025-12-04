# loggers/
"""
Evolution logging module.

Tracks self-evolution and self-modification events.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from .system_logger import SystemLogger


class EvolutionLogger:
    """
    Logger for tracking evolution events.
    """
    
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize evolution logger.
        
        Args:
            log_dir: Directory for log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        self.system_logger = SystemLogger(log_dir=log_dir)
        self.evolution_history: List[Dict[str, Any]] = []
        
        self.system_logger.log("EvolutionLogger initialized", level="INFO")
    
    def log_evolution(self, event_type: str, details: Dict[str, Any]) -> None:
        """
        Log an evolution event.
        
        Args:
            event_type: Type of evolution event
            details: Event details
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "details": details
        }
        
        self.evolution_history.append(event)
        self.system_logger.log(f"Evolution event: {event_type}", level="INFO", **details)
        
        # Save to file
        evolution_file = self.log_dir / f"evolution_{datetime.now().strftime('%Y%m%d')}.json"
        with open(evolution_file, 'a') as f:
            f.write(json.dumps(event) + '\n')

