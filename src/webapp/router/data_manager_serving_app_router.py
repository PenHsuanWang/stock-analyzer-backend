# webapp.data_manager_serving_app_router.py
import pandas as pd
from fastapi import APIRouter, Depends, Body, HTTPException
from pydantic import BaseModel

from src.webapp.serving_app.data_manager_serving_app import DataManagerApp, get_app

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
