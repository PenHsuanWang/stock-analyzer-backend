"""
Serving application for scheduler API endpoints.
"""
import threading
import logging
from typing import List, Optional

from core.scheduler.job_scheduler import JobScheduler
from core.scheduler.job_registry import JobRegistry
from core.scheduler.job_executor import JobExecutor
from core.scheduler.job_definition import ScheduledJob
from core.scheduler.job_execution_history import JobExecutionRecord
from core.scheduler.execution_history_registry import ExecutionHistoryRegistry

logger = logging.getLogger(__name__)


class SchedulerServingApp:
    """
    Singleton serving app for scheduler functionality.
    Follows the same pattern as existing serving apps.
    """
    
    _app_instance = None
    _app_lock = threading.Lock()
    
    def __new__(cls, *args, **kwargs):
        """Singleton pattern implementation."""
        with cls._app_lock:
            if cls._app_instance is None:
                cls._app_instance = super().__new__(cls)
                cls._app_instance._initialize()
            return cls._app_instance
    
    def _initialize(self) -> None:
        """Initialize scheduler components."""
        self.registry = JobRegistry()
        self.history_registry = ExecutionHistoryRegistry()
        self.executor = JobExecutor(history_registry=self.history_registry)
        self.scheduler = JobScheduler(
            registry=self.registry,
            executor=self.executor
        )
        
        # Auto-start scheduler
        self.scheduler.start()
        logger.info("SchedulerServingApp initialized and scheduler started")
    
    def create_job(
        self,
        name: str,
        stock_ids: List[str],
        schedule_time: str = "17:00",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        duration_days: Optional[int] = None,
        prefix: str = "scheduled_stock_data"
    ) -> str:
        """
        Create a new scheduled job.
        
        Args:
            name: Job name
            stock_ids: List of stock symbols
            schedule_time: Time to run daily (HH:MM format)
            start_date: Optional start date for data fetching
            end_date: Optional end date for data fetching
            duration_days: Optional sliding window duration in days (overrides start_date)
            prefix: Redis key prefix
            
        Returns:
            job_id: ID of created job
        """
        job = ScheduledJob(
            name=name,
            stock_ids=stock_ids,
            schedule_time=schedule_time,
            start_date=start_date,
            end_date=end_date,
            duration_days=duration_days,
            prefix=prefix
        )
        
        job_id = self.registry.create_job(job)
        logger.info(f"Created job: {name} ({job_id})")
        
        return job_id
    
    def get_job(self, job_id: str) -> Optional[dict]:
        """Get job details by ID."""
        job = self.registry.get_job(job_id)
        return job.to_dict() if job else None
    
    def list_jobs(self, active_only: bool = False) -> List[dict]:
        """List all jobs."""
        jobs = self.registry.list_jobs(active_only=active_only)
        return [job.to_dict() for job in jobs]
    
    def update_job(
        self,
        job_id: str,
        name: Optional[str] = None,
        stock_ids: Optional[List[str]] = None,
        schedule_time: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        duration_days: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> bool:
        """
        Update an existing job.
        
        Args:
            job_id: ID of job to update
            name: New name (optional)
            stock_ids: New stock list (optional)
            schedule_time: New schedule time (optional)
            start_date: New start date (optional)
            end_date: New end date (optional)
            duration_days: New sliding window duration (optional)
            is_active: New active status (optional)
            
        Returns:
            True if successful
        """
        job = self.registry.get_job(job_id)
        if not job:
            return False
        
        # Update fields if provided
        if name is not None:
            job.name = name
        if stock_ids is not None:
            job.stock_ids = stock_ids
        if schedule_time is not None:
            job.schedule_time = schedule_time
        if start_date is not None:
            job.start_date = start_date
        if end_date is not None:
            job.end_date = end_date
        if duration_days is not None:
            job.duration_days = duration_days
        if is_active is not None:
            job.is_active = is_active
        
        return self.registry.update_job(job)
    
    def delete_job(self, job_id: str) -> bool:
        """Delete a job."""
        return self.registry.delete_job(job_id)
    
    def start_job(self, job_id: str) -> bool:
        """Activate a job."""
        return self.update_job(job_id, is_active=True)
    
    def stop_job(self, job_id: str) -> bool:
        """Deactivate a job."""
        return self.update_job(job_id, is_active=False)
    
    def get_scheduler_status(self) -> dict:
        """Get scheduler status."""
        return {
            "is_running": self.scheduler.is_running(),
            "active_jobs_count": len(self.registry.get_active_jobs()),
            "total_jobs_count": len(self.registry.list_jobs())
        }
    
    def get_job_execution_history(
        self,
        job_id: str,
        limit: int = 50,
        status: Optional[str] = None
    ) -> List[JobExecutionRecord]:
        """
        Get execution history for a job.
        
        Args:
            job_id: Job ID to get history for
            limit: Maximum number of records to return
            status: Optional status filter
            
        Returns:
            List of JobExecutionRecord
        """
        return self.history_registry.get_job_history(job_id, limit=limit, status=status)
    
    def get_latest_execution(self, job_id: str) -> Optional[JobExecutionRecord]:
        """
        Get the most recent execution for a job.
        
        Args:
            job_id: Job ID
            
        Returns:
            JobExecutionRecord if found, None otherwise
        """
        return self.history_registry.get_latest_execution(job_id)
    
    def get_execution(self, execution_id: str) -> Optional[JobExecutionRecord]:
        """
        Get a specific execution record.
        
        Args:
            execution_id: Execution ID
            
        Returns:
            JobExecutionRecord if found, None otherwise
        """
        return self.history_registry.get_execution(execution_id)


def get_scheduler_app() -> SchedulerServingApp:
    """Get singleton instance of scheduler app."""
    return SchedulerServingApp()
