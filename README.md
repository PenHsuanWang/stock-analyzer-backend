# Project Title: Stock Analyzer Backend

This project leverages the power of Python's FastAPI framework to provide users with a robust service for stock analysis. Our system is designed to fetch data from external sources like Yahoo Finance and store it in a local Redis instance for rapid access.

The Python backend server of this project is engineered to serve frontend requests seamlessly. It shoulders the responsibilities of workflow management, data read/write operations, and the orchestration of various analysis processes. However, it's crucial to note that the number-crunching and numerical computations aren't done within this backend project. Instead, these stateless numerical operations are executed by a distinct package named stockana. Only logic and operations pertaining to computational states are present within this project. Our project is modularized into three main packages: core, utils, and webapp.

---

## Modular Introduction

### System Architecture

Our system is organized into three primary modules, each serving a distinct purpose in the stock analysis process:

1. **Core Module**: The backbone of the system, responsible for all core analytical computations and logic. It includes various analyzers for different technical analyses and the strategy pattern-based signal labeling system.

2. **Utils Module**: Provides auxiliary tools and utilities that support the core functionalities, including data sourcing, formatting, and database management tools.

3. **Webapp Module**: Serves as the interface for users to interact with the core functionalities. It transforms the analytical capabilities into accessible Web API endpoints, allowing users to perform stock analysis via HTTP requests.

project structure
```text
src
├── __init__.py
├── core
│   ├── __init__.py
│   ├── analyzer
│   │   ├── __init__.py
│   │   ├── candlestick_pattern_analyzer.py
│   │   ├── cross_asset_analyzer.py
│   │   ├── daily_return_analyzer.py
│   │   └── moving_average_analyzer.py
│   ├── manager
│   │   ├── __init__.py
│   │   └── data_manager.py
│   └── processor
│       ├── __init__.py
│       ├── data_convertor
│       │   ├── __init__.py
│       │   ├── preprocessor_base.py
│       │   └── time_series_preprocessor.py
│       ├── data_segment_extractor.py
│       └── gaf_processor.py
├── main.py
├── run_server.py
├── server.py
├── utils
│   ├── __init__.py
│   ├── data_io
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── data_fetcher.py
│   ├── database_adapters
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── minio_adapter.py
│   │   └── redis_adapter.py
│   ├── storage_identifier
│   │   ├── __init__.py
│   │   └── identifier_strategy.py
│   └── store
│       ├── __init__.py
│       └── companies.py
└── webapp
    ├── __init__.py
    ├── router
    │   ├── __init__.py
    │   ├── data_fetcher_serving_app_router.py
    │   ├── data_manager_serving_app_router.py
    │   ├── stock_analysis_serving_app_router.py
    │   └── stock_analyzer_basic_serving_app_router.py
    └── serving_app
        ├── __init__.py
        ├── data_fetcher_serving_app.py
        ├── data_manager_serving_app.py
        ├── stock_analysis_serving_app.py
        ├── stock_analyzer_basic_serving_app.py
        └── stock_data_transformation_serving_app.py
```

### 1. Core

The `core` module is the heart of the project, focusing on all logic and calculations directly related to the `stockana` package. It mainly encompasses core operations of stock analysis, such as calculating the moving average and labeling buy and sell signals based on various technical indicators. This module also ensures data flows efficiently and smoothly during the analysis process, utilizing management tools like `data_manager` to facilitate data storage and handling.

#### Implementation Example Explanation:
- `moving_average_analyzer.py` defines the `MovingAverageAnalyzer` class, primarily designed to fetch stock data from Redis, compute its moving average, and update such data in Redis.
- `signal_labeler` directory contains the strategy pattern implementation for labeling trading signals on stock data. The `buy_and_sell_signal_labeling.py` script within this directory implements the `BuySellSignalLabeler` class, a concrete strategy for identifying buy and sell signals based on MACD and RSI indicators.

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

4. **Buy and Sell Signal Labeling (`signal_labeler/buy_and_sell_signal_labeling.py`):**
   - This module implements the `BuySellSignalLabeler` class, which is used to label buy and sell signals in stock data based on MACD and RSI indicators. It follows the strategy pattern, allowing for easy extension with new labeling strategies in the future.

---

## Backend Serving:

### Data Access Management (`core/manager/data_manager.py` and `webapp/data_manager_serving_app.py`):** The `data_manager.py` under `core` is responsible for data flow and access, ensuring that data can be smoothly extracted from external sources, stored, and correctly transferred between internal modules. Correspondingly, `data_manager_serving_app.py` under `webapp` acts as the Web API version of this module, allowing external services or frontend interfaces to interact directly with the data management module.

