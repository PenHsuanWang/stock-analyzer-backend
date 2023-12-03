from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel
from webapp.serving_app.data_exporter_serving_app import DataExporterApp, get_app
import pandas as pd

router = APIRouter()


class ExportToCSVRequest(BaseModel):
    data: dict # Expected to be a DataFrame in dictionary format
    filepath: str


class SendDataHTTPRequest(BaseModel):
    data: dict # Expected to be a DataFrame or NumPy array in dictionary format
    url: str
    method: str = "POST"


@router.post("/data/export_to_csv")
def export_to_csv(request: ExportToCSVRequest, app: DataExporterApp = Depends(get_app)):
    data_df = pd.DataFrame(request.data)
    app.export_to_csv(data_df, request.filepath)
    return {"message": "Data exported to CSV successfully."}


@router.post("/data/send_http")
def send_data_http(request: SendDataHTTPRequest, app: DataExporterApp = Depends(get_app)):
    data_df = pd.DataFrame(request.data)
    app.send_data_http(data_df, request.url, request.method)
    return {"message": "Data sent to HTTP server successfully."}
