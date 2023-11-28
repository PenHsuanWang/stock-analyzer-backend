# test_data_segment_extractor.py

import pandas as pd
import pytest
from src.core.processor.data_segment_extractor import DataSegmentExtractor


def test_extract_data_segment():

    data = pd.DataFrame({
        'Pattern': ['Bullish', None, 'Bearish', None, None],
        'Value': [10, 20, 30, 40, 50]
    })

    segment = DataSegmentExtractor.extract_data_segment(data, 2, 1, 1)
    assert len(segment) == 3
    assert segment['Value'].tolist() == [20, 30, 40]

    segment = DataSegmentExtractor.extract_data_segment(data, 0, 2, 2)
    assert len(segment) == 3
    assert segment['Value'].tolist() == [10, 20, 30]


def test_segment_based_on_pattern():
    data = pd.DataFrame({
        'Pattern': [None, 'Bearish', None, 'Bullish', None, 'Hammer'],
        'Value': [10, 20, 30, 40, 50, 60]
    })

    segments = DataSegmentExtractor.segment_based_on_pattern(data, 1, 1)
    assert 'Bullish' in segments
    assert 'Bearish' in segments
    assert 'Hammer' not in segments
    assert len(segments['Bullish']) == 1
    assert len(segments['Bearish']) == 1
