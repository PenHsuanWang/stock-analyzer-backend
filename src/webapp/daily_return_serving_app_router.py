from fastapi import APIRouter, Depends, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from webapp.daily_return_serving_app import DailyReturnApp, get_app

router = APIRouter()

class ComputeDRRequest(BaseModel):
    stock_id: str
    start_date: str
    end_date: str

@router.post("/stock_data/compute_and_store_daily_return")
def compute_and_store_daily_return(request: ComputeDRRequest = Body(...),
                                   app: DailyReturnApp = Depends(get_app)):
    """
    Computes daily returns and updates the Redis store.

    :param request: Pydantic model to parse the request.
    :param app: Dependency injection of DailyReturnApp.
    :return: Confirmation message.
    """

    try:
        app.compute_and_store_daily_return(request.stock_id, request.start_date, request.end_date)
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={
                "message": f"An error occurred while computing daily returns. Error details: {str(e)}"
            }
        )
    return {"message": "Daily returns computed and stored into Redis successfully."}
