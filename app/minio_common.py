import os
from typing import Tuple
from minio import Minio

bucket = os.environ.get('S3BUCKET_NAME', 'test')
endpoint = os.environ.get(f'S3BUCKET_PROVIDER_ENDPOINT')
access_key = os.environ.get(f'S3BUCKET_ACCESS_KEY')
secret_key = os.environ.get(f'S3BUCKET_SECRET_KEY')

def get_bucket() -> Tuple[Minio, str]:
    client = Minio(
        endpoint,
        secure=False,               # use http://
        access_key=access_key,
        secret_key=secret_key,
    )
    bucket_name = client.list_buckets()[0].name
    return client, bucket_name
