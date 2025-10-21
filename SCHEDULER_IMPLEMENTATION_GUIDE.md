# Scheduler Module - Implementation Guide

## Quick Start Implementation

This guide provides step-by-step instructions to implement the scheduler module.

---

## Implementation Checklist

### Phase 1: Core Module (Day 1-2)

- [ ] **Step 1.1:** Create directory structure
  ```bash
  mkdir -p src/core/scheduler
  touch src/core/scheduler/__init__.py
  ```

- [ ] **Step 1.2:** Implement `job_definition.py`
  - Copy code from design document
  - Test: Run job validation tests
  
- [ ] **Step 1.3:** Implement `job_registry.py`
  - Copy code from design document
  - Test: Create/read/update/delete operations
  
- [ ] **Step 1.4:** Implement `job_executor.py`
  - Copy code from design document
  - Test: Execute single stock fetch
  
- [ ] **Step 1.5:** Implement `job_scheduler.py`
  - Copy code from design document
  - Test: Start/stop scheduler thread

### Phase 2: Webapp Integration (Day 3)

- [ ] **Step 2.1:** Implement `scheduler_serving_app.py`
  - Copy code from design document
  - Test: Singleton creation
  
- [ ] **Step 2.2:** Implement `scheduler_serving_app_router.py`
  - Copy code from design document
  - Test: API endpoints with Postman/curl
  
- [ ] **Step 2.3:** Update `server.py`
  - Add 2 lines to include router
  - Test: Server starts without errors

### Phase 3: Testing (Day 4-5)

- [ ] **Step 3.1:** Unit tests for job_definition
- [ ] **Step 3.2:** Unit tests for job_registry
- [ ] **Step 3.3:** Unit tests for job_executor
- [ ] **Step 3.4:** Unit tests for job_scheduler
- [ ] **Step 3.5:** Integration tests
- [ ] **Step 3.6:** API endpoint tests

---

## File Creation Order

### 1. Create `src/core/scheduler/__init__.py`

```python
"""
Scheduler module for periodic stock data fetching.
"""

from core.scheduler.job_definition import ScheduledJob, JobStatus
from core.scheduler.job_registry import JobRegistry
from core.scheduler.job_executor import JobExecutor
from core.scheduler.job_scheduler import JobScheduler

__all__ = [
    'ScheduledJob',
    'JobStatus',
    'JobRegistry',
    'JobExecutor',
    'JobScheduler'
]
```

### 2. Create each Python file

Follow the design document for full implementation of:
- `job_definition.py`
- `job_registry.py`
- `job_executor.py`
- `job_scheduler.py`
- `scheduler_serving_app.py`
- `scheduler_serving_app_router.py`

### 3. Modify `src/server.py`

```python
# ADD THESE TWO LINES:
from webapp.router import scheduler_serving_app_router
app.include_router(scheduler_serving_app_router.router)
```

---

## Testing Commands

### Start Redis (if not running)
```bash
docker run -d -p 6379:6379 redis:7
# or
redis-server
```

### Start the Server
```bash
cd /Users/pwang/Developer/stock-analyzer-backend
python src/run_server.py
```

### Test API Endpoints

#### 1. Create a Job
```bash
curl -X POST "http://localhost:8001/scheduler/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Daily FAANG Stocks",
    "stock_ids": ["META", "AAPL", "AMZN", "NFLX", "GOOGL"],
    "schedule_time": "17:00"
  }'
```

Expected response:
```json
{
  "message": "Job created successfully",
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### 2. List All Jobs
```bash
curl -X GET "http://localhost:8001/scheduler/jobs"
```

#### 3. Get Job Details
```bash
curl -X GET "http://localhost:8001/scheduler/jobs/{job_id}"
```

#### 4. Update Job
```bash
curl -X PUT "http://localhost:8001/scheduler/jobs/{job_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "schedule_time": "18:00",
    "stock_ids": ["AAPL", "MSFT", "GOOGL"]
  }'
```

#### 5. Stop Job
```bash
curl -X POST "http://localhost:8001/scheduler/jobs/{job_id}/stop"
```

#### 6. Start Job
```bash
curl -X POST "http://localhost:8001/scheduler/jobs/{job_id}/start"
```

#### 7. Delete Job
```bash
curl -X DELETE "http://localhost:8001/scheduler/jobs/{job_id}"
```

#### 8. Get Scheduler Status
```bash
curl -X GET "http://localhost:8001/scheduler/status"
```

---

## Verification Steps

### 1. Verify Scheduler Thread is Running
```bash
# Check logs - should see:
# "Job scheduler started"
# "Scheduler loop started"
```

### 2. Verify Job Storage in Redis
```bash
redis-cli

# List all scheduler keys
KEYS scheduler:*

# Get job data
GET scheduler:job:{job_id}

# Get job index
GET scheduler:job_index
```

### 3. Verify Data Fetching
```bash
redis-cli

# After a job runs, check for stock data
KEYS scheduled_stock_data:*

