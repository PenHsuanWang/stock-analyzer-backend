"""
Execution history registry for persisting job execution records.
"""
import json
import logging
from typing import List, Optional
from datetime import datetime, timedelta

from utils.database_adapters.redis_adapter import RedisAdapter
from core.scheduler.job_execution_history import JobExecutionRecord

logger = logging.getLogger(__name__)


class ExecutionHistoryRegistry:
    """
    Manages persistence of job execution history in Redis.
    
    Redis keys used:
        scheduler:execution_history:{execution_id} - Individual execution records
        scheduler:job_history_index:{job_id} - List of execution IDs per job
    """
    
    EXECUTION_KEY_PREFIX = "scheduler:execution_history:"
    JOB_HISTORY_INDEX_PREFIX = "scheduler:job_history_index:"
    DEFAULT_TTL_DAYS = 30
    MAX_HISTORY_PER_JOB = 100
    
    def __init__(self, adapter: Optional[RedisAdapter] = None):
        """
        Initialize execution history registry.
        
        Args:
            adapter: Redis adapter instance. If None, creates new instance.
        """
        self._adapter = adapter or RedisAdapter()
    
    def save_execution(self, record: JobExecutionRecord) -> bool:
        """
        Save execution record to Redis with TTL.
        
        Args:
            record: JobExecutionRecord to save
            
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            # Save execution record
            key = f"{self.EXECUTION_KEY_PREFIX}{record.execution_id}"
            data = json.dumps(record.to_dict())
            
            # Set with TTL (30 days default)
            ttl_seconds = self.DEFAULT_TTL_DAYS * 24 * 60 * 60
            self._adapter.set(key, data, ex=ttl_seconds)
            
            # Update job history index
            self._add_to_job_history_index(record.job_id, record.execution_id)
            
            logger.info(f"Saved execution record: {record.execution_id} for job: {record.job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save execution record {record.execution_id}: {str(e)}")
            return False
    
    def get_execution(self, execution_id: str) -> Optional[JobExecutionRecord]:
        """
        Retrieve a specific execution record.
        
        Args:
            execution_id: Execution ID to retrieve
            
        Returns:
            JobExecutionRecord if found, None otherwise
        """
        try:
            key = f"{self.EXECUTION_KEY_PREFIX}{execution_id}"
            data = self._adapter.get(key)
            
            if not data:
                return None
            
            record_dict = json.loads(data)
            return JobExecutionRecord.from_dict(record_dict)
            
        except Exception as e:
            logger.error(f"Failed to get execution record {execution_id}: {str(e)}")
            return None
    
    def get_job_history(
        self,
        job_id: str,
        limit: int = 50,
        status: Optional[str] = None
    ) -> List[JobExecutionRecord]:
        """
        Get execution history for a specific job.
        
        Args:
            job_id: Job ID to get history for
            limit: Maximum number of records to return
            status: Optional status filter (success, failed, partial_success)
            
        Returns:
            List of JobExecutionRecord, newest first
        """
        try:
            # Get execution IDs from index
            index_key = f"{self.JOB_HISTORY_INDEX_PREFIX}{job_id}"
            execution_ids_json = self._adapter.get(index_key)
            
            if not execution_ids_json:
                return []
            
            execution_ids = json.loads(execution_ids_json)
            
            # Retrieve execution records
            records = []
            for exec_id in execution_ids[:limit]:
                record = self.get_execution(exec_id)
                if record:
                    # Apply status filter if specified
                    if status is None or record.status == status:
                        records.append(record)
            
            return records
            
        except Exception as e:
            logger.error(f"Failed to get job history for {job_id}: {str(e)}")
            return []
    
    def get_latest_execution(self, job_id: str) -> Optional[JobExecutionRecord]:
        """
        Get the most recent execution record for a job.
        
        Args:
            job_id: Job ID to get latest execution for
            
        Returns:
            JobExecutionRecord if found, None otherwise
        """
        try:
            history = self.get_job_history(job_id, limit=1)
            return history[0] if history else None
            
        except Exception as e:
            logger.error(f"Failed to get latest execution for job {job_id}: {str(e)}")
            return None
    
    def _add_to_job_history_index(self, job_id: str, execution_id: str) -> None:
        """
        Add execution ID to job history index.
        Maintains list with newest first, limited to MAX_HISTORY_PER_JOB.
        
        Args:
            job_id: Job ID
            execution_id: Execution ID to add
        """
        try:
            index_key = f"{self.JOB_HISTORY_INDEX_PREFIX}{job_id}"
            
            # Get existing index
            existing_json = self._adapter.get(index_key)
            execution_ids = json.loads(existing_json) if existing_json else []
            
            # Add new execution ID at the beginning (newest first)
            execution_ids.insert(0, execution_id)
            
            # Limit to MAX_HISTORY_PER_JOB
            execution_ids = execution_ids[:self.MAX_HISTORY_PER_JOB]
            
            # Save updated index with TTL
            ttl_seconds = self.DEFAULT_TTL_DAYS * 24 * 60 * 60
            self._adapter.set(index_key, json.dumps(execution_ids), ex=ttl_seconds)
            
        except Exception as e:
            logger.error(f"Failed to update job history index for {job_id}: {str(e)}")
    
    def delete_execution(self, execution_id: str) -> bool:
        """
        Delete a specific execution record.
        
        Args:
            execution_id: Execution ID to delete
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            key = f"{self.EXECUTION_KEY_PREFIX}{execution_id}"
            self._adapter.delete(key)
            logger.info(f"Deleted execution record: {execution_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete execution record {execution_id}: {str(e)}")
            return False
    
    def delete_job_history(self, job_id: str) -> bool:
        """
        Delete all execution history for a job.
        
        Args:
            job_id: Job ID to delete history for
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            # Get all execution IDs for the job
            index_key = f"{self.JOB_HISTORY_INDEX_PREFIX}{job_id}"
            execution_ids_json = self._adapter.get(index_key)
            
            if execution_ids_json:
                execution_ids = json.loads(execution_ids_json)
                
                # Delete each execution record
                for exec_id in execution_ids:
                    self.delete_execution(exec_id)
            
            # Delete the index
            self._adapter.delete(index_key)
            logger.info(f"Deleted all execution history for job: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete job history for {job_id}: {str(e)}")
            return False
    
    def get_execution_count(self, job_id: str) -> int:
        """
        Get the number of execution records for a job.
        
        Args:
            job_id: Job ID to count executions for
            
        Returns:
            int: Number of execution records
        """
        try:
            index_key = f"{self.JOB_HISTORY_INDEX_PREFIX}{job_id}"
            execution_ids_json = self._adapter.get(index_key)
            
            if not execution_ids_json:
                return 0
            
            execution_ids = json.loads(execution_ids_json)
            return len(execution_ids)
            
        except Exception as e:
            logger.error(f"Failed to get execution count for {job_id}: {str(e)}")
            return 0
