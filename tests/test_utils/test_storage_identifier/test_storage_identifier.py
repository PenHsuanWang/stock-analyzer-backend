# test_storage_identifier.py

import pytest
from src.utils.storage_identifier.identifier_strategy import (
    DefaultStockDataIdentifierGenerator,
    SlicingStockDataIdentifierGenerator,
    NullStockDataIdentifierGenerator
)


def test_default_stock_data_identifier_generator():
    generator = DefaultStockDataIdentifierGenerator()
    identifier = generator.generate_identifier(
        prefix="prefix", stock_id="1234", start_date="2023-01-01", end_date="2023-01-10"
    )
    assert identifier == "prefix:1234:2023-01-01:2023-01-10" == "prefix:1234:2023-01-01:2023-01-10"


def test_slicing_stock_data_identifier_generator():
    generator = SlicingStockDataIdentifierGenerator()
    identifier = generator.generate_identifier(
        prefix="prefix", stock_id="1234", start_date="2023-01-01", end_date="2023-01-10", post_id="post1"
    )
    assert identifier == "prefix:1234:2023-01-01:2023-01-10:post1"


def test_null_stock_data_identifier_generator():
    generator = NullStockDataIdentifierGenerator()
    identifier = generator.generate_identifier()
    assert identifier == ""


def test_default_stock_data_identifier_generator_with_missing_args():
    generator = DefaultStockDataIdentifierGenerator()
    with pytest.raises(TypeError):
        generator.generate_identifier(prefix="prefix", stock_id="1234", start_date="2023-01-01")