# Get stock data
GET scheduled_stock_data:AAPL:2025-09-21:2025-10-21
```

### 4. Monitor Logs
```python
# Add to run_server.py for detailed logging:
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

## Troubleshooting

### Issue: Scheduler not starting

**Check:**
```python
# In scheduler_serving_app.py, verify:
def _initialize(self):
    # ...
    self.scheduler.start()  # This line must be present
    logger.info("Scheduler started")
```

### Issue: Jobs not executing

**Check:**
1. Is job active? `is_active: true`
2. Is time correct? Check `next_run` value
3. Is scheduler running? Check `GET /scheduler/status`
4. Check logs for errors

### Issue: Stock data not saving

**Check:**
1. Redis connection working?
   ```bash
   redis-cli ping
   # Should return: PONG
   ```
2. Check DataIOButler is initialized correctly
3. Check stock_id is valid
4. Check date range is valid

### Issue: Module import errors

**Check:**
```bash
# Make sure you're in the right directory
cd /Users/pwang/Developer/stock-analyzer-backend

# Run with PYTHONPATH set
PYTHONPATH=/Users/pwang/Developer/stock-analyzer-backend python src/run_server.py
```

---

## Testing Schedule

### Manual Test: Force Immediate Execution

For testing, temporarily modify schedule check:

```python
# In job_scheduler.py, _check_and_execute_jobs():
# Temporarily change to run immediately for testing:
if True:  # Always true for testing
    self._execute_job_async(job)
```

Then change back after testing:
```python
if current_time >= job.next_run:
    self._execute_job_async(job)
```

### Manual Test: Set Short Check Interval

```python
# In scheduler_serving_app.py:
self.scheduler = JobScheduler(
    registry=self.registry,
    executor=self.executor,
    check_interval=10  # Check every 10 seconds for testing
)
```

---

## Sample Test Scenario

### Complete End-to-End Test

```bash
# 1. Start server
python src/run_server.py

# 2. Create a job (in another terminal)
JOB_ID=$(curl -s -X POST "http://localhost:8001/scheduler/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Job",
    "stock_ids": ["AAPL", "MSFT"],
    "schedule_time": "17:00"
  }' | jq -r '.job_id')

echo "Created job: $JOB_ID"

# 3. Verify job created
curl "http://localhost:8001/scheduler/jobs/$JOB_ID" | jq

# 4. Check scheduler status
curl "http://localhost:8001/scheduler/status" | jq

# 5. Wait for scheduled time or force execution (modify code)

# 6. Verify data was fetched
redis-cli KEYS "scheduled_stock_data:*"

# 7. Get fetched data
redis-cli GET "scheduled_stock_data:AAPL:*" | jq

# 8. Check job was updated
curl "http://localhost:8001/scheduler/jobs/$JOB_ID" | jq '.last_run'

# 9. Stop job
curl -X POST "http://localhost:8001/scheduler/jobs/$JOB_ID/stop"

# 10. Cleanup
curl -X DELETE "http://localhost:8001/scheduler/jobs/$JOB_ID"
```

---

## Performance Considerations

### Recommended Settings

```python
# For production:
JobScheduler(
    check_interval=60  # Check every minute
)

# For development/testing:
JobScheduler(
    check_interval=10  # Check every 10 seconds
)
```

### Concurrent Job Execution

Jobs execute in separate threads, so multiple jobs can run simultaneously. To limit:

```python
# Add to JobScheduler if needed:
self._max_concurrent_jobs = 3
self._active_job_count = 0
```

---

## Monitoring Dashboard (Optional Enhancement)

### Add Status Endpoint

```python
@router.get("/scheduler/dashboard")
def get_dashboard(app = Depends(get_scheduler_app)):
    jobs = app.list_jobs()
    return {
        "scheduler_status": app.get_scheduler_status(),
        "jobs": jobs,
        "summary": {
            "total": len(jobs),
            "active": len([j for j in jobs if j['is_active']]),
            "completed_today": len([
                j for j in jobs 
                if j['last_run'] and 
                j['last_run'].startswith(datetime.now().date().isoformat())
            ])
        }
    }
```

---

## Next Steps After Implementation

1. **Add Job History Tracking**
   - Store execution results
   - Track success/failure rates
   
2. **Add Email Notifications**
   - Alert on job failures
   - Daily summary emails

3. **Add Job Dependencies**
   - Run analysis after data fetch
   - Chain multiple jobs

4. **Add Web UI**
   - Visual job management
   - Real-time status monitoring

5. **Add Advanced Scheduling**
   - Cron expression support
   - Weekly schedules
   - Multiple times per day

---

## Support and Questions

If you encounter issues during implementation:

1. Check the design document for full code
2. Review the architecture diagrams
3. Verify existing components are working
4. Test each component in isolation
5. Use logging extensively

---

**Document Version:** 1.0  
**Last Updated:** October 2025  
**Status:** Ready for Use

