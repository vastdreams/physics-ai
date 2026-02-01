# utilities/
"""
Real-time Data Streaming System.

Inspired by DREAM architecture - continuous data updates.

First Principle Analysis:
- Data streams: S(t) = {s_1(t), s_2(t), ..., s_n(t)}
- Real-time updates: Process data as it arrives
- Buffering: Queue data for batch processing
- Mathematical foundation: Stream processing, time series analysis
- Architecture: Async streaming with buffering and processing
"""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import deque
import threading
import time
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from loggers.system_logger import SystemLogger
from utilities.cot_logging import ChainOfThoughtLogger, LogLevel


@dataclass
class DataPoint:
    """Represents a data point in a stream."""
    timestamp: datetime
    source: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


class DataStream:
    """
    Real-time data stream.
    
    Features:
    - Continuous data ingestion
    - Buffering
    - Processing callbacks
    - Statistics tracking
    """
    
    def __init__(self, stream_id: str, buffer_size: int = 1000):
        """
        Initialize data stream.
        
        Args:
            stream_id: Stream identifier
            buffer_size: Maximum buffer size
        """
        self.stream_id = stream_id
        self.logger = SystemLogger()
        self.buffer: deque = deque(maxlen=buffer_size)
        self.processors: List[Callable[[DataPoint], Any]] = []
        self.is_running = False
        self.stats = {
            'total_points': 0,
            'processed_points': 0,
            'dropped_points': 0,
            'start_time': None
        }
        
        self.logger.log(f"DataStream initialized: {stream_id}", level="INFO")
    
    def add_data(self, source: str, data: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Add data point to stream.
        
        Args:
            source: Data source identifier
            data: Data dictionary
            metadata: Optional metadata
        """
        point = DataPoint(
            timestamp=datetime.now(),
            source=source,
            data=data,
            metadata=metadata or {}
        )
        
        if len(self.buffer) >= self.buffer.maxlen:
            self.stats['dropped_points'] += 1
            self.logger.log(f"Buffer full, dropping point: {self.stream_id}", level="WARNING")
        else:
            self.buffer.append(point)
            self.stats['total_points'] += 1
        
        # Process immediately if running
        if self.is_running:
            self._process_point(point)
    
    def register_processor(self, processor: Callable[[DataPoint], Any]) -> None:
        """
        Register a data processor.
        
        Args:
            processor: Function to process data points
        """
        self.processors.append(processor)
        self.logger.log(f"Processor registered: {self.stream_id}", level="DEBUG")
    
    def start(self) -> None:
        """Start processing stream."""
        self.is_running = True
        self.stats['start_time'] = datetime.now()
        self.logger.log(f"DataStream started: {self.stream_id}", level="INFO")
    
    def stop(self) -> None:
        """Stop processing stream."""
        self.is_running = False
        self.logger.log(f"DataStream stopped: {self.stream_id}", level="INFO")
    
    def _process_point(self, point: DataPoint) -> None:
        """Process a single data point."""
        for processor in self.processors:
            try:
                processor(point)
                self.stats['processed_points'] += 1
            except Exception as e:
                self.logger.log(f"Error processing point: {str(e)}", level="ERROR")
    
    def get_buffer(self) -> List[DataPoint]:
        """Get current buffer contents."""
        return list(self.buffer)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get stream statistics."""
        elapsed = None
        if self.stats['start_time']:
            elapsed = (datetime.now() - self.stats['start_time']).total_seconds()
        
        return {
            **self.stats,
            'buffer_size': len(self.buffer),
            'elapsed_seconds': elapsed,
            'points_per_second': self.stats['processed_points'] / elapsed if elapsed and elapsed > 0 else 0.0
        }


class DataStreamManager:
    """
    Manages multiple data streams.
    
    Features:
    - Stream creation and management
    - Cross-stream processing
    - Aggregated statistics
    """
    
    def __init__(self):
        """Initialize stream manager."""
        self.logger = SystemLogger()
        self.streams: Dict[str, DataStream] = {}
        
        self.logger.log("DataStreamManager initialized", level="INFO")
    
    def create_stream(self, stream_id: str, buffer_size: int = 1000) -> DataStream:
        """
        Create a new data stream.
        
        Args:
            stream_id: Stream identifier
            buffer_size: Buffer size
            
        Returns:
            Created stream
        """
        if stream_id in self.streams:
            self.logger.log(f"Stream already exists: {stream_id}", level="WARNING")
            return self.streams[stream_id]
        
        stream = DataStream(stream_id, buffer_size)
        self.streams[stream_id] = stream
        
        self.logger.log(f"Stream created: {stream_id}", level="INFO")
        return stream
    
    def get_stream(self, stream_id: str) -> Optional[DataStream]:
        """Get stream by ID."""
        return self.streams.get(stream_id)
    
    def start_all(self) -> None:
        """Start all streams."""
        for stream in self.streams.values():
            stream.start()
        self.logger.log("All streams started", level="INFO")
    
    def stop_all(self) -> None:
        """Stop all streams."""
        for stream in self.streams.values():
            stream.stop()
        self.logger.log("All streams stopped", level="INFO")
    
    def get_all_statistics(self) -> Dict[str, Any]:
        """Get statistics for all streams."""
        return {
            stream_id: stream.get_statistics()
            for stream_id, stream in self.streams.items()
        }

