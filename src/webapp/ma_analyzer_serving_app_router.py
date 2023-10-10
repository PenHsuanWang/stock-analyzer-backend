from fastapi import APIRouter, Depends, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from webapp.ma_analyzer_serving_app import MovingAverageAnalyzerApp, get_app

router = APIRouter()


class ComputeMARequest(BaseModel):
    stock_id: str
    start_date: str
    end_date: str
    window_sizes: list[int]


@router.post("/stock_data/compute_and_store_moving_average")
def compute_and_store_moving_average(request: ComputeMARequest = Body(...),
                                     app: MovingAverageAnalyzerApp = Depends(get_app)):
    """
    Computes moving averages and updates the Redis store.

    :param request: Pydantic model to parse the request.
    :param app: Dependency injection of MovingAverageAnalyzerApp.
    :return: Confirmation message.
    """

    try:
        app.compute_and_store_moving_average(request.stock_id, request.start_date, request.end_date,
                                             request.window_sizes)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "message": f"An error occurred while computing moving averages. Error details: {str(e)}"
            }
        )
    return {"message": "Moving averages computed and stored into Redis successfully."}
