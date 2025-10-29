"""
Job executor for running scheduled data fetch operations.
"""
import logging
import threading
from datetime import datetime, date
from typing import Optional

from utils.data_inbound.data_fetcher import YFinanceFetcher
from core.manager.data_manager import DataIOButler
from utils.database_adapters.redis_adapter import RedisAdapter
from core.scheduler.job_definition import ScheduledJob, JobStatus
from core.services.metadata_service import MetadataService
from core.scheduler.job_execution_history import JobExecutionRecord
from core.scheduler.execution_history_registry import ExecutionHistoryRegistry

logger = logging.getLogger(__name__)


class JobExecutionError(Exception):
    """Exception raised when job execution fails."""
    pass


class JobExecutor:
    """
    Executes scheduled jobs by fetching stock data and storing it.
    Wraps existing components without modifying them.
    """
    
    def __init__(self, history_registry: Optional[ExecutionHistoryRegistry] = None):
        """Initialize job executor with existing components."""
        self._data_fetcher = YFinanceFetcher()
        self._data_butler = DataIOButler(adapter=RedisAdapter())
        self._execution_lock = threading.Lock()
        self._history_registry = history_registry or ExecutionHistoryRegistry()
    
    def execute_job(self, job: ScheduledJob) -> dict:
        """
        Execute a scheduled job and save execution history.
        
        Args:
            job: ScheduledJob instance to execute
            
        Returns:
            dict: Execution result with status and details
        """
        start_time = datetime.now()
        
        # Create execution record
        execution_record = JobExecutionRecord(
            job_id=job.job_id,
            job_name=job.name,
            start_time=start_time,
            status="running",
            total_stocks=len(job.stock_ids),
            triggered_by="scheduler_auto"
        )
        
        execution_result = {
            "job_id": job.job_id,
            "job_name": job.name,
            "execution_id": execution_record.execution_id,
            "start_time": start_time.isoformat(),
            "status": "success",
            "fetched_stocks": [],
            "failed_stocks": [],
            "errors": []
        }
        
        logger.info(f"Starting execution of job: {job.name} ({job.job_id}), execution_id: {execution_record.execution_id}")
        
        # Calculate date range with sliding window support
        end_date = job.end_date or date.today().isoformat()
        
        # If duration_days is set, calculate start_date as a sliding window
        if job.duration_days is not None:
            start_date = self._calculate_sliding_start_date(job.duration_days)
            logger.info(f"Using sliding window: {job.duration_days} days (from {start_date} to {end_date})")
        else:
            start_date = job.start_date or self._calculate_default_start_date()
        
        # Fetch and store data for each stock
        for stock_id in job.stock_ids:
            try:
                self._fetch_and_store_single_stock(
                    stock_id=stock_id,
                    start_date=start_date,
                    end_date=end_date,
                    prefix=job.prefix,
                    job=job
                )
                execution_result["fetched_stocks"].append(stock_id)
                execution_record.fetched_stocks.append(stock_id)
                logger.info(f"Successfully fetched and stored data for {stock_id}")
                
            except Exception as e:
                error_msg = f"Failed to fetch {stock_id}: {str(e)}"
                logger.error(error_msg)
                execution_result["failed_stocks"].append(stock_id)
                execution_result["errors"].append(error_msg)
                execution_record.failed_stocks.append(stock_id)
                execution_record.errors.append(error_msg)
        
        # Determine overall status
        if execution_result["failed_stocks"]:
            if execution_result["fetched_stocks"]:
                execution_result["status"] = "partial_success"
                execution_record.status = "partial_success"
            else:
                execution_result["status"] = "failed"
                execution_record.status = "failed"
        else:
            execution_result["status"] = "success"
            execution_record.status = "success"
        
        # Complete execution record
        end_time = datetime.now()
        execution_result["end_time"] = end_time.isoformat()
        execution_record.end_time = end_time
        execution_record.duration_seconds = (end_time - start_time).total_seconds()
        
        # Save execution history
        try:
            self._history_registry.save_execution(execution_record)
            logger.info(f"Saved execution history for {execution_record.execution_id}")
        except Exception as e:
            logger.error(f"Failed to save execution history: {str(e)}")
        
        logger.info(
            f"Completed job: {job.name}. "
            f"Success: {len(execution_result['fetched_stocks'])}, "
            f"Failed: {len(execution_result['failed_stocks'])}"
        )
        
        return execution_result
    
    def _fetch_and_store_single_stock(
        self,
        stock_id: str,
        start_date: str,
        end_date: str,
        prefix: str,
        job: Optional[ScheduledJob] = None
    ) -> None:
        """
        Fetch and store data for a single stock with metadata.
        Uses existing components without modification.
        
        Args:
            stock_id: Stock symbol to fetch
            start_date: Start date for data range
            end_date: End date for data range
            prefix: Redis key prefix
            job: Optional ScheduledJob instance for metadata creation
        """
        # Fetch data using existing YFinanceFetcher
        self._data_fetcher.fetch_from_source(
            stock_id=stock_id,
            start_date=start_date,
            end_date=end_date
        )
        
        df = self._data_fetcher.get_as_dataframe()
        
        if df.empty:
            raise JobExecutionError(f"No data returned for {stock_id}")
        
        # Create metadata if job is provided
        metadata = None
        if job is not None:
            next_update = MetadataService.calculate_next_run_time(job.schedule_time)
            metadata = MetadataService.create_job_metadata(
                job_id=job.job_id,
                job_name=job.name,
                schedule_time=job.schedule_time,
                next_update=next_update
            )
            logger.info(f"Created metadata for {stock_id} from job {job.name}")
        
        # Store data using existing DataIOButler
        self._data_butler.save_data(
            data=df,
            prefix=prefix,
            stock_id=stock_id,
            start_date=start_date,
            end_date=end_date,
            metadata=metadata
        )
    
    @staticmethod
    def _calculate_default_start_date() -> str:
        """
        Calculate default start date (30 days ago).
        
        Returns:
            Date string in YYYY-MM-DD format
        """
        from datetime import timedelta
        default_start = date.today() - timedelta(days=30)
        return default_start.isoformat()
    
    @staticmethod
    def _calculate_sliding_start_date(duration_days: int) -> str:
        """
        Calculate start date based on sliding window duration.
        
        Args:
            duration_days: Number of days to go back from today
            
        Returns:
            Date string in YYYY-MM-DD format
        """
        from datetime import timedelta
        sliding_start = date.today() - timedelta(days=duration_days)
        return sliding_start.isoformat()
