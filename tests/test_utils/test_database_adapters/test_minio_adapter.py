# tests/test_minio_adapter.py

import pytest
from unittest.mock import Mock, patch, ANY
from src.utils.database_adapters.minio_adapter import MinIOAdapter

from minio.error import S3Error

@pytest.fixture(scope="module")
def minio_adapter():
    # Mock the MinIO client
    with patch('src.utils.database_adapters.minio_adapter.Minio') as mock_minio:
        mock_minio.return_value = Mock()
        adapter = MinIOAdapter('localhost:9000', 'minioadmin', 'minioadmin', secure=False)
        yield adapter


def test_set_data(minio_adapter):
    # Mock the put_object method
    minio_adapter.client.put_object = Mock()

    # Test set_data
    minio_adapter.set_data('test-key', b'test-data', 'test-bucket')

    # Assert put_object was called correctly
    minio_adapter.client.put_object.assert_called_with('test-bucket', 'test-key', ANY, length=9)


def test_get_data(minio_adapter):
    # Mock the get_object method
    mock_response = Mock()
    mock_response.read.return_value = b'test-data'
    minio_adapter.client.get_object = Mock(return_value=mock_response)

    # Test get_data
    result = minio_adapter.get_data('test-key', 'test-bucket')

    # Assert get_object was called and result is correct
    minio_adapter.client.get_object.assert_called_with('test-bucket', 'test-key')
    assert result == b'test-data'


def test_delete_data(minio_adapter):
    # Mock the remove_object method
    minio_adapter.client.remove_object = Mock()

    # Test delete_data
    result = minio_adapter.delete_data('test-key', 'test-bucket')

    # Assert remove_object was called and result is True
    minio_adapter.client.remove_object.assert_called_with('test-bucket', 'test-key')
    assert result == True


def test_exists(minio_adapter):
    # Mock the stat_object method
    minio_adapter.client.stat_object = Mock()

    # Test exists
    result = minio_adapter.exists('test-key', 'test-bucket')

    # Assert stat_object was called and result is True
    minio_adapter.client.stat_object.assert_called_with('test-bucket', 'test-key')
    assert result == True

def test_keys(minio_adapter):
    # Mock the list_objects method
    mock_object1 = Mock()
    mock_object1.object_name = 'test-key1'
    mock_object2 = Mock()
    mock_object2.object_name = 'test-key2'
    minio_adapter.client.list_objects = Mock(return_value=[mock_object1, mock_object2])

    # Test keys
    result = minio_adapter.keys('test-bucket', 'test')

    # Assert list_objects was called and result is correct
    minio_adapter.client.list_objects.assert_called_with('test-bucket', prefix='test', recursive=False)
    assert result == ['test-key1', 'test-key2']


def test_set_empty_data(minio_adapter):
    # Mock the put_object method for empty data
    minio_adapter.client.put_object = Mock()

    # Test set_data with empty data
    minio_adapter.set_data('test-empty', b'', 'test-bucket')

    # Assert put_object was called correctly with empty data
    minio_adapter.client.put_object.assert_called_with('test-bucket', 'test-empty', ANY, length=0)


def test_get_nonexistent_data(minio_adapter):
    # Mock the get_object method to raise S3Error for nonexistent key
    mock_s3error = S3Error("NoSuchKey", "The specified key does not exist.", resource="some_resource", request_id="some_request_id", host_id="some_host_id", response="some_response")
    minio_adapter.client.get_object = Mock(side_effect=mock_s3error)

    # Test get_data with nonexistent key
    result = minio_adapter.get_data('nonexistent', 'test-bucket')

    # Assert get_object was called and None is returned for nonexistent key
    minio_adapter.client.get_object.assert_called_with('test-bucket', 'nonexistent')
    assert result is None


def test_set_invalid_data_type(minio_adapter):
    # Test set_data with invalid data type should raise ValueError
    with pytest.raises(ValueError):
        minio_adapter.set_data('test-invalid', 12345, 'test-bucket')  # Invalid data type


def test_operations_on_nonexistent_bucket(minio_adapter):
    nonexistent_bucket = 'nonexistent-bucket'
    test_key = 'test-object'

    # Create a mock S3Error object for nonexistent bucket
    mock_s3error = S3Error("NoSuchBucket", "The specified bucket does not exist.", resource="some_resource",
                           request_id="some_request_id", host_id="some_host_id", response="some_response")
    minio_adapter.client.put_object = Mock(side_effect=mock_s3error)
    minio_adapter.client.get_object = Mock(side_effect=mock_s3error)
    minio_adapter.client.remove_object = Mock(side_effect=mock_s3error)
    minio_adapter.client.stat_object = Mock(side_effect=mock_s3error)

    # Test set_data on a nonexistent bucket
    with pytest.raises(ValueError):
        minio_adapter.set_data(test_key, b'test-data', nonexistent_bucket)

    # Test get_data on a nonexistent bucket
    with pytest.raises(ValueError):
        minio_adapter.get_data(test_key, nonexistent_bucket)

    # Test delete_data on a nonexistent bucket
    with pytest.raises(ValueError):
        minio_adapter.delete_data(test_key, nonexistent_bucket)

    # Test exists on a nonexistent bucket
    with pytest.raises(ValueError):
        minio_adapter.exists(test_key, nonexistent_bucket)

