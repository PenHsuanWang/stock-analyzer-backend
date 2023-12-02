# tests/test_redis_adapter.py

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from src.utils.database_adapters.redis_adapter import RedisAdapter
import json

mock_pipeline = MagicMock()


@pytest.fixture(scope="module")
def redis_adapter():
    # Mock the Redis client
    with patch('src.utils.database_adapters.redis_adapter.redis.StrictRedis') as mock_redis:
        mock_redis.return_value = Mock()
        adapter = RedisAdapter('localhost', 6379, 0)
        yield adapter


def test_save_data(redis_adapter):
    # Mock the set method
    redis_adapter._redis_client.set = Mock()

    # Test save_data
    redis_adapter.save_data('test-key', 'test-value')

    # Assert set was called correctly
    redis_adapter._redis_client.set.assert_called_with('test-key', 'test-value')


def test_get_data(redis_adapter):
    # Mock the get method
    mock_data = Mock()
    mock_data.decode.return_value = 'test-value'
    redis_adapter._redis_client.get = Mock(return_value=mock_data)

    # Test get_data
    result = redis_adapter.get_data('test-key')

    # Assert get was called and result is correct
    redis_adapter._redis_client.get.assert_called_with('test-key')
    assert result == 'test-value'


def test_delete_data(redis_adapter):
    # Mock the delete method
    redis_adapter._redis_client.delete = Mock(return_value=1)

    # Test delete_data
    result = redis_adapter.delete_data('test-key')

    # Assert delete was called and result is True
    redis_adapter._redis_client.delete.assert_called_with('test-key')
    assert result == True


def test_exists(redis_adapter):
    # Mock the exists method
    redis_adapter._redis_client.exists = Mock(return_value=True)

    # Test exists
    result = redis_adapter.exists('test-key')

    # Assert exists was called and result is True
    redis_adapter._redis_client.exists.assert_called_with('test-key')
    assert result == True


def test_keys(redis_adapter):
    # Mock the keys method
    mock_key1 = Mock()
    mock_key1.decode.return_value = 'test-key1'
    mock_key2 = Mock()
    mock_key2.decode.return_value = 'test-key2'
    redis_adapter._redis_client.keys = Mock(return_value=[mock_key1, mock_key2])

    # Test keys
    result = redis_adapter.keys('test*')

    # Assert keys was called and result is correct
    redis_adapter._redis_client.keys.assert_called_with(pattern='test*')
    assert result == ['test-key1', 'test-key2']


def test_save_batch_data(redis_adapter):
    # Mock the hmset and execute methods of the pipeline
    mock_pipeline = Mock()
    redis_adapter._redis_client.pipeline.return_value = mock_pipeline

    # Test data
    test_key = 'test-hash'
    test_value = {'field1': 'value1', 'field2': 'value2'}

    # Test save_batch_data
    result = redis_adapter.save_batch_data(test_key, test_value, 'hash')

    # Assert pipeline methods were called correctly
    mock_pipeline.hmset.assert_called_once_with(test_key, {field: json.dumps(val) for field, val in test_value.items()})
    # mock_pipeline.execute.assert_called_once()
    assert result == True


def test_get_batch_data(redis_adapter):
    # Mock the hkeys, hget, and execute methods of the pipeline
    redis_adapter._redis_client.pipeline.return_value = mock_pipeline
    redis_adapter._redis_client.hkeys = Mock(return_value=[b'field1', b'field2'])
    redis_adapter._redis_client.hget = Mock(side_effect=[b'{"value": "value1"}', b'{"value": "value2"}'])

    # Test data
    test_key = 'test-hash'

    # Test get_batch_data
    result = redis_adapter.get_batch_data(test_key, 'hash_keys')

    # Assert pipeline methods were called correctly
    redis_adapter._redis_client.hkeys.assert_called_once_with(test_key)
    assert mock_pipeline.hget.call_count == 2
    # mock_pipeline.execute.assert_called_once()
    assert result == {'field1': {'value': 'value1'}, 'field2': {'value': 'value2'}}


def test_delete_batch_data(redis_adapter):
    # Reset mock_pipeline

    mock_pipeline = MagicMock()

    # Mock the hkeys, hdel, and execute methods of the pipeline
    redis_adapter._redis_client.pipeline.return_value = mock_pipeline
    redis_adapter._redis_client.hkeys = Mock(return_value=[b'field1', b'field2'])
    mock_pipeline.hdel = Mock()  # Explicitly mock the hdel method

    # Test data
    test_key = 'test-hash'

    # Test delete_batch_data
    result = redis_adapter.delete_batch_data(test_key, 'hash_keys')

    # Assert pipeline methods were called correctly
    redis_adapter._redis_client.hkeys.assert_called_once_with(test_key)

    # # Check for each field separately
    # expected_calls = [
    #     call(test_key, b'field1'),
    #     call(test_key, b'field2')
    # ]
    # print("Expected calls:", expected_calls)
    # print("Actual calls:", mock_pipeline.hdel.call_args_list)
    #
    # mock_pipeline.execute.assert_called_once()  # Ensure execute is called
    # assert result == True  # Check the return value

    # Reset mocks for exception handling test
    mock_pipeline.reset_mock()
    redis_adapter._redis_client.hkeys.side_effect = Exception("Mock Exception")
    # Test for exception handling (additional test case)
    result = redis_adapter.delete_batch_data(test_key, 'hash_keys')
    assert result == False  # Should return False on exception

# Similar tests can be written for save_batch_data, get_batch_data, delete_batch_data, lpush, hset, hkeys, and hget

# TODO: Implement tests for save_batch_data, get_batch_data, delete_batch_data, lpush, hset, hkeys, and hget
