# Scheduler Module Design Document

**Feature:** Periodic Stock Data Fetching with Cron-like Scheduling  
**Design Date:** October 2025  
**Status:** Design Phase  

---

## 1. Requirements Summary

### Functional Requirements:
1. Allow users to create scheduled jobs for fetching stock data
2. Support multiple stock IDs per job
3. Schedule jobs to run daily at specific times (e.g., 5 PM)
4. Jobs should fetch data from yfinance and store in Redis
5. Support multiple concurrent scheduled jobs
6. Allow users to manage jobs (create, list, update, delete, start, stop)

### Non-Functional Requirements:
1. **Zero Impact:** Must not modify existing code architecture
2. **Open-Close Principle:** Extend functionality without modifying existing modules
3. **Thread-Safe:** Handle concurrent job execution
4. **Fault-Tolerant:** Jobs should continue even if one fails
5. **Configurable:** Allow flexible scheduling patterns

---

## 2. Architecture Overview

### 2.1 Module Structure

The new scheduler module will integrate as a separate component following your existing pattern:

```
src/
├── core/
│   ├── analyzer/          (existing - no changes)
│   ├── manager/           (existing - no changes)
│   ├── processor/         (existing - no changes)
│   └── scheduler/         ← NEW MODULE
│       ├── __init__.py
│       ├── job_scheduler.py           # Main scheduler engine
│       ├── job_definition.py          # Job data models
│       ├── job_executor.py            # Job execution logic
│       └── job_registry.py            # Job storage/management
├── utils/                 (existing - no changes)
└── webapp/
    ├── serving_app/
    │   ├── ...            (existing - no changes)
    │   └── scheduler_serving_app.py   ← NEW
    └── router/
        ├── ...            (existing - no changes)
        └── scheduler_serving_app_router.py  ← NEW
```

### 2.2 Integration Points

**Existing Components Used (Read-Only):**
- ✅ `YFinanceFetcher` (from `utils.data_inbound.data_fetcher`)
- ✅ `DataIOButler` (from `core.manager.data_manager`)
- ✅ `RedisAdapter` (from `utils.database_adapters.redis_adapter`)

**No Modifications Required:**
- ❌ No changes to existing analyzers
- ❌ No changes to existing serving apps
- ❌ No changes to existing routers
- ❌ No changes to existing managers

---

## 3. Class Design

### 3.1 Class Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Scheduler Module                          │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────────┐
│   ScheduledJob           │  (Data Model)
├──────────────────────────┤
│ - job_id: str            │
│ - name: str              │
│ - stock_ids: List[str]   │
│ - schedule_time: str     │  # "17:00" format
│ - is_active: bool        │
│ - created_at: datetime   │
│ - last_run: datetime     │
│ - next_run: datetime     │
│ - status: JobStatus      │
├──────────────────────────┤
│ + to_dict(): dict        │
│ + from_dict(): Self      │
│ + validate(): bool       │
└──────────────────────────┘
            △
            │
            │ uses
            │
┌──────────────────────────┐
│   JobRegistry            │  (Storage Manager)
├──────────────────────────┤
│ - adapter: AbstractDB    │
│ - _lock: Lock            │
├──────────────────────────┤
│ + create_job()           │
│ + get_job()              │
│ + list_jobs()            │
│ + update_job()           │
│ + delete_job()           │
│ + get_active_jobs()      │
└──────────────────────────┘
            △
            │
            │ uses
            │
┌──────────────────────────┐
│   JobExecutor            │  (Execution Logic)
├──────────────────────────┤
│ - data_fetcher: Fetcher  │
│ - data_butler: Butler    │
│ - _execution_lock: Lock  │
├──────────────────────────┤
│ + execute_job()          │
│ + fetch_and_store()      │
│ - _handle_error()        │
│ - _update_job_status()   │
└──────────────────────────┘
            △
            │
            │ uses
            │
