import logging
import tempfile
from minio import Minio

from . import minio_common

PART_SIZE = 10 * 1024 * 1024  # x MiB


def put_file_to_bucket(
        prefix: str,
        filename: str,
        file: tempfile.SpooledTemporaryFile,
        content_type: str):
    client, bucket_name = minio_common.get_bucket()

    # Use put instead of fput with fileno() to avoid "bad file descriptor" errors
    try:
        resp = client.put_object(
            bucket_name,
            f'{prefix}{filename}',
            file,
            -1,
            part_size=PART_SIZE,
            content_type=content_type
        )
        logging.info(f'Successfully upload file {prefix}{filename} with content_type: {content_type}')
        return resp
    except:
        logging.error(
            f'Failed to upload file {prefix}{filename}', exc_info=True)
        raise
