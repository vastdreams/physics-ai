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

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from loggers.system_logger import SystemLogger

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_DEFAULT_BUFFER_SIZE = 1000


@dataclass
class DataPoint:
    """Represents a single data point in a stream."""

    timestamp: datetime
    source: str
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)


class DataStream:
    """Real-time data stream with buffering and processor callbacks.

    Features:
    - Continuous data ingestion
    - Configurable buffer size
    - Pluggable processing callbacks
    - Statistics tracking
    """

    def __init__(self, stream_id: str, buffer_size: int = _DEFAULT_BUFFER_SIZE) -> None:
        """Initialize data stream.

        Args:
            stream_id: Unique stream identifier.
            buffer_size: Maximum buffer size.
        """
        self.stream_id = stream_id
        self._logger = SystemLogger()
        self.buffer: deque[DataPoint] = deque(maxlen=buffer_size)
        self.processors: List[Callable[[DataPoint], Any]] = []
        self.is_running = False
        self.stats: Dict[str, Any] = {
            "total_points": 0,
            "processed_points": 0,
            "dropped_points": 0,
            "start_time": None,
        }

        self._logger.log(f"DataStream initialized: {stream_id}", level="INFO")

    def add_data(
        self,
        source: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add data point to stream.

        Args:
            source: Data source identifier.
            data: Data dictionary.
            metadata: Optional metadata.
        """
        point = DataPoint(
            timestamp=datetime.now(),
            source=source,
            data=data,
            metadata=metadata or {},
        )

        if len(self.buffer) >= self.buffer.maxlen:
            self.stats["dropped_points"] += 1
            self._logger.log(f"Buffer full, dropping point: {self.stream_id}", level="WARNING")
        else:
            self.buffer.append(point)
            self.stats["total_points"] += 1

        if self.is_running:
            self._process_point(point)

    def register_processor(self, processor: Callable[[DataPoint], Any]) -> None:
        """Register a data processor callback.

        Args:
            processor: Function to process data points.
        """
        self.processors.append(processor)
        self._logger.log(f"Processor registered: {self.stream_id}", level="DEBUG")

    def start(self) -> None:
        """Start processing stream."""
        self.is_running = True
        self.stats["start_time"] = datetime.now()
        self._logger.log(f"DataStream started: {self.stream_id}", level="INFO")

    def stop(self) -> None:
        """Stop processing stream."""
        self.is_running = False
        self._logger.log(f"DataStream stopped: {self.stream_id}", level="INFO")

    def _process_point(self, point: DataPoint) -> None:
        """Process a single data point through all registered processors."""
        for processor in self.processors:
            try:
                processor(point)
                self.stats["processed_points"] += 1
            except Exception as e:
                self._logger.log(f"Error processing point: {e}", level="ERROR")

    def get_buffer(self) -> List[DataPoint]:
        """Get current buffer contents as a list."""
        return list(self.buffer)

    def get_statistics(self) -> Dict[str, Any]:
        """Get stream statistics."""
        elapsed: Optional[float] = None
        if self.stats["start_time"]:
            elapsed = (datetime.now() - self.stats["start_time"]).total_seconds()

        return {
            **self.stats,
            "buffer_size": len(self.buffer),
            "elapsed_seconds": elapsed,
            "points_per_second": (
                self.stats["processed_points"] / elapsed
                if elapsed and elapsed > 0
                else 0.0
            ),
        }


class DataStreamManager:
    """Manages multiple data streams.

    Features:
    - Stream creation and lifecycle management
    - Cross-stream processing
    - Aggregated statistics
    """

    def __init__(self) -> None:
        """Initialize stream manager."""
        self._logger = SystemLogger()
        self.streams: Dict[str, DataStream] = {}

        self._logger.log("DataStreamManager initialized", level="INFO")

    def create_stream(
        self, stream_id: str, buffer_size: int = _DEFAULT_BUFFER_SIZE
    ) -> DataStream:
        """Create a new data stream.

        Args:
            stream_id: Unique stream identifier.
            buffer_size: Buffer size.

        Returns:
            The created (or existing) ``DataStream``.
        """
        if stream_id in self.streams:
            self._logger.log(f"Stream already exists: {stream_id}", level="WARNING")
            return self.streams[stream_id]

        stream = DataStream(stream_id, buffer_size)
        self.streams[stream_id] = stream

        self._logger.log(f"Stream created: {stream_id}", level="INFO")
        return stream

    def get_stream(self, stream_id: str) -> Optional[DataStream]:
        """Get stream by ID."""
        return self.streams.get(stream_id)

    def start_all(self) -> None:
        """Start all streams."""
        for stream in self.streams.values():
            stream.start()
        self._logger.log("All streams started", level="INFO")

    def stop_all(self) -> None:
        """Stop all streams."""
        for stream in self.streams.values():
            stream.stop()
        self._logger.log("All streams stopped", level="INFO")

    def get_all_statistics(self) -> Dict[str, Any]:
        """Get statistics for all streams."""
        return {
            stream_id: stream.get_statistics()
            for stream_id, stream in self.streams.items()
        }