┌──────────────────────────┐
│   JobScheduler           │  (Main Scheduler)
├──────────────────────────┤
│ - registry: JobRegistry  │
│ - executor: JobExecutor  │
│ - scheduler_thread: Thrd │
│ - is_running: bool       │
│ - check_interval: int    │
├──────────────────────────┤
│ + start()                │
│ + stop()                 │
│ + add_job()              │
│ + remove_job()           │
│ - _scheduler_loop()      │
│ - _check_and_execute()   │
│ - _calculate_next_run()  │
└──────────────────────────┘


┌─────────────────────────────────────────────────────────────┐
│                  Webapp Layer (API)                          │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────────┐
│ SchedulerServingApp      │  (Singleton)
├──────────────────────────┤
│ - scheduler: JobScheduler│
│ - _app_lock: Lock        │
├──────────────────────────┤
│ + create_scheduled_job() │
│ + get_job()              │
│ + list_jobs()            │
│ + update_job()           │
│ + delete_job()           │
│ + start_job()            │
│ + stop_job()             │
│ + get_job_status()       │
└──────────────────────────┘
            △
            │
            │ exposes
            │
┌──────────────────────────┐
│   FastAPI Router         │
├──────────────────────────┤
│ POST   /scheduler/jobs   │
│ GET    /scheduler/jobs   │
│ GET    /scheduler/jobs/{id}
│ PUT    /scheduler/jobs/{id}
│ DELETE /scheduler/jobs/{id}
│ POST   /scheduler/jobs/{id}/start
│ POST   /scheduler/jobs/{id}/stop
│ GET    /scheduler/jobs/{id}/status
└──────────────────────────┘
```

### 3.2 Integration with Existing Components

```
┌────────────────────────────────────────────────────────┐
│         Existing Components (No Modifications)          │
└────────────────────────────────────────────────────────┘

    ┌──────────────────┐
    │  YFinanceFetcher │  (Reused as-is)
    └────────┬─────────┘
             │
             │ used by
             │
    ┌────────▼─────────┐
    │   JobExecutor    │  (New - wraps existing)
    └────────┬─────────┘
             │
             │ stores to
             │
    ┌────────▼─────────┐
    │  DataIOButler    │  (Reused as-is)
    └────────┬─────────┘
             │
             │ uses
             │
    ┌────────▼─────────┐
    │   RedisAdapter   │  (Reused as-is)
    └──────────────────┘
```

---

## 4. Detailed Class Specifications

### 4.1 ScheduledJob (Data Model)

**File:** `src/core/scheduler/job_definition.py`

```python
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
    schedule_time: str = "17:00"  # Default 5 PM
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
```

### 4.2 JobRegistry (Storage Manager)

**File:** `src/core/scheduler/job_registry.py`

```python
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
```

### 4.3 JobExecutor (Execution Logic)

**File:** `src/core/scheduler/job_executor.py`

```python
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

logger = logging.getLogger(__name__)


class JobExecutionError(Exception):
    """Exception raised when job execution fails."""
    pass


