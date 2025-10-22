#!/usr/bin/env python3
"""
Example script demonstrating the sliding window feature for scheduled jobs.

This script shows different use cases for the duration_days parameter.
"""

import requests
import json
from datetime import datetime

# Base URL for the scheduler API
BASE_URL = "http://localhost:8000/scheduler"


def create_sliding_window_job():
    """Example: Create a job with a 60-day sliding window."""
    
    print("=" * 70)
    print("Example 1: Create a job with 60-day sliding window")
    print("=" * 70)
    
    job_data = {
        "name": "60-Day Sliding Window - Tech Stocks",
        "stock_ids": ["AAPL", "GOOGL", "MSFT", "AMZN"],
        "schedule_time": "17:00",
        "duration_days": 60,
        "prefix": "tech_stocks_60d"
    }
    
    print("\nRequest:")
    print(json.dumps(job_data, indent=2))
    
    # Uncomment to actually make the request
    # response = requests.post(f"{BASE_URL}/jobs", json=job_data)
    # print("\nResponse:")
    # print(json.dumps(response.json(), indent=2))
    
    print("\nWhat this does:")
    print("• Fetches data for AAPL, GOOGL, MSFT, AMZN")
    print("• Runs daily at 5:00 PM")
    print("• Always fetches the last 60 days of data")
    print("• Example: On 2025-10-23, fetches from 2025-08-24 to 2025-10-23")
    print("• Example: On 2025-10-24, fetches from 2025-08-25 to 2025-10-24")


def create_weekly_window_job():
    """Example: Create a job with a 7-day (weekly) sliding window."""
    
    print("\n" + "=" * 70)
    print("Example 2: Create a job with 7-day sliding window (weekly)")
    print("=" * 70)
    
    job_data = {
        "name": "Weekly Window - Market Indices",
        "stock_ids": ["SPY", "QQQ", "DIA", "IWM"],
        "schedule_time": "09:30",
        "duration_days": 7,
        "prefix": "market_indices_7d"
    }
    
    print("\nRequest:")
    print(json.dumps(job_data, indent=2))
    
    print("\nWhat this does:")
    print("• Fetches data for major market indices")
    print("• Runs daily at 9:30 AM (market open)")
    print("• Always maintains the last 7 days of data")
    print("• Perfect for weekly trend analysis")


def create_quarterly_window_job():
    """Example: Create a job with a 90-day (quarterly) sliding window."""
    
    print("\n" + "=" * 70)
    print("Example 3: Create a job with 90-day sliding window (quarterly)")
    print("=" * 70)
    
    job_data = {
        "name": "Quarterly Window - Growth Stocks",
        "stock_ids": ["TSLA", "NVDA", "AMD", "NFLX"],
        "schedule_time": "16:30",
        "duration_days": 90,
        "prefix": "growth_stocks_90d"
    }
    
    print("\nRequest:")
    print(json.dumps(job_data, indent=2))
    
    print("\nWhat this does:")
    print("• Fetches data for high-growth stocks")
    print("• Runs daily at 4:30 PM (before market close)")
    print("• Always maintains the last 90 days (~3 months)")
    print("• Useful for quarterly performance analysis")


def create_annual_window_job():
    """Example: Create a job with a 365-day (annual) sliding window."""
    
    print("\n" + "=" * 70)
    print("Example 4: Create a job with 365-day sliding window (annual)")
    print("=" * 70)
    
    job_data = {
        "name": "Annual Window - Dividend Stocks",
        "stock_ids": ["KO", "JNJ", "PG", "MCD"],
        "schedule_time": "18:00",
        "duration_days": 365,
        "prefix": "dividend_stocks_365d"
    }
    
    print("\nRequest:")
    print(json.dumps(job_data, indent=2))
    
    print("\nWhat this does:")
    print("• Fetches data for stable dividend stocks")
    print("• Runs daily at 6:00 PM (after market close)")
    print("• Always maintains the last 365 days (1 year)")
    print("• Perfect for year-over-year comparisons")


