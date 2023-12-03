from fastapi import APIRouter, Depends, Body, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from webapp.serving_app.stock_analyzer_basic_serving_app import get_stock_analyzer_basic_serving_app, StockAnalyzerBasicServingApp

router = APIRouter()


class StockAnalyzerBasicOperationRequest(BaseModel):
    prefix: str
    stock_id: str
    start_date: str
    end_date: str
    window_sizes: list[int]


class ComputeCorrelationRequest(BaseModel):
    stock_ids: list[str]
    start_date: str
    end_date: str
    metric: str


# Define a dependency that will provide an instance of StockAnalysisServingApp
def get_serving_app_dependency():
    return get_stock_analyzer_basic_serving_app()


@router.post("/stock_data/compute_full_analysis_and_store")
def compute_and_store_moving_average(
    request: StockAnalyzerBasicOperationRequest = Body(...),
    app: StockAnalyzerBasicServingApp = Depends(get_serving_app_dependency)
):
    """
    Endpoint to compute moving averages and update Redis store.

    :param request: Request body with stock details and window sizes.
    :param app: Instance of StockAnalysisServingApp provided by Depends.
    :return: Confirmation message.
    """
    try:
        app.fetch_and_do_full_basic_analysis_and_save(
            prefix=request.prefix,
            stock_id=request.stock_id,
            start_date=request.start_date,
            end_date=request.end_date,
            window_sizes=request.window_sizes
        )
        return {"message": f"Complete to do the basic operation on {request.stock_id}. Saved into Redis"}

    except HTTPException as httpe:
        error_message = f"Error happened in stock analyzer basic serving application: {httpe}"
        raise HTTPException(status_code=500, detail=error_message)

    except Exception as e:
        error_message = f"Unexpected Error happened ! please check: {e}"
        raise HTTPException(status_code=500, detail=error_message)


@router.post("/stock_data/calculate_correlation")
def calculate_correlation(
    request: ComputeCorrelationRequest = Body(...),
    app: StockAnalyzerBasicServingApp = Depends(get_serving_app_dependency)
):
    """
    Endpoint to calculate correlation between assets and optionally store the result.

    :param request: Request body with stock IDs, dates, and metric for correlation.
    :param app: Instance of StockAnalysisServingApp provided by Depends.
    :return: JSON response with correlation data.
    """
    try:
        correlation_df = app.calculate_correlation(stock_ids=request.stock_ids, start_date=request.start_date,
                                                   end_date=request.end_date, metric=request.metric)
        return correlation_df.to_dict()
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "message": f"An error occurred while computing asset correlations. Error details: {str(e)}"
            }
        )

