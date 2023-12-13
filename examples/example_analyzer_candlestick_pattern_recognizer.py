
import pandas as pd
from src.core.analyzer.candlestick_pattern_analyzer import CandlestickPatternAnalyzer


def main():

    df = pd.read_csv('AAPL.csv')
    pattern_analyzer = CandlestickPatternAnalyzer()

    patterns_df = pattern_analyzer.analyze_patterns(df)

    # Set pandas options to display all rows and columns
    pd.set_option('display.max_rows', None)  # Set to None to display all rows
    pd.set_option('display.max_columns', None)  # Set to None to display all columns
    pd.set_option('display.width', None)  # Ensure the output isn't wrapped
    pd.set_option('display.max_colwidth', None)  # Display full content of

    print(patterns_df)


if __name__ == "__main__":
    main()
