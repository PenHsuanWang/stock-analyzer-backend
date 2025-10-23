"""
Test script for metadata feature implementation.
Tests all acceptance criteria from UX_BACKEND_REQUIREMENTS.md
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import json
import pandas as pd
from datetime import datetime, timezone, timedelta

from core.services.metadata_service import MetadataService
from core.manager.data_manager import DataIOButler
from utils.database_adapters.redis_adapter import RedisAdapter


def test_metadata_service():
    """Test MetadataService functionality"""
    print("\n" + "="*60)
    print("TEST 1: Metadata Service")
    print("="*60)
    
    # Test default metadata creation
    print("\n✓ Testing default metadata creation...")
    metadata = MetadataService.create_default_metadata()
    assert metadata["source_type"] == "manual_fetch"
    assert metadata["job_id"] is None
    assert metadata["created_by"] == "user"
    assert "created_at" in metadata
    print("  ✅ AC1.3: Default metadata created successfully")
    
    # Test job metadata creation
    print("\n✓ Testing job metadata creation...")
    job_metadata = MetadataService.create_job_metadata(
        job_id="test-job-123",
        job_name="Test Job",
        schedule_time="09:00",
        next_update=datetime.now(timezone.utc).isoformat()
    )
    assert job_metadata["source_type"] == "scheduled_job"
    assert job_metadata["job_id"] == "test-job-123"
    assert job_metadata["job_name"] == "Test Job"
    assert "scheduled" in job_metadata["tags"]
    assert "auto-updating" in job_metadata["tags"]
    print("  ✅ AC2.1-2.4: Job metadata created correctly")
    
    # Test next run time calculation
    print("\n✓ Testing next run time calculation...")
    next_run = MetadataService.calculate_next_run_time("23:59")
    assert next_run is not None
    next_run_dt = datetime.fromisoformat(next_run)
    assert next_run_dt.hour == 23
    assert next_run_dt.minute == 59
    print("  ✅ AC2.3: Next run time calculated correctly")
    
    # Test backward compatibility
    print("\n✓ Testing backward compatibility...")
    old_data = [{"Date": "2025-01-01", "Close": 150.0}]
    result = MetadataService.extract_data_and_metadata(old_data)
    assert "data" in result
    assert "metadata" in result
    assert result["metadata"]["source_type"] == "unknown"
    print("  ✅ AC1.2: Backward compatibility works")
    
    print("\n✅ Metadata Service: ALL TESTS PASSED")


def test_data_storage_with_metadata():
    """Test data storage with metadata"""
    print("\n" + "="*60)
    print("TEST 2: Data Storage with Metadata")
    print("="*60)
    
    adapter = RedisAdapter()
    butler = DataIOButler(adapter=adapter)
    
    # Test saving data with metadata
    print("\n✓ Testing save data with metadata...")
    test_data = pd.DataFrame([
        {"Date": "2025-01-01", "Close": 150.0, "Volume": 1000000},
        {"Date": "2025-01-02", "Close": 151.0, "Volume": 1100000}
    ])
    
    metadata = MetadataService.create_job_metadata(
        job_id="test-save-123",
        job_name="Test Save Job",
        schedule_time="10:00"
    )
    
    butler.save_data(
        data=test_data,
        prefix="test_metadata",
        stock_id="TEST1",
        start_date="2025-01-01",
        end_date="2025-01-02",
        metadata=metadata
    )
    print("  ✅ AC1.1: Data saved with metadata")
    
    # Test retrieving data with metadata
    print("\n✓ Testing get data with metadata...")
    result = butler.get_data_with_metadata(
        prefix="test_metadata",
        stock_id="TEST1",
        start_date="2025-01-01",
        end_date="2025-01-02"
    )
    
    assert "data" in result
    assert "metadata" in result
    assert isinstance(result["data"], pd.DataFrame)
    assert result["metadata"]["job_id"] == "test-save-123"
    assert result["metadata"]["source_type"] == "scheduled_job"
    print("  ✅ AC1.1: Data retrieved with metadata")
    
    # Test backward compatibility - save without metadata
    print("\n✓ Testing save without metadata...")
    butler.save_data(
        data=test_data,
        prefix="test_metadata",
        stock_id="TEST2",
        start_date="2025-01-01",
        end_date="2025-01-02"
    )
    
    result2 = butler.get_data_with_metadata(
        prefix="test_metadata",
        stock_id="TEST2",
        start_date="2025-01-01",
        end_date="2025-01-02"
    )
    assert result2["metadata"]["source_type"] == "unknown"
    print("  ✅ AC1.3: Default metadata applied when not provided")
    
    # Clean up
    butler.delete_data(prefix="test_metadata", stock_id="TEST1", start_date="2025-01-01", end_date="2025-01-02")
    butler.delete_data(prefix="test_metadata", stock_id="TEST2", start_date="2025-01-01", end_date="2025-01-02")
    
    print("\n✅ Data Storage: ALL TESTS PASSED")


def test_list_datasets():
    """Test list datasets functionality"""
    print("\n" + "="*60)
    print("TEST 3: List Datasets")
    print("="*60)
    
    adapter = RedisAdapter()
    butler = DataIOButler(adapter=adapter)
    
    # Create test datasets
    print("\n✓ Creating test datasets...")
    test_data = pd.DataFrame([{"Date": "2025-01-01", "Close": 100.0}])
    
    # Dataset 1: Scheduled job
    butler.save_data(
        data=test_data,
        prefix="test_list",
        stock_id="AAPL",
        start_date="2025-01-01",
        end_date="2025-01-31",
        metadata=MetadataService.create_job_metadata(
            job_id="morning-job",
            job_name="Morning Job",
            schedule_time="09:00"
        )
    )
    
    # Dataset 2: Manual fetch
    butler.save_data(
        data=test_data,
        prefix="test_list",
        stock_id="MSFT",
        start_date="2025-01-01",
        end_date="2025-01-31",
        metadata=MetadataService.create_default_metadata("manual_fetch")
    )
    
    # Test listing all datasets
    print("\n✓ Testing list all datasets...")
    datasets = butler.list_all_datasets("test_list:*")
    assert len(datasets) >= 2
    print(f"  Found {len(datasets)} datasets")
    print("  ✅ AC4.1: List all datasets works")
    
    # Verify structure
    for ds in datasets:
        assert "key" in ds
        assert "stock_id" in ds
        assert "start_date" in ds
        assert "end_date" in ds
        assert "record_count" in ds
        assert "metadata" in ds
        print(f"  Dataset: {ds['stock_id']} - Source: {ds['metadata']['source_type']}")
    
    # Clean up
    butler.delete_data(prefix="test_list", stock_id="AAPL", start_date="2025-01-01", end_date="2025-01-31")
    butler.delete_data(prefix="test_list", stock_id="MSFT", start_date="2025-01-01", end_date="2025-01-31")
    
    print("\n✅ List Datasets: ALL TESTS PASSED")


def test_metadata_schema():
    """Test metadata schema validation"""
    print("\n" + "="*60)
    print("TEST 4: Metadata Schema Validation")
    print("="*60)
    
    print("\n✓ Testing metadata schema completeness...")
    metadata = MetadataService.create_default_metadata()
    
    required_fields = [
        "source_type", "job_id", "job_name", "created_by",
        "created_at", "updated_at", "schedule_time",
        "is_recurring", "next_update", "tags", "description"
    ]
    
    for field in required_fields:
        assert field in metadata, f"Missing required field: {field}"
        print(f"  ✓ Field '{field}' present")
    
    print("  ✅ AC1.4: All metadata fields present")
    
    # Test data types
    print("\n✓ Testing metadata data types...")
    assert isinstance(metadata["source_type"], str)
    assert isinstance(metadata["is_recurring"], bool)
    assert isinstance(metadata["tags"], list)
    print("  ✅ AC1.5: Data types correct")
    
    # Test ISO 8601 format
    print("\n✓ Testing timestamp format...")
    created_at = metadata["created_at"]
    datetime.fromisoformat(created_at)  # Will raise if not valid ISO 8601
    print("  ✅ AC1.6: ISO 8601 format validated")
    
    print("\n✅ Metadata Schema: ALL TESTS PASSED")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print(" METADATA FEATURE TEST SUITE")
    print(" Testing UX Backend Requirements Implementation")
    print("="*70)
    
    try:
        test_metadata_service()
        test_data_storage_with_metadata()
        test_list_datasets()
        test_metadata_schema()
        
        print("\n" + "="*70)
        print(" 🎉 ALL TESTS PASSED! 🎉")
        print("="*70)
        print("\n✅ Summary:")
        print("  - Metadata Service: PASSED")
        print("  - Data Storage with Metadata: PASSED")
        print("  - List Datasets: PASSED")
        print("  - Metadata Schema: PASSED")
        print("\n✅ Acceptance Criteria Met:")
        print("  AC1.1: New data saved includes both data and metadata ✓")
        print("  AC1.2: Old data without metadata can be read ✓")
        print("  AC1.3: Default metadata created when not provided ✓")
        print("  AC1.4: All metadata fields follow defined schema ✓")
        print("  AC1.5: Metadata fields have correct data types ✓")
        print("  AC1.6: ISO 8601 timestamps are used ✓")
        print("  AC2.1-2.4: Job metadata creation works correctly ✓")
        print("  AC4.1: List datasets returns all datasets ✓")
        print("="*70)
        return 0
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
