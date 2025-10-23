"""
Metadata service for managing dataset metadata.
Handles creation, retrieval, and management of metadata for stock data.
"""
import json
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any, List


class MetadataService:
    """Service for creating and managing metadata for datasets."""
    
    @staticmethod
    def create_default_metadata(source_type: str = "manual_fetch") -> Dict[str, Any]:
        """
        Create default metadata for manual fetches or unknown sources.
        
        Args:
            source_type: Type of source ('manual_fetch', 'unknown', etc.)
            
        Returns:
            Dictionary containing default metadata
        """
        now = datetime.now(timezone.utc)
        
        return {
            "source_type": source_type,
            "job_id": None,
            "job_name": None,
            "created_by": "user" if source_type == "manual_fetch" else "unknown",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "schedule_time": None,
            "is_recurring": False,
            "next_update": None,
            "tags": [],
            "description": ""
        }
    
    @staticmethod
    def create_job_metadata(
        job_id: str,
        job_name: str,
        schedule_time: str,
        next_update: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create metadata for data fetched by a scheduled job.
        
        Args:
            job_id: Unique identifier of the job
            job_name: Human-readable name of the job
            schedule_time: Time when the job runs (HH:MM format)
            next_update: ISO 8601 timestamp for next scheduled run
            
        Returns:
            Dictionary containing job metadata
        """
        now = datetime.now(timezone.utc)
        
        return {
            "source_type": "scheduled_job",
            "job_id": job_id,
            "job_name": job_name,
            "created_by": "job_scheduler",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "schedule_time": schedule_time,
            "is_recurring": True,
            "next_update": next_update,
            "tags": ["scheduled", "auto-updating"],
            "description": f"Data from scheduled job '{job_name}' at {schedule_time}"
        }
    
    @staticmethod
    def calculate_next_run_time(schedule_time: str) -> Optional[str]:
        """
        Calculate next run time based on schedule.
        
        Args:
            schedule_time: Schedule time in HH:MM format
            
        Returns:
            ISO 8601 timestamp for next run, or None on error
        """
        try:
            now = datetime.now(timezone.utc)
            hour, minute = map(int, schedule_time.split(':'))
            
            # Calculate today's run time
            today_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # If already passed, schedule for tomorrow
            if now >= today_run:
                next_run = today_run + timedelta(days=1)
            else:
                next_run = today_run
                
            return next_run.isoformat()
        except Exception:
            return None
    
    @staticmethod
    def wrap_data_with_metadata(
        data: Any,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Wrap data with metadata structure.
        
        Args:
            data: The actual data to wrap
            metadata: Optional metadata dictionary
            
        Returns:
            Dictionary with 'data' and 'metadata' keys
        """
        if metadata is None:
            metadata = MetadataService.create_default_metadata()
            
        return {
            "data": data,
            "metadata": metadata
        }
    
    @staticmethod
    def extract_data_and_metadata(
        stored_value: Any
    ) -> Dict[str, Any]:
        """
        Extract data and metadata from stored value.
        Handles both old format (raw data) and new format (with metadata).
        
        Args:
            stored_value: Value retrieved from storage
            
        Returns:
            Dictionary with 'data' and 'metadata' keys
        """
        # Handle None
        if stored_value is None:
            return None
            
        # If it's a string, try to parse as JSON
        if isinstance(stored_value, str):
            try:
                stored_value = json.loads(stored_value)
            except json.JSONDecodeError:
                # Not JSON, treat as raw data
                return {
                    "data": stored_value,
                    "metadata": MetadataService.create_default_metadata("unknown")
                }
        
        # Handle old format (list/array without metadata)
        if isinstance(stored_value, list):
            return {
                "data": stored_value,
                "metadata": MetadataService.create_default_metadata("unknown")
            }
        
        # Handle new format (dict with data and metadata)
        if isinstance(stored_value, dict):
            if "data" in stored_value and "metadata" in stored_value:
                return stored_value
            else:
                # Dict without metadata structure, treat as raw data
                return {
                    "data": stored_value,
                    "metadata": MetadataService.create_default_metadata("unknown")
                }
        
        # Unknown format
        return {
            "data": stored_value,
            "metadata": MetadataService.create_default_metadata("unknown")
        }
    
    @staticmethod
    def update_metadata_field(
        metadata: Dict[str, Any],
        field: str,
        value: Any
    ) -> Dict[str, Any]:
        """
        Update a specific field in metadata.
        
        Args:
            metadata: Existing metadata dictionary
            field: Field name to update
            value: New value for the field
            
        Returns:
            Updated metadata dictionary
        """
        metadata[field] = value
        metadata["updated_at"] = datetime.now(timezone.utc).isoformat()
        return metadata
