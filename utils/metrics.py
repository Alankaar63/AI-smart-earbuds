"""Performance measurement helpers for stage and total pipeline latency."""

from __future__ import annotations

import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Dict, Generator

import psutil


@dataclass
class StageMetrics:
    """Container for measured stage times in seconds."""

    timings: Dict[str, float]

    def record(self, stage_name: str, seconds: float) -> None:
        """Store stage timing by name."""
        self.timings[stage_name] = seconds

    def total(self) -> float:
        """Compute total measured time."""
        return sum(self.timings.values())


def get_cpu_percent() -> float:
    """Read current CPU usage percentage."""
    return psutil.cpu_percent(interval=None)


@contextmanager
def timed_stage(metrics: StageMetrics, stage_name: str) -> Generator[None, None, None]:
    """Context manager to time a pipeline stage and record duration."""
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        metrics.record(stage_name, elapsed)
