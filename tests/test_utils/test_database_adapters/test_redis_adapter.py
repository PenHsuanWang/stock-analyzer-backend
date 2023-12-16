# tests/test_redis_adapter.py

import pytest
import json

from unittest.mock import Mock, patch, MagicMock

from src.utils.database_adapters.redis_adapter import RedisAdapter

mock_pipeline = MagicMock()


class MockRedisPipeline(object):
    def __init__(self, mock_redis, transaction=True, shard_hint=None):
        self.mock_redis = mock_redis
        self.commands = []
        self.watching = False
        self.explicit_transaction = False

    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            self.commands.append((name, args, kwargs))
            # Simulate return value if needed, for example:
            if name == 'hget':
                return b'{"value": "some_value"}'  # Example return value
            return self
        return wrapper

    def execute(self):
        # Record the 'execute' command
        self.commands.append(('execute', (), {}))

        # Existing implementation of execute
        results = []
        for cmd, args, kwargs in self.commands:
            command = getattr(self.mock_redis, cmd)
            results.append(command(*args, **kwargs))
        return results

    def multi(self):
        self.explicit_transaction = True
        return self

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.explicit_transaction = False


@pytest.fixture(scope="module")
def redis_adapter():
    # Mock the Redis client
    with patch('src.utils.database_adapters.redis_adapter.redis.StrictRedis') as mock_redis:
        mock_redis.return_value = MagicMock()
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


def test_save_batch_data():
    mock_redis = MagicMock()  # Create a mock Redis client
    mock_pipeline = MockRedisPipeline(mock_redis)  # Create a mock pipeline using the mock Redis client
    mock_redis.pipeline.return_value = mock_pipeline  # Set the mock pipeline as the return value for pipeline calls

    # Initialize RedisAdapter with the mock Redis client
    redis_adapter = RedisAdapter()
    redis_adapter._redis_client = mock_redis

    # Test data
    test_key = 'test-hash'
    test_value = {'field1': 'value1', 'field2': 'value2'}

    # Call the method under test
    result = redis_adapter.save_batch_data(test_key, test_value, 'hash')

    # Check that the correct commands were added to the pipeline
    expected_commands = [
        ('hset', (test_key, 'field1', json.dumps('value1')), {}),
        ('hset', (test_key, 'field2', json.dumps('value2')), {}),
        ('execute', (), {})  # Now included in the expected commands
    ]
    assert mock_pipeline.commands == expected_commands
    assert result is True


# def test_get_batch_data(redis_adapter):
#     # Initialize MockRedisPipeline
#     mock_redis = MagicMock()  # Create a mock Redis client
#     mock_pipeline = MockRedisPipeline(mock_redis)  # Create a mock pipeline using the mock Redis client
#     mock_redis.pipeline.return_value = mock_pipeline  # Set the mock pipeline as the return value for pipeline calls
#
#     # Mock hkeys method (called outside the pipeline)
#     mock_hkeys = [b'field1', b'field2']
#     redis_adapter._redis_client.hkeys = Mock(return_value=mock_hkeys)
#
#     # Set hget return value on the mock Redis client
#     mock_hget_values = [b'{"value": "value1"}', b'{"value": "value2"}']
#     mock_redis.hget.side_effect = mock_hget_values
#
#     # Test data
#     test_key = 'test-hash'
#
#     # Test get_batch_data
#     result = redis_adapter.get_batch_data(test_key, 'hash_keys')
#
#     # Assert hkeys method was called correctly
#     redis_adapter._redis_client.hkeys.assert_called_once_with(test_key)
#
#     # Check that the correct commands were added to the pipeline
#     expected_commands = [
#                             ('hget', (test_key, field), {}) for field in mock_hkeys
#                         ] + [('execute', (), {})]
#
#     # assert mock_pipeline.commands == expected_commands
#     assert result == {field.decode('utf-8'): json.loads(value.decode('utf-8')) for field, value in
#                       zip(mock_hkeys, mock_hget_values)}

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

    # Reset mocks for exception handling test
    mock_pipeline.reset_mock()
    redis_adapter._redis_client.hkeys.side_effect = Exception("Mock Exception")
    # Test for exception handling (additional test case)
    result = redis_adapter.delete_batch_data(test_key, 'hash_keys')
    assert result == False  # Should return False on exception

# Similar tests can be written for save_batch_data, get_batch_data, delete_batch_data, lpush, hset, hkeys, and hget

# TODO: Implement tests for save_batch_data, get_batch_data, delete_batch_data, lpush, hset, hkeys, and hget
