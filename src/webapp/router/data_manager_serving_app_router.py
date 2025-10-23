# webapp.data_manager_serving_app_router.py
import pandas as pd
from fastapi import APIRouter, Depends, Body, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime, timezone, timedelta

from webapp.serving_app.data_manager_serving_app import DataManagerApp, get_app

router = APIRouter()


class GetAllKeyWithPrefix(BaseModel):
    prefix: str


class GetDataRequest(BaseModel):
    prefix: str
    stock_id: str
    start_date: str
    end_date: str


class UpdateDataRequest(BaseModel):
    prefix: str
    stock_id: str
    start_date: str
    end_date: str
    updated_dataframe: dict  # a dict representation of the dataframe


class GroupDataRequest(BaseModel):
    group_id: str
    start_date: str
    end_date: str


class SaveGroupDataRequest(GroupDataRequest):
    group_df_list: Optional[List[List[Dict]]] = Field(None, description="List of lists of dataframes in dict format")


class SourceTypeFilter(str, Enum):
    scheduled_job = "scheduled_job"
    manual_fetch = "manual_fetch"
    all = "all"


class ListDatasetsRequest(BaseModel):
    source_type: SourceTypeFilter = SourceTypeFilter.all
    job_id: Optional[str] = None
    stock_ids: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    fresh_only: bool = False


class DatasetSummary(BaseModel):
    key: str
    stock_id: str
    start_date: str
    end_date: str
    record_count: int
    metadata: Dict[str, Any]


class ListDatasetsResponse(BaseModel):
    datasets: List[DatasetSummary]
    total_count: int
    filtered_count: int


class DataWithMetadataResponse(BaseModel):
    data: List[Dict[str, Any]]
    metadata: Dict[str, Any]

@router.post("/stock_data/get_all_keys")
def get_all_data_keys(request: GetAllKeyWithPrefix = Body(...), app: DataManagerApp = Depends(get_app)):
    try:
        keys = app.get_all_data_keys(request.prefix)
        return {"keys": keys}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stock_data/get_data")
def get_stock_data(request: GetDataRequest = Body(...), app: DataManagerApp = Depends(get_app)):
    try:
        # app.get_stock_data will return a pandas dataframe
        data = app.get_stock_data(request.prefix, request.stock_id, request.start_date, request.end_date)
        data = data.round(decimals=4)
        data = data.fillna('null')

        return {"data": data.to_dict(orient="records")}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stock_data/check_data_exists")
def check_data_exists(request: GetDataRequest = Body(...), app: DataManagerApp = Depends(get_app)):
    try:
        exists = app.check_data(request.prefix, request.stock_id, request.start_date, request.end_date)
        return {"exists": exists}
    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stock_data/update_data")
def update_stock_data(request: UpdateDataRequest = Body(...), app: DataManagerApp = Depends(get_app)):
    try:
        updated_data_frame_in_dict = request.updated_dataframe
        df_to_update = pd.DataFrame(updated_data_frame_in_dict)
        app.update_stock_data(request.prefix, request.stock_id, request.start_date, request.end_date, df_to_update)
        return {"updated": "Data updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stock_data/delete_data")
def delete_stock_data(request: GetDataRequest = Body(...), app: DataManagerApp = Depends(get_app)):
    try:
        success = app.delete_stock_data(request.prefix, request.stock_id, request.start_date, request.end_date)
        if success:
            return {"message": "Data deleted successfully."}
        else:
            return {"message": "Failed to delete the data."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/group_data/save")
def save_dataframes_group(request: SaveGroupDataRequest = Body(...), app: DataManagerApp = Depends(get_app)):
    try:
        # convert list of dataframes to pandas DataFrame
        group_df_list = [pd.DataFrame(df_dict) for df_dict in request.group_df_list] if request.group_df_list else []

        success = app.save_dataframes_group(
            group_id=request.group_id,
            start_date=request.start_date,
            end_date=request.end_date,
            group_df_list=group_df_list
        )
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/group_data/get")
def get_dataframes_group(group_id: str, start_date: str, end_date: str, app: DataManagerApp = Depends(get_app)):
    try:
        dataframes_group = app.get_dataframes_group(
            group_id=group_id,
            start_date=start_date,
            end_date=end_date
        )
        return {"dataframes_group": dataframes_group}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/group_data/delete")
def delete_dataframes_group(group_id: str, start_date: str, end_date: str, app: DataManagerApp = Depends(get_app)):
    try:
        success = app.delete_dataframes_group(
            group_id=group_id,
            start_date=start_date,
            end_date=end_date
        )
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stock_data/get_data_with_metadata", response_model=DataWithMetadataResponse)
def get_data_with_metadata(request: GetDataRequest = Body(...), app: DataManagerApp = Depends(get_app)):
    """
    Get stock data with metadata.
    
    Returns both the data array and metadata object.
    Handles backward compatibility with old data format.
    """
    try:
        result = app.get_stock_data_with_metadata(
            prefix=request.prefix,
            stock_id=request.stock_id,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        # Convert DataFrame to dict for response
        data_df = result["data"]
        data_df = data_df.round(decimals=4)
        data_df = data_df.fillna('null')
        
        return {
            "data": data_df.to_dict(orient="records"),
            "metadata": result["metadata"]
        }
    
    except Exception as e:
        error_msg = str(e).lower()
        if "not found" in error_msg or "no data" in error_msg:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for {request.stock_id} from {request.start_date} to {request.end_date}"
            )
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stock_data/list_datasets", response_model=ListDatasetsResponse)
def list_datasets(request: ListDatasetsRequest = Body(...), app: DataManagerApp = Depends(get_app)):
    """
    List all datasets with optional filtering.
    
    Filters:
    - source_type: scheduled_job, manual_fetch, or all
    - job_id: specific job ID
    - stock_ids: list of stock symbols
    - tags: list of tags (AND logic)
    - fresh_only: only data updated in last 24h
    """
    try:
        # Get all datasets
        all_datasets = app.list_all_datasets()
        
        # Apply filters
        filtered = all_datasets
        
        # Filter by source type
        if request.source_type != SourceTypeFilter.all:
            filtered = [
                ds for ds in filtered 
                if ds["metadata"].get("source_type") == request.source_type.value
            ]
        
        # Filter by job_id
        if request.job_id:
            filtered = [
                ds for ds in filtered 
                if ds["metadata"].get("job_id") == request.job_id
            ]
        
        # Filter by stock_ids
        if request.stock_ids:
            filtered = [
                ds for ds in filtered 
                if ds["stock_id"] in request.stock_ids
            ]
        
        # Filter by tags (AND logic - must have all tags)
        if request.tags:
            filtered = [
                ds for ds in filtered 
                if all(tag in ds["metadata"].get("tags", []) for tag in request.tags)
            ]
        
        # Filter by freshness (last 24 hours)
        if request.fresh_only:
            cutoff = datetime.now(timezone.utc) - timedelta(hours=24)
            filtered = [
                ds for ds in filtered 
                if ds["metadata"].get("updated_at") and 
                   datetime.fromisoformat(ds["metadata"]["updated_at"].replace('Z', '+00:00')) > cutoff
            ]
        
        return {
            "datasets": filtered,
            "total_count": len(all_datasets),
            "filtered_count": len(filtered)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