class JobExecutor:
    """
    Executes scheduled jobs by fetching stock data and storing it.
    Wraps existing components without modifying them.
    """
    
    def __init__(self):
        """Initialize job executor with existing components."""
        self._data_fetcher = YFinanceFetcher()
        self._data_butler = DataIOButler(adapter=RedisAdapter())
        self._execution_lock = threading.Lock()
    
    def execute_job(self, job: ScheduledJob) -> dict:
        """
        Execute a scheduled job.
        
        Args:
            job: ScheduledJob instance to execute
            
        Returns:
            dict: Execution result with status and details
        """
        execution_result = {
            "job_id": job.job_id,
            "job_name": job.name,
            "start_time": datetime.now().isoformat(),
            "status": "success",
            "fetched_stocks": [],
            "failed_stocks": [],
            "errors": []
        }
        
        logger.info(f"Starting execution of job: {job.name} ({job.job_id})")
        
        # Calculate date range
        end_date = job.end_date or date.today().isoformat()
        start_date = job.start_date or self._calculate_default_start_date()
        
        # Fetch and store data for each stock
        for stock_id in job.stock_ids:
            try:
                self._fetch_and_store_single_stock(
                    stock_id=stock_id,
                    start_date=start_date,
                    end_date=end_date,
                    prefix=job.prefix
                )
                execution_result["fetched_stocks"].append(stock_id)
                logger.info(f"Successfully fetched and stored data for {stock_id}")
                
            except Exception as e:
                error_msg = f"Failed to fetch {stock_id}: {str(e)}"
                logger.error(error_msg)
                execution_result["failed_stocks"].append(stock_id)
                execution_result["errors"].append(error_msg)
        
        # Determine overall status
        if execution_result["failed_stocks"]:
            if execution_result["fetched_stocks"]:
                execution_result["status"] = "partial_success"
            else:
                execution_result["status"] = "failed"
        
        execution_result["end_time"] = datetime.now().isoformat()
        
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
        prefix: str
    ) -> None:
        """
        Fetch and store data for a single stock.
        Uses existing components without modification.
        
        Args:
            stock_id: Stock symbol to fetch
            start_date: Start date for data range
            end_date: End date for data range
            prefix: Redis key prefix
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
        
        # Store data using existing DataIOButler
        self._data_butler.save_data(
            data=df,
            prefix=prefix,
            stock_id=stock_id,
            start_date=start_date,
            end_date=end_date
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
```

### 4.4 JobScheduler (Main Scheduler Engine)

**File:** `src/core/scheduler/job_scheduler.py`

```python
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
        check_interval: int = 60  # Check every 60 seconds
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
```

---

## 5. Webapp Integration

### 5.1 SchedulerServingApp (Singleton Service)

**File:** `src/webapp/serving_app/scheduler_serving_app.py`

```python
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
        self.executor = JobExecutor()
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


def get_scheduler_app() -> SchedulerServingApp:
    """Get singleton instance of scheduler app."""
    return SchedulerServingApp()
```

### 5.2 FastAPI Router

**File:** `src/webapp/router/scheduler_serving_app_router.py`

```python
"""
FastAPI router for scheduler endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel, validator
from typing import List, Optional
import re

from webapp.serving_app.scheduler_serving_app import (
    SchedulerServingApp,
    get_scheduler_app
)

router = APIRouter(prefix="/scheduler", tags=["scheduler"])


# Request/Response Models
class CreateJobRequest(BaseModel):
    """Request model for creating a scheduled job."""
    name: str
    stock_ids: List[str]
    schedule_time: str = "17:00"
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    prefix: str = "scheduled_stock_data"
    
    @validator('schedule_time')
    def validate_time_format(cls, v):
        """Validate time format."""
        if not re.match(r'^([01]\d|2[0-3]):([0-5]\d)$', v):
            raise ValueError('Invalid time format. Use HH:MM')
        return v
    
    @validator('stock_ids')
    def validate_stock_ids(cls, v):
        """Validate stock IDs."""
        if not v:
            raise ValueError('At least one stock ID is required')
        return v


class UpdateJobRequest(BaseModel):
    """Request model for updating a job."""
    name: Optional[str] = None
    stock_ids: Optional[List[str]] = None
    schedule_time: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    is_active: Optional[bool] = None


class JobResponse(BaseModel):
    """Response model for job details."""
    job_id: str
    name: str
    stock_ids: List[str]
    schedule_time: str
    is_active: bool
    status: str
    created_at: str
    last_run: Optional[str]
    next_run: Optional[str]


