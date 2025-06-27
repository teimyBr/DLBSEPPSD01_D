import logging
from minio import Minio
from datetime import timedelta

from . import minio_common


def get_presigned_url(
        filename: str,
        expiration: timedelta) -> str:
    client, bucket_name = minio_common.get_bucket()

    try:
        url = client.presigned_get_object(
            bucket_name,
            filename,
            expiration,
        ).replace("http", "https", 1)
        logging.info(f'Successfully created presigned URL "{url}" '
                     f'for file "{filename}"')
        return url
    except:
        logging.error(
            f'Failed to create presigned URL '
            f'for file "{filename}"', exc_info=True)
        raise
