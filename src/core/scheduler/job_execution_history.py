"""
Job execution history tracking.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any
import uuid


@dataclass
class JobExecutionRecord:
    """
    Records details of a single job execution.
    
    Attributes:
        execution_id: Unique ID for this execution
        job_id: ID of the job that was executed
        job_name: Name of the job at execution time
        start_time: When execution started
        end_time: When execution completed
        status: success, failed, partial_success
        fetched_stocks: List of successfully fetched stock IDs
        failed_stocks: List of stock IDs that failed
        errors: List of error messages
        total_stocks: Total number of stocks attempted
        duration_seconds: Execution duration
        triggered_by: scheduler_auto, manual_trigger, retry
        metadata: Additional metadata
    """
    
    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    job_id: str = ""
    job_name: str = ""
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    status: str = "running"
    fetched_stocks: List[str] = field(default_factory=list)
    failed_stocks: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    total_stocks: int = 0
    duration_seconds: Optional[float] = None
    triggered_by: str = "scheduler_auto"
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "execution_id": self.execution_id,
            "job_id": self.job_id,
            "job_name": self.job_name,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "fetched_stocks": self.fetched_stocks,
            "failed_stocks": self.failed_stocks,
            "errors": self.errors,
            "total_stocks": self.total_stocks,
            "duration_seconds": self.duration_seconds,
            "triggered_by": self.triggered_by,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'JobExecutionRecord':
        """Create from dictionary."""
        return cls(
            execution_id=data.get("execution_id", str(uuid.uuid4())),
            job_id=data.get("job_id", ""),
            job_name=data.get("job_name", ""),
            start_time=datetime.fromisoformat(data["start_time"]),
            end_time=datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None,
            status=data.get("status", "running"),
            fetched_stocks=data.get("fetched_stocks", []),
            failed_stocks=data.get("failed_stocks", []),
            errors=data.get("errors", []),
            total_stocks=data.get("total_stocks", 0),
            duration_seconds=data.get("duration_seconds"),
            triggered_by=data.get("triggered_by", "scheduler_auto"),
            metadata=data.get("metadata", {})
        )