# Endpoints
@router.post("/jobs", response_model=dict)
def create_job(
    request: CreateJobRequest = Body(...),
    app: SchedulerServingApp = Depends(get_scheduler_app)
):
    """
    Create a new scheduled job.
    
    The job will automatically run daily at the specified time.
    """
    try:
        job_id = app.create_job(
            name=request.name,
            stock_ids=request.stock_ids,
            schedule_time=request.schedule_time,
            start_date=request.start_date,
            end_date=request.end_date,
            prefix=request.prefix
        )
        return {
            "message": "Job created successfully",
            "job_id": job_id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/jobs", response_model=List[dict])
def list_jobs(
    active_only: bool = False,
    app: SchedulerServingApp = Depends(get_scheduler_app)
):
    """
    List all scheduled jobs.
    
    Query Parameters:
        active_only: If true, return only active jobs
    """
    return app.list_jobs(active_only=active_only)


@router.get("/jobs/{job_id}", response_model=dict)
def get_job(
    job_id: str,
    app: SchedulerServingApp = Depends(get_scheduler_app)
):
    """Get details of a specific job."""
    job = app.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.put("/jobs/{job_id}", response_model=dict)
def update_job(
    job_id: str,
    request: UpdateJobRequest = Body(...),
    app: SchedulerServingApp = Depends(get_scheduler_app)
):
    """Update an existing job."""
    success = app.update_job(
        job_id=job_id,
        name=request.name,
        stock_ids=request.stock_ids,
        schedule_time=request.schedule_time,
        start_date=request.start_date,
        end_date=request.end_date,
        is_active=request.is_active
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"message": "Job updated successfully"}


@router.delete("/jobs/{job_id}", response_model=dict)
def delete_job(
    job_id: str,
    app: SchedulerServingApp = Depends(get_scheduler_app)
):
    """Delete a scheduled job."""
    success = app.delete_job(job_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"message": "Job deleted successfully"}


@router.post("/jobs/{job_id}/start", response_model=dict)
def start_job(
    job_id: str,
    app: SchedulerServingApp = Depends(get_scheduler_app)
):
    """Activate a job to start running on schedule."""
    success = app.start_job(job_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"message": "Job started successfully"}


@router.post("/jobs/{job_id}/stop", response_model=dict)
def stop_job(
    job_id: str,
    app: SchedulerServingApp = Depends(get_scheduler_app)
):
    """Deactivate a job to stop it from running."""
    success = app.stop_job(job_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"message": "Job stopped successfully"}


@router.get("/status", response_model=dict)
def get_scheduler_status(
    app: SchedulerServingApp = Depends(get_scheduler_app)
):
    """Get scheduler status and statistics."""
    return app.get_scheduler_status()
```

---

## 6. Integration with Existing Server

**File:** `src/server.py` (Add one line only)

```python
# src/server.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from webapp.router import data_fetcher_serving_app_router, data_manager_serving_app_router
from webapp.router import stock_analyzer_basic_serving_app_router
from webapp.router import scheduler_serving_app_router  # ← ADD THIS LINE

origins = [
    "http://localhost:3000",  # for react application development
]

app = FastAPI()

# Include the router in the main FastAPI app
app.include_router(data_fetcher_serving_app_router.router)
app.include_router(data_manager_serving_app_router.router)
app.include_router(stock_analyzer_basic_serving_app_router.router)
app.include_router(scheduler_serving_app_router.router)  # ← ADD THIS LINE


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 7. Design Principles Applied

### 7.1 Open-Close Principle ✅

**Open for Extension:**
- New scheduler module adds functionality
- Existing components reused through composition
- New endpoints added via router

**Closed for Modification:**
- Zero changes to existing analyzers
- Zero changes to existing managers
- Zero changes to existing fetchers
- Only 2 lines added to server.py (include router)

### 7.2 Single Responsibility Principle ✅

Each class has one clear responsibility:
- `ScheduledJob`: Data model
- `JobRegistry`: Persistence
- `JobExecutor`: Execution logic
- `JobScheduler`: Scheduling coordination
- `SchedulerServingApp`: API service
- Router: HTTP endpoints

### 7.3 Dependency Inversion ✅

- Scheduler depends on abstractions (interfaces)
- Uses `AbstractDatabaseAdapter` not concrete Redis
- JobExecutor wraps existing components
- No tight coupling to implementations

### 7.4 No Side Effects ✅

**Guarantees:**
1. Existing code unchanged (except 2 lines in server.py)
2. Existing functionality unaffected
3. Can be disabled by not including router
4. Scheduler runs in separate thread
5. No interference with existing data flows

---

## 8. Usage Examples

### 8.1 Create a Scheduled Job

```bash
curl -X POST "http://localhost:8001/scheduler/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Daily Tech Stocks",
    "stock_ids": ["AAPL", "MSFT", "GOOGL", "AMZN"],
    "schedule_time": "17:00",
    "prefix": "scheduled_stock_data"
  }'

# Response:
{
  "message": "Job created successfully",
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### 8.2 List All Jobs

```bash
curl -X GET "http://localhost:8001/scheduler/jobs"

# Response:
[
  {
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Daily Tech Stocks",
    "stock_ids": ["AAPL", "MSFT", "GOOGL", "AMZN"],
    "schedule_time": "17:00",
    "is_active": true,
    "status": "completed",
    "created_at": "2025-10-21T10:00:00",
    "last_run": "2025-10-21T17:00:00",
    "next_run": "2025-10-22T17:00:00"
  }
]
```

### 8.3 Update a Job

```bash
curl -X PUT "http://localhost:8001/scheduler/jobs/550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "stock_ids": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"],
    "schedule_time": "18:00"
  }'
