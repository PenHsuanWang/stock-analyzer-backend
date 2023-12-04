from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel
from webapp.serving_app.data_exporter_serving_app import DataExporterApp, get_app

router = APIRouter()


class ExportRequest(BaseModel):
    key: str  # Redis key
    export_type: str  # Export type ('csv' or 'http')
    filepath: str = None  # Required for CSV export
    url: str = None  # Required for HTTP export
    method: str = "POST"  # HTTP method, default is POST


@router.post("/data/export")
def export_data(request: ExportRequest, app: DataExporterApp = Depends(get_app)):
    # Determine export type and call appropriate method
    if request.export_type == 'csv' and request.filepath:
        app.export_data(key=request.key, export_type='csv', filepath=request.filepath)
        return {"message": "Data exported to CSV successfully."}
    elif request.export_type == 'http' and request.url:
        app.export_data(key=request.key, export_type='http', url=request.url, method=request.method)
        return {"message": "Data sent to HTTP server successfully."}
    else:
        return {"message": "Invalid export request parameters."}

