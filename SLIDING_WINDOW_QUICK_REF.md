# Quick Reference: Sliding Window Feature

## Overview
Add `duration_days` to scheduled jobs to create a sliding time window that automatically fetches the last N days of stock data.

## API Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `duration_days` | int | No | Number of days to fetch from today | `60` |

## How It Works

```
duration_days = 60

Day 1: Fetches [today - 60 days] to [today]
Day 2: Fetches [today - 60 days] to [today]  ← Automatically updates
Day 3: Fetches [today - 60 days] to [today]  ← Automatically updates
```

## Quick Examples

### Create Job
```bash
curl -X POST "http://localhost:8000/scheduler/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Sliding Window Job",
    "stock_ids": ["AAPL", "GOOGL"],
    "schedule_time": "17:00",
    "duration_days": 60
  }'
```

### Update Job
```bash
curl -X PUT "http://localhost:8000/scheduler/jobs/{job_id}" \
  -H "Content-Type: application/json" \
  -d '{"duration_days": 90}'
```

## Common Durations

| Use Case | duration_days | Description |
|----------|--------------|-------------|
| Weekly | 7 | Last 7 days |
| Monthly | 30 | Last 30 days |
| Bi-Monthly | 60 | Last 60 days |
| Quarterly | 90 | Last 90 days |
| Annual | 365 | Last 365 days |

## Priority Rules

1. If `duration_days` is set → Uses sliding window (ignores `start_date`)
2. If `start_date` is set → Uses fixed start date
3. If neither → Defaults to 30 days ago

## Validation

✅ **Valid**: Any positive integer (1, 7, 30, 60, 90, 365, etc.)  
❌ **Invalid**: Zero, negative numbers, non-integers

## Benefits

✓ Always fetches most recent data  
✓ No manual date updates needed  
✓ Perfect for trend analysis  
✓ Ideal for moving averages  
✓ Consistent time windows  

## See Also

- `SLIDING_WINDOW_FEATURE.md` - Full documentation
- `examples/sliding_window_usage.py` - Complete examples
- `SCHEDULER_MODULE_DESIGN.md` - Scheduler design
