# Sliding Time Window Feature for Scheduled Jobs

## Overview

The scheduler now supports a **sliding time window** feature that allows you to fetch stock data for a dynamic date range that updates on each job execution. Instead of using fixed `start_date` and `end_date`, you can specify a `duration_days` parameter to fetch data from the last N days.

## Feature Details

### New Parameter: `duration_days`

- **Type**: Optional integer
- **Description**: Number of days to fetch from today (sliding window)
- **Validation**: Must be a positive integer (> 0)
- **Priority**: When set, `duration_days` takes priority over `start_date`

### How It Works

When you set `duration_days`, the job will:
1. Calculate `start_date` = today - `duration_days`
2. Calculate `end_date` = today (or the specified `end_date`)
3. Fetch stock data for this dynamic range on each execution

This creates a **sliding window** that always fetches the most recent N days of data.

### Example Use Cases

#### Example 1: Fetch Last 60 Days Daily

```json
{
  "name": "Daily 60-Day Window",
  "stock_ids": ["AAPL", "GOOGL", "MSFT"],
  "schedule_time": "17:00",
  "duration_days": 60
}
```

**Behavior**:
- On 2025-10-23: Fetches data from 2025-08-24 to 2025-10-23
- On 2025-10-24: Fetches data from 2025-08-25 to 2025-10-24
- And so on...

#### Example 2: Fetch Last 30 Days at Market Close

```json
{
  "name": "Monthly Rolling Window",
  "stock_ids": ["TSLA", "AMZN"],
  "schedule_time": "16:30",
  "duration_days": 30,
  "prefix": "rolling_30d_data"
}
```

**Behavior**:
- Always maintains the most recent 30 days of data
- Updates daily at 4:30 PM

#### Example 3: Fetch Last 90 Days for Quarterly Analysis

```json
{
  "name": "Quarterly Rolling Window",
  "stock_ids": ["SPY", "QQQ", "DIA"],
  "schedule_time": "18:00",
  "duration_days": 90
}
```

**Behavior**:
- Maintains a rolling 90-day (approximately 3 months) window
- Useful for quarterly trend analysis

## API Usage

### Creating a Job with Sliding Window

**Endpoint**: `POST /scheduler/jobs`

```bash
curl -X POST "http://localhost:8000/scheduler/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "60-Day Sliding Window",
    "stock_ids": ["AAPL", "GOOGL"],
    "schedule_time": "17:00",
    "duration_days": 60
  }'
```

### Updating a Job to Use Sliding Window

**Endpoint**: `PUT /scheduler/jobs/{job_id}`

```bash
curl -X PUT "http://localhost:8000/scheduler/jobs/{job_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "duration_days": 90
  }'
```

### Response Format

The job response includes the `duration_days` field:

```json
{
  "job_id": "abc-123-def",
  "name": "60-Day Sliding Window",
  "stock_ids": ["AAPL", "GOOGL"],
  "schedule_time": "17:00",
  "duration_days": 60,
  "is_active": true,
  "status": "pending",
  "created_at": "2025-10-23T10:00:00",
  "last_run": null,
  "next_run": "2025-10-23T17:00:00"
}
```

## Comparison: Fixed Dates vs. Sliding Window

### Fixed Date Range (Old Method)

```json
{
  "start_date": "2025-01-01",
  "end_date": "2025-03-31"
}
```

- **Static**: Always fetches data from Jan 1 to Mar 31, 2025
- **Manual Updates**: Need to update dates manually for new periods
- **Use Case**: Historical analysis of specific periods

### Sliding Window (New Method)

```json
{
  "duration_days": 90
}
```

- **Dynamic**: Always fetches the last 90 days
- **Automatic**: Updates automatically on each run
- **Use Case**: Real-time analysis, trend tracking, moving averages

## Priority Rules

1. If `duration_days` is set, it **takes priority** over `start_date`
2. The `end_date` is always used if specified, otherwise defaults to today
3. You can have both `start_date` and `duration_days` in the job definition, but `duration_days` will be used during execution

## Implementation Details

### Code Changes

1. **Job Definition** (`job_definition.py`):
   - Added `duration_days: Optional[int]` field
   - Added validation for positive integer values
   - Updated `to_dict()` and `from_dict()` methods

2. **Job Executor** (`job_executor.py`):
   - Added `_calculate_sliding_start_date()` method
   - Updated `execute_job()` to check and use `duration_days`
   - Logs indicate when sliding window is being used

3. **API Router** (`scheduler_serving_app_router.py`):
   - Added `duration_days` to `CreateJobRequest`
   - Added `duration_days` to `UpdateJobRequest`
   - Added validation for positive integer values

4. **Serving App** (`scheduler_serving_app.py`):
   - Updated `create_job()` to accept `duration_days`
   - Updated `update_job()` to handle `duration_days`

## Benefits

1. **Always Fresh Data**: Automatically maintains the most recent N days
2. **No Manual Updates**: Set once, runs indefinitely with current data
3. **Flexible Analysis**: Easily adjust window size (30, 60, 90 days, etc.)
4. **Moving Windows**: Perfect for technical indicators like moving averages
5. **Trend Tracking**: Consistently compare equivalent time periods

## Migration Guide

### Converting Existing Jobs

If you have an existing job with fixed dates and want to convert to sliding window:

**Before**:
```json
{
  "start_date": "2025-09-01",
  "end_date": "2025-10-23"
}
```

**After** (53-day window):
```json
{
  "duration_days": 53
}
```

Simply calculate the number of days between your dates and use that as `duration_days`.

## Validation and Error Handling

### Valid Values

- Any positive integer: `1, 30, 60, 90, 365, etc.`
- Common use cases: 7 (week), 30 (month), 60 (2 months), 90 (quarter), 365 (year)

### Invalid Values

- Zero: `"duration_days": 0` → **Error**: "duration_days must be a positive integer"
- Negative: `"duration_days": -10` → **Error**: "duration_days must be a positive integer"
- Non-integer: `"duration_days": "30"` → **Error**: Pydantic validation error

## Logging

When a job with `duration_days` executes, you'll see log messages like:

```
INFO: Using sliding window: 60 days (from 2025-08-24 to 2025-10-23)
INFO: Successfully fetched and stored data for AAPL
INFO: Successfully fetched and stored data for GOOGL
```

## Testing

Run the included test script to verify the feature:

```bash
cd /Users/pwang/Developer/stock-analyzer-backend
PYTHONPATH=src python test_sliding_window.py
```

This validates:
- Field storage and retrieval
- Sliding window calculation
- Input validation
- Priority logic

## Future Enhancements

Potential future improvements:
- Support for business days only (exclude weekends/holidays)
- Custom window types (e.g., "last_month", "last_quarter")
- Multiple window sizes per job
- Window offset (e.g., fetch 60 days starting from 30 days ago)

## Questions & Support

For issues or questions about this feature, please refer to:
- Main scheduler documentation: `SCHEDULER_MODULE_DESIGN.md`
- Implementation guide: `SCHEDULER_IMPLEMENTATION_GUIDE.md`
- Frontend integration: `SCHEDULER_FRONTEND_DESIGN.md`
