from fastapi import APIRouter, Depends, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from webapp.cross_asset_serving_app import CrossAssetApp, get_app

router = APIRouter()

class ComputeCorrelationRequest(BaseModel):
    stock_ids: list[str]
    start_date: str
    end_date: str

@router.post("/stock_data/compute_assets_correlation")
def compute_assets_correlation(request: ComputeCorrelationRequest = Body(...),
                               app: CrossAssetApp = Depends(get_app)):
    """
    Computes correlation among different stocks and returns the result.

    :param request: Pydantic model to parse the request.
    :param app: Dependency injection of CrossAssetApp.
    :return: DataFrame of correlations
    """

    try:
        correlation_df = app.compute_assets_correlation(request.stock_ids, request.start_date, request.end_date)
        return correlation_df.to_dict()
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "message": f"An error occurred while computing asset correlations. Error details: {str(e)}"
            }
        )
