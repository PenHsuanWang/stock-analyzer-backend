import pandas as pd


class DataSegmentExtractor:

    @staticmethod
    def extract_data_segment(data: pd.DataFrame, index: int, window_prev: int, window_post: int) -> pd.DataFrame:
        """
        Extract a dataframe segment from 'data'. The segment centers around 'index' with
        'window_prev' rows before and 'window_post' rows after the specified index.
        """
        start_index = max(index - window_prev, 0)  # Ensure start_index is not negative
        end_index = min(index + window_post, len(data) - 1)  # Ensure end_index is not beyond the DataFrame

        return data.iloc[start_index:end_index + 1]

    @staticmethod
    def segment_based_on_pattern(data: pd.DataFrame, window_prev: int = 7, window_post: int = 3) -> dict[str, list[pd.DataFrame]]:
        """
        Scan the input dataframe and extract segments based on labeled patterns.
        Each pattern type is categorized with its corresponding segments.
        """
        pattern_segment_dict = {}

        for index, row in data.iterrows():
            if not isinstance(index, int):
                raise ValueError("Index must be an integer")
            if row['Pattern'] and window_prev <= index <= len(data) - window_post - 1:
                segment = DataSegmentExtractor.extract_data_segment(data, index, window_prev, window_post)

                # Add the segment to the corresponding pattern type in the dictionary
                if row['Pattern'] not in pattern_segment_dict:
                    pattern_segment_dict[row['Pattern']] = [segment]
                else:
                    pattern_segment_dict[row['Pattern']].append(segment)

        return pattern_segment_dict

