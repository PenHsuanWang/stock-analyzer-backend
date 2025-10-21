"""
Job definition and data models for the scheduler.
"""
from dataclasses import dataclass, field
from datetime import datetime, time
from typing import List, Optional
from enum import Enum
import uuid


class JobStatus(Enum):
    """Status of a scheduled job."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"


@dataclass
class ScheduledJob:
    """
    Represents a scheduled job for fetching stock data.
    
    Attributes:
        job_id: Unique identifier for the job
        name: Human-readable name for the job
        stock_ids: List of stock symbols to fetch
        schedule_time: Time of day to run (HH:MM format)
        is_active: Whether the job is active
        created_at: When the job was created
        last_run: Last execution time
        next_run: Next scheduled execution time
        status: Current status of the job
        start_date: Start date for data fetching (optional)
        end_date: End date for data fetching (default: today)
        prefix: Redis key prefix for storing data
    """
    
    job_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    stock_ids: List[str] = field(default_factory=list)
    schedule_time: str = "17:00"
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    status: JobStatus = JobStatus.PENDING
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    prefix: str = "scheduled_stock_data"
    
    def validate(self) -> bool:
        """Validate job configuration."""
        if not self.name:
            raise ValueError("Job name is required")
        if not self.stock_ids:
            raise ValueError("At least one stock ID is required")
        if not self._validate_time_format(self.schedule_time):
            raise ValueError("Invalid schedule_time format. Use HH:MM")
        return True
    
    @staticmethod
    def _validate_time_format(time_str: str) -> bool:
        """Validate time string format (HH:MM)."""
        try:
            time.fromisoformat(time_str)
            return True
        except ValueError:
            return False
    
    def to_dict(self) -> dict:
        """Convert job to dictionary for storage."""
        return {
            "job_id": self.job_id,
            "name": self.name,
            "stock_ids": self.stock_ids,
            "schedule_time": self.schedule_time,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": self.next_run.isoformat() if self.next_run else None,
            "status": self.status.value,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "prefix": self.prefix
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ScheduledJob':
        """Create job from dictionary."""
        return cls(
            job_id=data.get("job_id", str(uuid.uuid4())),
            name=data.get("name", ""),
            stock_ids=data.get("stock_ids", []),
            schedule_time=data.get("schedule_time", "17:00"),
            is_active=data.get("is_active", True),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now(),
            last_run=datetime.fromisoformat(data["last_run"]) if data.get("last_run") else None,
            next_run=datetime.fromisoformat(data["next_run"]) if data.get("next_run") else None,
            status=JobStatus(data.get("status", "pending")),
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            prefix=data.get("prefix", "scheduled_stock_data")
        )
