"""
Main job scheduler that manages periodic execution of jobs.
"""
import threading
import time
import logging
from datetime import datetime, time as dt_time, timedelta
from typing import Optional

from core.scheduler.job_definition import ScheduledJob, JobStatus
from core.scheduler.job_registry import JobRegistry
from core.scheduler.job_executor import JobExecutor

logger = logging.getLogger(__name__)


class JobScheduler:
    """
    Main scheduler that runs in a background thread and executes jobs.
    """
    
    def __init__(
        self,
        registry: Optional[JobRegistry] = None,
        executor: Optional[JobExecutor] = None,
        check_interval: int = 60
    ):
        """
        Initialize job scheduler.
        
        Args:
            registry: JobRegistry for managing jobs
            executor: JobExecutor for running jobs
            check_interval: Seconds between schedule checks
        """
        self.registry = registry or JobRegistry()
        self.executor = executor or JobExecutor()
        self.check_interval = check_interval
        
        self._scheduler_thread: Optional[threading.Thread] = None
        self._is_running = False
        self._stop_event = threading.Event()
        self._lock = threading.Lock()
    
    def start(self) -> None:
        """Start the scheduler thread."""
        with self._lock:
            if self._is_running:
                logger.warning("Scheduler is already running")
                return
            
            self._is_running = True
            self._stop_event.clear()
            
            self._scheduler_thread = threading.Thread(
                target=self._scheduler_loop,
                daemon=True,
                name="JobSchedulerThread"
            )
            self._scheduler_thread.start()
            
            logger.info("Job scheduler started")
    
    def stop(self) -> None:
        """Stop the scheduler thread."""
        with self._lock:
            if not self._is_running:
                logger.warning("Scheduler is not running")
                return
            
            self._is_running = False
            self._stop_event.set()
            
            if self._scheduler_thread:
                self._scheduler_thread.join(timeout=5)
            
            logger.info("Job scheduler stopped")
    
    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self._is_running
    
    def _scheduler_loop(self) -> None:
        """Main scheduler loop that checks and executes jobs."""
        logger.info("Scheduler loop started")
        
        while not self._stop_event.is_set():
            try:
                self._check_and_execute_jobs()
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}", exc_info=True)
            
            # Wait for check_interval or until stop signal
            self._stop_event.wait(self.check_interval)
        
        logger.info("Scheduler loop stopped")
    
    def _check_and_execute_jobs(self) -> None:
        """Check all active jobs and execute those that are due."""
        active_jobs = self.registry.get_active_jobs()
        
        if not active_jobs:
            return
        
        current_time = datetime.now()
        
        for job in active_jobs:
            try:
                # Calculate next run time if not set
                if job.next_run is None:
                    job.next_run = self._calculate_next_run_time(
                        job.schedule_time,
                        current_time
                    )
                    self.registry.update_job(job)
                
                # Check if job should run
                if current_time >= job.next_run:
                    self._execute_job_async(job)
                    
            except Exception as e:
                logger.error(
                    f"Error processing job {job.name} ({job.job_id}): {e}",
                    exc_info=True
                )
    
    def _execute_job_async(self, job: ScheduledJob) -> None:
        """
        Execute job in a separate thread to avoid blocking scheduler.
        
        Args:
            job: Job to execute
        """
        def run_job():
            try:
                # Update status to running
                job.status = JobStatus.RUNNING
                self.registry.update_job(job)
                
                # Execute the job
                result = self.executor.execute_job(job)
                
                # Update job after execution
                job.last_run = datetime.now()
                job.next_run = self._calculate_next_run_time(
                    job.schedule_time,
                    job.last_run
                )
                
                if result["status"] == "success":
                    job.status = JobStatus.COMPLETED
                elif result["status"] == "failed":
                    job.status = JobStatus.FAILED
                else:
                    job.status = JobStatus.COMPLETED  # partial_success
                
                self.registry.update_job(job)
                
                logger.info(
                    f"Job {job.name} executed. "
                    f"Next run: {job.next_run.isoformat()}"
                )
                
            except Exception as e:
                logger.error(
                    f"Error executing job {job.name}: {e}",
                    exc_info=True
                )
                job.status = JobStatus.FAILED
                job.last_run = datetime.now()
                self.registry.update_job(job)
        
        # Start job execution in separate thread
        job_thread = threading.Thread(
            target=run_job,
            daemon=True,
            name=f"JobExecution-{job.job_id}"
        )
        job_thread.start()
    
    @staticmethod
    def _calculate_next_run_time(
        schedule_time: str,
        from_time: datetime
    ) -> datetime:
        """
        Calculate next run time based on schedule.
        
        Args:
            schedule_time: Time in HH:MM format
            from_time: Calculate from this time
            
        Returns:
            Next scheduled datetime
        """
        scheduled_time = dt_time.fromisoformat(schedule_time)
        
        # Create datetime for today at scheduled time
        next_run = datetime.combine(
            from_time.date(),
            scheduled_time
        )
        
        # If scheduled time has passed today, schedule for tomorrow
        if next_run <= from_time:
            next_run += timedelta(days=1)
        
        return next_run