def update_job_to_sliding_window():
    """Example: Update an existing job to use sliding window."""
    
    print("\n" + "=" * 70)
    print("Example 5: Update existing job to use sliding window")
    print("=" * 70)
    
    job_id = "your-job-id-here"
    
    update_data = {
        "duration_days": 60
    }
    
    print(f"\nRequest to update job {job_id}:")
    print(json.dumps(update_data, indent=2))
    
    # Uncomment to actually make the request
    # response = requests.put(f"{BASE_URL}/jobs/{job_id}", json=update_data)
    # print("\nResponse:")
    # print(json.dumps(response.json(), indent=2))
    
    print("\nWhat this does:")
    print("• Converts an existing job to use a 60-day sliding window")
    print("• All other job settings remain unchanged")
    print("• The job will now always fetch the last 60 days on each run")


def compare_fixed_vs_sliding():
    """Example: Compare fixed dates vs sliding window."""
    
    print("\n" + "=" * 70)
    print("Example 6: Fixed Dates vs Sliding Window Comparison")
    print("=" * 70)
    
    print("\nOption A: Fixed Date Range (Traditional)")
    fixed_job = {
        "name": "Fixed Range Job",
        "stock_ids": ["AAPL"],
        "schedule_time": "17:00",
        "start_date": "2025-08-24",
        "end_date": "2025-10-23"
    }
    print(json.dumps(fixed_job, indent=2))
    print("\n→ Always fetches: 2025-08-24 to 2025-10-23")
    print("→ Needs manual update for new periods")
    
    print("\n" + "-" * 70)
    
    print("\nOption B: Sliding Window (New Feature)")
    sliding_job = {
        "name": "Sliding Window Job",
        "stock_ids": ["AAPL"],
        "schedule_time": "17:00",
        "duration_days": 60
    }
    print(json.dumps(sliding_job, indent=2))
    print("\n→ On 2025-10-23: fetches 2025-08-24 to 2025-10-23")
    print("→ On 2025-10-24: fetches 2025-08-25 to 2025-10-24")
    print("→ Automatically updates every day!")


def curl_examples():
    """Show curl command examples."""
    
    print("\n" + "=" * 70)
    print("Example 7: Using curl commands")
    print("=" * 70)
    
    print("\nCreate a job with 60-day sliding window:")
    print("""
curl -X POST "http://localhost:8000/scheduler/jobs" \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "60-Day Rolling Window",
    "stock_ids": ["AAPL", "GOOGL"],
    "schedule_time": "17:00",
    "duration_days": 60
  }'
    """)
    
    print("\nUpdate a job to use 90-day sliding window:")
    print("""
curl -X PUT "http://localhost:8000/scheduler/jobs/{job_id}" \\
  -H "Content-Type: application/json" \\
  -d '{
    "duration_days": 90
  }'
    """)
    
    print("\nGet job details (includes duration_days):")
    print("""
curl -X GET "http://localhost:8000/scheduler/jobs/{job_id}"
    """)


def main():
    """Run all examples."""
    
    print("\n" + "=" * 70)
    print("SLIDING WINDOW FEATURE - USAGE EXAMPLES")
    print("=" * 70)
    print(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nThese examples demonstrate how to use the duration_days parameter")
    print("to create sliding time windows for stock data fetching.")
    print("\nNote: API calls are commented out. Uncomment to execute.")
    
    create_sliding_window_job()
    create_weekly_window_job()
    create_quarterly_window_job()
    create_annual_window_job()
    update_job_to_sliding_window()
    compare_fixed_vs_sliding()
    curl_examples()
    
    print("\n" + "=" * 70)
    print("ADDITIONAL RESOURCES")
    print("=" * 70)
    print("\nFor more information, see:")
    print("• SLIDING_WINDOW_FEATURE.md - Complete feature documentation")
    print("• SCHEDULER_MODULE_DESIGN.md - Overall scheduler design")
    print("• SCHEDULER_IMPLEMENTATION_GUIDE.md - Implementation details")
    print("\nTo test the feature:")
    print("  PYTHONPATH=src python test_sliding_window.py")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
