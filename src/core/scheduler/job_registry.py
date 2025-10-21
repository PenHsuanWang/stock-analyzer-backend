"""
Job registry for managing scheduled job persistence.
"""
import json
import threading
from typing import List, Optional
from utils.database_adapters.base import AbstractDatabaseAdapter
from utils.database_adapters.redis_adapter import RedisAdapter
from core.scheduler.job_definition import ScheduledJob


class JobRegistry:
    """
    Manages storage and retrieval of scheduled jobs.
    Uses Redis adapter for persistence without modifying existing code.
    """
    
    def __init__(self, adapter: Optional[AbstractDatabaseAdapter] = None):
        """
        Initialize job registry.
        
        Args:
            adapter: Database adapter for storage (defaults to RedisAdapter)
        """
        self.adapter = adapter or RedisAdapter()
        self._lock = threading.Lock()
        self._job_key_prefix = "scheduler:job"
        self._job_index_key = "scheduler:job_index"
    
    def create_job(self, job: ScheduledJob) -> str:
        """
        Create a new scheduled job.
        
        Args:
            job: ScheduledJob instance to create
            
        Returns:
            job_id: The ID of the created job
        """
        job.validate()
        
        with self._lock:
            # Store job data
            job_key = f"{self._job_key_prefix}:{job.job_id}"
            self.adapter.save_data(job_key, json.dumps(job.to_dict()))
            
            # Add to index
            self._add_to_index(job.job_id)
        
        return job.job_id
    
    def get_job(self, job_id: str) -> Optional[ScheduledJob]:
        """
        Retrieve a job by ID.
        
        Args:
            job_id: The ID of the job to retrieve
            
        Returns:
            ScheduledJob instance or None if not found
        """
        job_key = f"{self._job_key_prefix}:{job_id}"
        
        if not self.adapter.exists(job_key):
            return None
        
        job_data = self.adapter.get_data(job_key)
        if job_data:
            return ScheduledJob.from_dict(json.loads(job_data))
        
        return None
    
    def list_jobs(self, active_only: bool = False) -> List[ScheduledJob]:
        """
        List all scheduled jobs.
        
        Args:
            active_only: If True, return only active jobs
            
        Returns:
            List of ScheduledJob instances
        """
        job_ids = self._get_all_job_ids()
        jobs = []
        
        for job_id in job_ids:
            job = self.get_job(job_id)
            if job:
                if not active_only or job.is_active:
                    jobs.append(job)
        
        return jobs
    
    def update_job(self, job: ScheduledJob) -> bool:
        """
        Update an existing job.
        
        Args:
            job: ScheduledJob instance with updated data
            
        Returns:
            True if successful, False otherwise
        """
        job_key = f"{self._job_key_prefix}:{job.job_id}"
        
        if not self.adapter.exists(job_key):
            return False
        
        with self._lock:
            self.adapter.save_data(job_key, json.dumps(job.to_dict()))
        
        return True
    
    def delete_job(self, job_id: str) -> bool:
        """
        Delete a job.
        
        Args:
            job_id: The ID of the job to delete
            
        Returns:
            True if successful, False otherwise
        """
        job_key = f"{self._job_key_prefix}:{job_id}"
        
        with self._lock:
            result = self.adapter.delete_data(job_key)
            if result:
                self._remove_from_index(job_id)
        
        return result
    
    def get_active_jobs(self) -> List[ScheduledJob]:
        """Get all active jobs."""
        return self.list_jobs(active_only=True)
    
    def _add_to_index(self, job_id: str) -> None:
        """Add job ID to the index."""
        job_ids = self._get_all_job_ids()
        if job_id not in job_ids:
            job_ids.append(job_id)
            self.adapter.save_data(
                self._job_index_key,
                json.dumps(job_ids)
            )
    
    def _remove_from_index(self, job_id: str) -> None:
        """Remove job ID from the index."""
        job_ids = self._get_all_job_ids()
        if job_id in job_ids:
            job_ids.remove(job_id)
            self.adapter.save_data(
                self._job_index_key,
                json.dumps(job_ids)
            )
    
    def _get_all_job_ids(self) -> List[str]:
        """Get all job IDs from index."""
        if not self.adapter.exists(self._job_index_key):
            return []
        
        data = self.adapter.get_data(self._job_index_key)
        if data:
            return json.loads(data)
        
        return []
