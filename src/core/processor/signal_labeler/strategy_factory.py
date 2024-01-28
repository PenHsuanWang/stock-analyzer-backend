# strategy_factory.py

from src.core.processor.signal_labeler.strategies import *
from src.core.processor.signal_labeler.strategies.bollinger_bands_buy_sell_labeler import BollingerBandsLabeler
from src.core.processor.signal_labeler.strategies.rsi_dominate_buy_sell_labeler import RsiDominateLabeler
from src.core.processor.signal_labeler.strategies.ma_crossover_buy_sell_labeler import MovingAverageCrossoverLabeler


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
