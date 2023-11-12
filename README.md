# Project Title: Stock Analyzer Backend

This project leverages the power of Python's FastAPI framework to provide users with a robust service for stock analysis. Our system is designed to fetch data from external sources like Yahoo Finance and store it in a local Redis instance for rapid access.

The Python backend server of this project is engineered to serve frontend requests seamlessly. It shoulders the responsibilities of workflow management, data read/write operations, and the orchestration of various analysis processes. However, it's crucial to note that the number-crunching and numerical computations aren't done within this backend project. Instead, these stateless numerical operations are executed by a distinct package named stockana. Only logic and operations pertaining to computational states are present within this project. Our project is modularized into three main packages: core, utils, and webapp.

---

## Modular Introduction

project structure
```text
.
├── __init__.py
├── core
│   ├── __init__.py
│   ├── analyzer
│   │   ├── __init__.py
│   │   ├── cross_asset_analyzer.py
│   │   ├── daily_return_analyzer.py
│   │   └── moving_average_analyzer.py
│   └── manager
│       ├── __init__.py
│       └── data_manager.py
├── main.py
├── run_server.py
├── server.py
├── utils
│   ├── __init__.py
│   ├── data_io
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── data_fetcher.py
│   └── store
│       ├── __init__.py
│       └── companies.py
└── webapp
    ├── __init__.py
    ├── router
    │   ├── __init__.py
    │   ├── data_fetcher_serving_app_router.py
    │   ├── data_manager_serving_app_router.py
    │   └── stock_analysis_serving_app_router.py
    └── serving_app
        ├── __init__.py
        ├── data_fetcher_serving_app.py
        ├── data_manager_serving_app.py
        └── stock_analysis_serving_app.py
```

### 1. Core

The `core` module is the heart of the project, focusing on all logic and calculations directly related to the `stockana` package. It mainly encompasses core operations of stock analysis, such as calculating the moving average. This module also ensures data flows efficiently and smoothly during the analysis process, utilizing management tools like `data_manager` to facilitate data storage and handling.

#### Implementation Example Explanation:
- `moving_average_analyzer.py` defines the `MovingAverageAnalyzer` class, primarily designed to fetch stock data from Redis, compute its moving average, and update such data in Redis. Additionally, this file offers a straightforward example showcasing how to employ this class to calculate the moving average of a specific stock.

### 2. Utils

The `utils` module provides a collection of auxiliary tools, focusing on tasks not directly related to stock analysis but vital for overall functionality. These utilities ensure that `core` can smoothly receive and process data without concerning itself with the data's source or format.

#### Implementation Example Explanation:
- The provided example illustrates that data is fetched from Redis, implying that the `utils` module might have tools assisting in connecting and managing the Redis database access.

### 3. Webapp

The `webapp` module serves as a bridge, transforming functionalities and logic in `core` into a Web API accessible directly by end-users. Using the FastAPI framework, `webapp` offers a set of applications and defines corresponding routes, allowing users to access and utilize stock analysis functions via specific URL endpoints.

#### Implementation Example Explanation:
- `ma_analyzer_serving_app.py` defines the `MovingAverageAnalyzerApp` singleton class, aiming to encapsulate the functionalities of `MovingAverageAnalyzer` for webapp use. It provides a static method `compute_and_store_moving_average` to compute the moving average.
- `ma_analyzer_serving_app_router.py` is a route definition file for FastAPI, establishing an endpoint `/stock_data/compute_and_store_moving_average`. When invoked, this endpoint computes the moving average and updates the Redis database.

## Application Introduction

The project structure distinctly separates computational and backend services, ensuring that each module has a specific focus and excels in its functionality.

### Computational Aspects (`core/analyzer`):

1. **Moving Average Calculation (`moving_average_analyzer.py`):** This module provides the functionality to calculate the moving average for stocks or other assets. The moving average is a technical indicator commonly used in stock market analysis that aids investors in understanding price trends and market dynamics better.

2. **Daily Return Calculation (`daily_return_analyzer.py`):** The primary function of this module is to compute the daily return for stocks or other assets. This is a crucial metric for investors evaluating asset performance and risk.

3. **Cross-Asset Correlation Analysis (`cross_asset_analyzer.py`):** The function of this module is to analyze the price correlation between two or more assets. Cross-asset analysis can help investors determine the risk diversification strategy of an asset portfolio and identify potential arbitrage opportunities.

### Backend Serving:

1. **Data Access Management (`core/manager/data_manager.py` and `webapp/data_manager_serving_app.py`):** The `data_manager.py` under `core` is responsible for data flow and access, ensuring that data can be smoothly extracted from external sources, stored, and correctly transferred between internal modules. Correspondingly, `data_manager_serving_app.py` under `webapp` acts as the Web API version of this module, allowing external services or frontend interfaces to interact directly with the data management module.


---

The three main modules collaborate to form a comprehensive stock analysis system, from data sourcing, core analysis, to Web API provision, ensuring users receive precise and timely analysis results. Not only do these modules ensure data accuracy and reliability, but they also offer a user-friendly web interface, allowing end-users easy access to analysis functionalities.

## Example

In this example, we'll delve into using the previously introduced `core` and `webapp` modules to implement the moving average analysis functionality.

### `core` - MovingAverageAnalyzer

Within the `core` module, `MovingAverageAnalyzer` is tasked with calculating the moving average. It initially fetches stock data from the Redis database, then employs the `stockana` package to compute the moving average, updating the database subsequently.

The principal function of this class is `calculate_moving_average`, requiring the following parameters:

- `stock_id`: Stock code.
- `start_date` and `end_date`: Starting and ending dates of the data.
- `window_sizes`: List of window sizes for the moving average to be computed.

Additionally, this class guarantees thread safety in Redis operations using `threading.Lock()`.

### `webapp` - MovingAverageAnalyzerApp and Router

The `webapp` module offers the `MovingAverageAnalyzerApp` singleton class, encapsulating and providing the Web API functionalities for moving average analysis. The `compute_and_store_moving_average` function allows this app to invoke the core module's `MovingAverageAnalyzer` for computation and storage of moving averages.

Lastly, we define `ma_analyzer_serving_app_router.py`. This routing file, utilizing the FastAPI framework, sets up an endpoint `/stock_data/compute_and_store_moving_average`, enabling users to send POST requests with parameters like stock code, dates, and window sizes, and returns the computed results.

When users send a request to this API endpoint, the request is processed through the `MovingAverageAnalyzerApp`'s `compute_and_store_moving_average` function, thus achieving the objective of computing the moving average and updating the Redis database.

### Conclusion

This example demonstrates the amalgamation of `core` and `webapp` modules to offer a complete moving average computation functionality. It aptly separates the core computational logic from the Web API, rendering the overall design both clear and scalable.

---

### Developer Notes:

Always ensure that you're familiar with the purpose and responsibilities of each package before diving in. Modularity has been emphasized to ensure that each section of the codebase can be understood, maintained, and tested independently.

---
