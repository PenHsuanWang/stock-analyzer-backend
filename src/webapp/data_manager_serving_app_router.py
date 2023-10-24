# webapp.data_manager_serving_app_router.py

from fastapi import APIRouter, Depends, Body, HTTPException
from pydantic import BaseModel

from webapp.data_manager_serving_app import DataManagerApp, get_app

router = APIRouter()


class GetDataRequest(BaseModel):
    stock_id: str
    start_date: str
    end_date: str


class UpdateDataRequest(BaseModel):
    stock_id: str
    start_date: str
    end_date: str
    updated_dataframe: dict  # a dict representation of the dataframe


@router.post("/stock_data/get_data")
def get_stock_data(request: GetDataRequest = Body(...), app: DataManagerApp = Depends(get_app)):
    try:
        data = app.get_stock_data(request.stock_id, request.start_date, request.end_date)
        return {"data": data.to_dict(orient="records")}
        # sample_data = {
        #     "stock_id": "sample_id",
        #     "start_date": "2021-10-20",
        #     "end_date": "2022-10-20"
        # }
        # request_obj = GetDataRequest(**sample_data)
        # print(request_obj)
        # return {"data": {"key", "value"}}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stock_data/check_data_exists")
def check_data_exists(request: GetDataRequest = Body(...), app: DataManagerApp = Depends(get_app)):
    try:
        exists = app.check_data(request.stock_id, request.start_date, request.end_date)
        return {"exists": exists}
    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stock_data/update_data")
def update_stock_data(request: UpdateDataRequest = Body(...), app: DataManagerApp = Depends(get_app)):
    try:
        app.update_stock_data(request.stock_id, request.start_date, request.end_date, request.updated_dataframe)
        return {"message": "Data updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stock_data/delete_data")
def delete_stock_data(request: GetDataRequest = Body(...), app: DataManagerApp = Depends(get_app)):
    try:
        success = app.delete_stock_data(request.stock_id, request.start_date, request.end_date)
        if success:
            return {"message": "Data deleted successfully."}
        else:
            return {"message": "Failed to delete the data."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
