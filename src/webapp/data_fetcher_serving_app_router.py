from fastapi import APIRouter, Depends, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel

import pandas as pd

from webapp.data_fetcher_serving_app import StockDataFetcherApp, get_app

router = APIRouter()


class FetchStockDataRequest(BaseModel):
    stock_id: str
    start_date: str
    end_date: str


@router.post("/stock_data/fetch_and_get_as_dataframe")
def fetch_data_and_get_as_dataframe(request: FetchStockDataRequest = Body(...),
                                    app: StockDataFetcherApp = Depends(get_app)):
    """
    Fetch stock data using stock id and date range and then get it as a DataFrame.
    :param request: pydantic model to parse the request.
    :param app: Dependency injection of StockDataFetcherApp.
    :return: Data in DataFrame format.
    """

    try:
        dataframe = app.fetch_data_and_get_as_dataframe(request.stock_id, request.start_date, request.end_date)
    except RuntimeError:
        return JSONResponse(
            status_code=500,
            content={"message": "An error occurred while fetching the stock data. Please check the input parameters."}
        )

    # Convert DataFrame to JSON for response.
    # This approach might not be efficient for very large DataFrames.
    return dataframe.to_json(orient="records")


@router.post("/stock_data/fetch_and_stash")
def fetch_data_and_stash(request: FetchStockDataRequest = Body(...), app: StockDataFetcherApp = Depends(get_app)):
    """
    Fetch stock data using stock id and date range and stash it into Redis.
    :param request: Pydantic model to parse the request.
    :param app: Dependency injection of StockDataFetcherApp.
    :return: Confirmation message.
    """

    try:
        app.fetch_data_and_stash(request.stock_id, request.start_date, request.end_date)
    except RuntimeError:
        return JSONResponse(
            status_code=500,
            content={
                "message": "An error occurred while fetching and stashing the stock data. Please check the input parameters."}
        )

    return {"message": "Data fetched and stashed into Redis successfully."}
