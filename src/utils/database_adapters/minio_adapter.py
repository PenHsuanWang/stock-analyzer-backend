# utils/database_adapters/minio_adapter.py

from minio import Minio
from minio.error import S3Error
from io import BytesIO
from utils.database_adapters.base import AbstractDatabaseAdapter


class MinIOAdapter(AbstractDatabaseAdapter):
    def __init__(self, endpoint, access_key, secret_key, secure=True):
        """
        Initialize the MinIO client.
        :param endpoint: MinIO server URL.
        :param access_key: Access key for MinIO.
        :param secret_key: Secret key for MinIO.
        :param secure: Flag to indicate if the connection is secure (HTTPS).
        """
        self.client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)

    def set_data(self, key: str, value, bucket: str):
        """
        Store data in MinIO bucket.

        :param key: The object name under which the data should be stored.
        :param value: The data to store. It can be a string or bytes.
        :param bucket: The name of the bucket.
        """
        if isinstance(value, str):
            value = value.encode('utf-8')
        elif not isinstance(value, bytes):
            raise ValueError("Value must be a string or bytes")

        try:
            value_stream = BytesIO(value)
            self.client.put_object(bucket, key, value_stream, length=len(value))
        except S3Error as e:
            if e.code == 'NoSuchBucket':
                raise ValueError(f"Bucket '{bucket}' does not exist")
            raise

    def get_data(self, key: str, bucket: str) -> bytes:
        """
        Retrieve data from MinIO bucket.

        :param key: The object name of the data to retrieve.
        :param bucket: The name of the bucket.
        :return: The data as bytes.
        """
        try:
            response = self.client.get_object(bucket, key)
            return response.read()
        except S3Error as e:
            if e.code == 'NoSuchBucket':
                raise ValueError(f"Bucket '{bucket}' does not exist")
            return None

    def delete_data(self, key: str, bucket: str) -> bool:
        """
        Delete data from MinIO bucket.

        :param key: The object name of the data to delete.
        :param bucket: The name of the bucket.
        :return: True if deletion was successful, False otherwise.
        """
        try:
            self.client.remove_object(bucket, key)
            return True
        except S3Error as e:
            if e.code == 'NoSuchBucket':
                raise ValueError(f"Bucket '{bucket}' does not exist")
            return False

    def exists(self, key: str, bucket: str) -> bool:
        """
        Check if an object exists in MinIO bucket.

        :param key: The object name to check.
        :param bucket: The name of the bucket.
        :return: True if the object exists, False otherwise.
        """
        try:
            self.client.stat_object(bucket, key)
            return True
        except S3Error as e:
            if e.code == 'NoSuchBucket':
                raise ValueError(f"Bucket '{bucket}' does not exist")
            return False

    def keys(self, bucket: str, prefix: str = None, recursive: bool = False) -> list:
        """
        Retrieve a list of object names from MinIO bucket matching a prefix.

        :param bucket: The name of the bucket.
        :param prefix: The prefix to match.
        :param recursive: Flag to indicate if the search should be recursive.
        :return: A list of object names.
        """
        try:
            objects = self.client.list_objects(bucket, prefix=prefix, recursive=recursive)
            return [obj.object_name for obj in objects]
        except S3Error as e:
            if e.code == 'NoSuchBucket':
                raise ValueError(f"Bucket '{bucket}' does not exist")
            raise