#### Batch Data Handling Capabilities

In the latest development cycle, we've introduced three new functions in the `DataManagerApp` class, enhancing our backend's capability to handle batch data operations. These additions are crucial for dealing with large datasets efficiently and are particularly useful when operating on grouped stock data or when simultaneous operations on multiple data sets are required.

1. **Save Dataframes Group**:
   - The `save_dataframes_group` function allows for the storage of a group of Pandas DataFrames in the Redis database. This is particularly useful for handling batch operations where multiple datasets need to be stored simultaneously under a common group identifier.
   - Usage Example: This function can be utilized to store a collection of stock data frames, each representing a different stock, under a single group identifier.

2. **Get Dataframes Group**:
   - The `get_dataframes_group` function enables the retrieval of a group of DataFrames, previously stored using the `save_dataframes_group` function. This allows for efficient access to batch data that has been grouped together under a single identifier.
   - Usage Example: This can be used to fetch all stock data frames related to a specific group of stocks for batch processing or analysis.

3. **Delete Dataframes Group**:
   - The `delete_dataframes_group` function provides the capability to delete a group of DataFrames from the Redis database. This is vital for maintaining the integrity and relevance of the data in the database, allowing for the removal of outdated or unnecessary batch data.
   - Usage Example: This function can be employed to remove old or irrelevant stock data collections from a specific group, ensuring that the database is not cluttered with stale data.

These functions are encapsulated within the `DataManagerApp` class, ensuring thread safety and consistency in data operations. They represent a significant enhancement in our backend's ability to handle complex data operations, making our system more robust and versatile in dealing with various data management scenarios.


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

This update introduces a flexible and extensible approach to labeling trading signals, enhancing the stock analysis capabilities of the system. The implementation showcases the use of design patterns to ensure scalability and maintainability in financial data analysis.

---

## Introduction to Software Architecture and Coding Practices

### Software Architecture Overview

Our system is structured into three main modules, each with its own specific responsibilities and design principles. Understanding this modular architecture is key to navigating and contributing to the project effectively.

#### Core Module

- **Purpose**: The Core module is the backbone of our application, handling the primary logic and computation related to stock analysis.
- **Components**:
  - **Analyzers**: These classes (e.g., `MovingAverageAnalyzer`, `BuySellSignalLabeler`) perform the core computations, such as calculating technical indicators and labeling signals.
  - **Managers**: The `DataManager` class is responsible for the flow and management of data within the system.
- **Key Principles**: Emphasis on computational efficiency, accuracy, and maintainability. Utilizes design patterns like Strategy (for signal labeling) to ensure extensibility.

#### Utils Module

- **Purpose**: Provides auxiliary functionalities that support the Core module. This includes data handling, formatting, and external integrations.
- **Components**: Classes and functions dedicated to data fetching, conversion, and database management.
- **Key Principles**: Focus on reliability and scalability. Ensures that Core functions can seamlessly receive and process data.

#### Webapp Module

- **Purpose**: Transforms Core functionalities into Web API endpoints using the FastAPI framework.
- **Components**: Includes router and serving app classes that define API routes and connect them to Core functionalities.
- **Key Principles**: Emphasizes usability and accessibility. The API design aims to be intuitive and user-friendly.

### Coding Guidelines

To maintain code quality and consistency, we adhere to the following coding practices:

- **Style Guide**: Follow PEP 8 for Python code styling. Ensure readability and clean code formatting.
- **Documentation**: Write comprehensive docstrings for classes and methods. New functionalities should be well-documented with clear descriptions, parameters, and return types.
- **Testing**: Prioritize writing tests for new features. Ensure that existing tests pass before pushing code changes.
- **Code Reviews**: All contributions should be reviewed through pull requests. Engage in constructive code reviews to maintain code quality.
- **Version Control**: Use Git for version control. Commit messages should be clear and descriptive.

### Getting Started with Development

1. **Setup**: Clone the repository and set up a development environment. Familiarize yourself with the project structure and dependencies.
2. **First Steps**: Start by reviewing existing code to understand implementation patterns. Explore the `tests` directory to understand how functionalities are tested.
3. **Contribution**: Pick up issues or tasks that match your skill level. Begin with smaller tasks to get accustomed to the codebase and workflow.
4. **Ask Questions**: Don’t hesitate to ask for help or clarifications from the team. Collaboration is key to our project's success.

---
