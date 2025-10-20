# strategy_factory.py

from core.processor.signal_labeler.strategies import *
from core.processor.signal_labeler.strategies.bollinger_bands_buy_sell_labeler import BollingerBandsLabeler
from core.processor.signal_labeler.strategies.rsi_dominate_buy_sell_labeler import RsiDominateLabeler
from core.processor.signal_labeler.strategies.ma_crossover_buy_sell_labeler import MovingAverageCrossoverLabeler


class StrategyFactory:
    @staticmethod
    def get_strategy(strategy_name, **kwargs):
        if strategy_name == "bollinger_bands":
            return BollingerBandsLabeler(**kwargs)
        elif strategy_name == "moving_average_crossover":
            return MovingAverageCrossoverLabeler(**kwargs)
        elif strategy_name == "rsi_dominate_buy_sell":
            return RsiDominateLabeler(**kwargs)
        # Add other strategies here
        else:
            raise ValueError("Unknown Strategy")


if __name__ == "__main__":
    import pandas as pd
    import numpy as np

    # Sample data for demonstration
    data = {
        'Close': [100, 102, 104, 103, 105, 106, 107, 108, 110, 109],
        # Mock MACD and Signal Line values for demonstration purposes
        'MACD': np.random.normal(0, 1, 10),
        'Signal_Line': np.random.normal(0, 1, 10),
        # Mock RSI values for demonstration purposes
        'RSI': np.random.uniform(10, 90, 10),
    }

    # Creating a DataFrame from the sample data
    df = pd.DataFrame(data)

    # Example: Creating and applying a Bollinger Bands labeler
    bollinger_labeler = StrategyFactory.get_strategy("bollinger_bands", window=20, num_std_dev=2)
    labeled_data_bb = bollinger_labeler.apply(df)
    print("Bollinger Bands Labeled Data:")
    print(labeled_data_bb)

    # Example: Creating and applying a Moving Average Crossover labeler
    ma_crossover_labeler = StrategyFactory.get_strategy("moving_average_crossover", short_window=5, long_window=10)
    labeled_data_ma = ma_crossover_labeler.apply(df)
    print("\nMoving Average Crossover Labeled Data:")
    print(labeled_data_ma)

    # Example: Creating and applying an RSI Dominant Buy Sell labeler
    # (Assuming necessary columns for RSI calculations are present)
    rsi_labeler = StrategyFactory.get_strategy("rsi_dominate_buy_sell", rsi_buy_threshold=30.0, rsi_sell_threshold=70.0)
    labeled_data_rsi = rsi_labeler.apply(df)
    print("\nRSI Dominant Buy Sell Labeled Data:")
    print(labeled_data_rsi)

