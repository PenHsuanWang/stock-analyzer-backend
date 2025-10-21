# src/webapp/router/data_exporter_serving_app_router.py

from fastapi import APIRouter, Depends, HTTPException
import requests
from pydantic import BaseModel

from webapp.serving_app.data_exporter_serving_app import DataExporterApp, get_app

router = APIRouter()


class ExportToCSVRequest(BaseModel):
    key: str
    filepath: str


class SendDataOverHTTPRequest(BaseModel):
    key: str
    url: str
    method: str = 'POST'


@router.post("/export_data/csv")
def export_data_to_csv(request: ExportToCSVRequest, app: DataExporterApp = Depends(get_app)):
    try:
        result = app.export_data(key=request.key, export_type='csv', filepath=request.filepath)
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.post("/export_data/http")
def send_data_over_http(request: SendDataOverHTTPRequest, app: DataExporterApp = Depends(get_app)):
    try:
        response = app.export_data(key=request.key, export_type='http', url=request.url, method=request.method)
        # Ensure the response is a requests.Response object
        if response and isinstance(response, requests.Response):
            return {"message": "Data has been sent successfully.", "server_response": response.json()}
        else:
            raise HTTPException(status_code=500, detail="Received no response or invalid response from the HTTP export operation.")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
