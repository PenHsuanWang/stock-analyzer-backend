# src/server.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from webapp import data_fetcher_serving_app_router, ma_analyzer_serving_app_router, daily_return_serving_app_router



origins = [
    "http://localhost:3000",  # for react application development
]

app = FastAPI()

# Include the router in the main FastAPI app
app.include_router(data_fetcher_serving_app_router.router)
app.include_router(ma_analyzer_serving_app_router.router)
app.include_router(daily_return_serving_app_router.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

