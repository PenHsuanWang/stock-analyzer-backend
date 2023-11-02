from fastapi import APIRouter, Depends, Body, HTTPException
from pydantic import BaseModel

from webapp.serving_app.stock_analysis_serving_app import get_stock_analysis_serving_app, StockAnalysisServingApp

router = APIRouter()

class ComputeMARequest(BaseModel):
    prefix: str
    stock_id: str
    start_date: str
    end_date: str
    window_sizes: list[int]


class ComputeDRRequest(BaseModel):
    prefix: str
    stock_id: str
    start_date: str
    end_date: str


# Define a dependency that will provide an instance of StockAnalysisServingApp
def get_serving_app_dependency():
    return get_stock_analysis_serving_app()


@router.post("/stock_data/compute_and_store_moving_average")
def compute_and_store_moving_average(
    request: ComputeMARequest = Body(...),
    app: StockAnalysisServingApp = Depends(get_serving_app_dependency)
):
    """
    Endpoint to compute moving averages and update Redis store.

    :param request: Request body with stock details and window sizes.
    :param app: Instance of StockAnalysisServingApp provided by Depends.
    :return: Confirmation message.
    """
    try:
        app.calculating_moving_average_and_saved_as_analyzed_prefix(
            prefix=request.prefix,
            stock_id=request.stock_id,
            start_date=request.start_date,
            end_date=request.end_date,
            window_sizes=request.window_sizes
        )
        return {"message": "Moving averages computed and stored into Redis successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stock_data/compute_and_store_daily_return")
def compute_and_store_daily_return(
    request: ComputeDRRequest = Body(...),
    app: StockAnalysisServingApp = Depends(get_serving_app_dependency)
):
    """
    Endpoint to compute daily returns and update Redis store.

    :param request: Request body with stock details.
    :param app: Instance of StockAnalysisServingApp provided by Depends.
    :return: Confirmation message.
    """
    try:
        app.calculating_daily_return_and_saved_as_analyzed_prefix(
            prefix=request.prefix,
            stock_id=request.stock_id,
            start_date=request.start_date,
            end_date=request.end_date
        )
        return {"message": "Daily returns computed and stored into Redis successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
