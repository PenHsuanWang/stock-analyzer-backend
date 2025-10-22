# Sliding Window Duration Feature - Implementation Summary

## Overview

Added support for a **sliding time window** feature to scheduled jobs, allowing users to specify a `duration_days` parameter that creates a dynamic date range that updates on each job execution.

**Feature**: Fetch stock data for the last N days (e.g., 60 days) where the window slides forward each day automatically.

## Changes Made

### 1. Core Data Model (`src/core/scheduler/job_definition.py`)

**Added**:
- New field: `duration_days: Optional[int] = None`
- Validation: Ensures `duration_days` is a positive integer
- Documentation: Updated docstring to include the new parameter

**Modified Methods**:
- `validate()`: Added validation for `duration_days > 0`
- `to_dict()`: Includes `duration_days` in serialization
- `from_dict()`: Restores `duration_days` from storage

### 2. Job Executor (`src/core/scheduler/job_executor.py`)

**Added**:
- New method: `_calculate_sliding_start_date(duration_days: int)` 
  - Calculates start_date as `today - duration_days`
  - Returns date in ISO format (YYYY-MM-DD)

**Modified Methods**:
- `execute_job()`: 
  - Checks if `duration_days` is set
  - If set, uses sliding window calculation instead of fixed `start_date`
  - Logs when sliding window is being used
  - Priority: `duration_days` > `start_date` > default (30 days)

### 3. API Router (`src/webapp/router/scheduler_serving_app_router.py`)

**Modified Models**:
- `CreateJobRequest`:
  - Added `duration_days: Optional[int] = None`
  - Added validator to ensure positive integer
  - Updated docstring to explain sliding window behavior

- `UpdateJobRequest`:
  - Added `duration_days: Optional[int] = None`

**Modified Endpoints**:
- `POST /scheduler/jobs`: Accepts `duration_days` parameter
- `PUT /scheduler/jobs/{job_id}`: Supports updating `duration_days`

### 4. Serving App (`src/webapp/serving_app/scheduler_serving_app.py`)

**Modified Methods**:
- `create_job()`: 
  - Accepts `duration_days` parameter
  - Passes it to `ScheduledJob` constructor

- `update_job()`:
  - Accepts `duration_days` parameter
  - Updates job's `duration_days` field when provided

## File Changes Summary

| File | Lines Changed | Type |
|------|--------------|------|
| `src/core/scheduler/job_definition.py` | ~10 | Modified |
| `src/core/scheduler/job_executor.py` | ~25 | Modified |
| `src/webapp/router/scheduler_serving_app_router.py` | ~15 | Modified |
| `src/webapp/serving_app/scheduler_serving_app.py` | ~10 | Modified |
| `SLIDING_WINDOW_FEATURE.md` | New | Documentation |
| `examples/sliding_window_usage.py` | New | Examples |
| `test_sliding_window.py` | New | Test |

**Total**: 4 files modified, 3 files created

## Key Features

1. **Sliding Window**: `duration_days` parameter creates a dynamic time window
2. **Automatic Updates**: Window slides forward automatically on each execution
3. **Priority Logic**: `duration_days` takes precedence over `start_date`
4. **Validation**: Ensures only positive integers are accepted
5. **Backward Compatible**: Existing jobs continue to work unchanged
6. **Flexible**: Supports any duration (7 days, 30 days, 60 days, 365 days, etc.)

## Usage Examples

### Create Job with 60-Day Sliding Window
```bash
curl -X POST "http://localhost:8000/scheduler/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "60-Day Rolling Window",
    "stock_ids": ["AAPL", "GOOGL"],
    "schedule_time": "17:00",
    "duration_days": 60
  }'
```

### Update Job to Use Sliding Window
```bash
curl -X PUT "http://localhost:8000/scheduler/jobs/{job_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "duration_days": 90
  }'
```

## Behavior

### Without duration_days (Traditional)
- Uses fixed `start_date` and `end_date`
- Fetches same date range on every execution
- Requires manual updates for new periods

### With duration_days (New Feature)
- Calculates `start_date = today - duration_days`
- Uses `end_date = today` (or specified value)
- Automatically updates window on each execution

**Example**: `duration_days: 60`
- Oct 23, 2025: Fetches Aug 24 to Oct 23 (60 days)
- Oct 24, 2025: Fetches Aug 25 to Oct 24 (60 days)
- Oct 25, 2025: Fetches Aug 26 to Oct 25 (60 days)
- And so on...

## Testing

All tests pass successfully:

```bash
PYTHONPATH=src python test_sliding_window.py
```

**Tests cover**:
- ✓ Field storage and retrieval
- ✓ Sliding window calculation
- ✓ Input validation (positive integers only)
- ✓ Priority logic (duration_days vs start_date)
- ✓ Serialization/deserialization

## Documentation

Created comprehensive documentation:
- `SLIDING_WINDOW_FEATURE.md`: Complete feature guide with examples
- `examples/sliding_window_usage.py`: Executable examples
- `test_sliding_window.py`: Validation tests

## Backward Compatibility

✓ **Fully backward compatible**
- Existing jobs without `duration_days` continue to work
- `duration_days` is optional
- Default behavior unchanged
- No breaking changes to API

## Migration Path

To convert existing fixed-date jobs to sliding window:

1. Calculate days between current start_date and end_date
2. Set `duration_days` to that value
3. Remove `start_date` (optional, will be ignored anyway)

Example:
```json
// Before
{
  "start_date": "2025-08-24",
  "end_date": "2025-10-23"
}

// After (53 days)
{
  "duration_days": 53
}
```

## Benefits

1. **Automated Maintenance**: No need to update date ranges manually
2. **Always Current**: Automatically fetches most recent data
3. **Consistent Windows**: Always compares equivalent time periods
4. **Flexible Analysis**: Easy to adjust window size (weekly, monthly, quarterly, annual)
5. **Perfect for Indicators**: Ideal for moving averages and trend analysis

## Future Enhancements

Potential improvements:
- Business days only mode (exclude weekends/holidays)
- Named window types ("last_week", "last_month", "last_quarter")
- Multiple windows per job
- Window offsets (e.g., 60 days ending 30 days ago)

## Verification

Run these commands to verify the implementation:

```bash
# Test the feature
PYTHONPATH=src python test_sliding_window.py

# View examples
python examples/sliding_window_usage.py

# Check imports
PYTHONPATH=src python -c "from core.scheduler.job_definition import ScheduledJob; print('✓ OK')"
```

## Notes

- **Current Date**: 2025-10-23
- **Implementation Date**: 2025-10-22
- **Status**: Complete and tested
- **Breaking Changes**: None
- **Database Migration**: Not required (optional field)

## Questions?

For more information:
- Feature documentation: `SLIDING_WINDOW_FEATURE.md`
- Usage examples: `examples/sliding_window_usage.py`
- Implementation tests: `test_sliding_window.py`