```

### 8.4 Stop a Job

```bash
curl -X POST "http://localhost:8001/scheduler/jobs/550e8400-e29b-41d4-a716-446655440000/stop"
```

### 8.5 Get Scheduler Status

```bash
curl -X GET "http://localhost:8001/scheduler/status"

# Response:
{
  "is_running": true,
  "active_jobs_count": 3,
  "total_jobs_count": 5
}
```

---

## 9. Testing Strategy

### 9.1 Unit Tests

Create `tests/test_core/test_scheduler/` directory:

```
tests/test_core/test_scheduler/
├── __init__.py
├── test_job_definition.py
├── test_job_registry.py
├── test_job_executor.py
└── test_job_scheduler.py
```

### 9.2 Integration Tests

Create `tests/test_scheduler_integration.py`:

```python
def test_full_scheduler_flow(redis_client):
    """Test creating job, scheduler execution, and data storage."""
    # Test will verify end-to-end flow
    pass
```

### 9.3 API Tests

Create `tests/test_routers/test_scheduler_router.py`:

```python
def test_create_job_endpoint(test_client):
    """Test POST /scheduler/jobs endpoint."""
    pass
```

---

## 10. Monitoring and Logging

### 10.1 Logging Points

The design includes logging at key points:
- Job creation/update/deletion
- Scheduler start/stop
- Job execution start/completion
- Errors and failures

### 10.2 Metrics to Track

Recommended metrics:
- Number of active jobs
- Jobs executed successfully
- Jobs failed
- Average execution time
- Next scheduled runs

---

## 11. Future Enhancements (Optional)

Potential extensions without breaking design:

1. **Multiple Schedule Patterns**
   - Weekly schedules
   - Custom cron expressions
   - Interval-based scheduling

2. **Job Chaining**
   - Run analysis after data fetch
   - Dependency management

3. **Notifications**
   - Email on job completion/failure
   - Webhook callbacks

4. **Advanced Features**
   - Job priorities
   - Retry policies
   - Concurrent execution limits

---

## 12. Summary

### What This Design Provides:

✅ **Cron-like scheduling** for daily stock data fetching  
✅ **Background thread** for non-blocking execution  
✅ **Full CRUD API** for managing jobs  
✅ **Zero modifications** to existing code (except 2 lines)  
✅ **Open-Close compliant** - extends without modifying  
✅ **Thread-safe** execution with proper locking  
✅ **Fault-tolerant** - individual stock failures don't stop job  
✅ **Follows existing patterns** - matches your architecture  
✅ **Redis-based persistence** - consistent with existing storage  
✅ **RESTful API** - consistent with existing endpoints  

### Files to Create:

**Core Module (5 files):**
1. `src/core/scheduler/__init__.py`
2. `src/core/scheduler/job_definition.py`
3. `src/core/scheduler/job_registry.py`
4. `src/core/scheduler/job_executor.py`
5. `src/core/scheduler/job_scheduler.py`

**Webapp Module (2 files):**
6. `src/webapp/serving_app/scheduler_serving_app.py`
7. `src/webapp/router/scheduler_serving_app_router.py`

**Modification (1 file):**
8. `src/server.py` - Add 2 lines to include router

---

**Design Status:** Ready for Implementation  
**Impact on Existing Code:** Minimal (2 lines)  
**Estimated Implementation Time:** 2-3 days  
**Testing Time:** 1-2 days  

