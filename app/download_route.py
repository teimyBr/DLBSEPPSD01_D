import logging

from fastapi import Depends, APIRouter, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from minio import S3Error
from starlette.responses import StreamingResponse
from urllib3 import HTTPResponse

from . import minio_common
from . import security

CHUNK_SIZE = 10 * 1024 * 1024

router = APIRouter()
api_security = HTTPBasic()


@router.get('/data/{file_path:path}')
def bucket_download(file_path: str, credentials: HTTPBasicCredentials = Depends(api_security)):
    '''
    Download a file from a S3 Bucket.
    '''

    security.check_credentials(credentials)
    client, bucket_name = minio_common.get_bucket()

    try:
        s3_response = client.get_object(bucket_name, file_path)
        headers = {
            'Content-Type': s3_response.getheader('Content-Type'),
            'Content-Length': s3_response.getheader('Content-Length')
        }

        return StreamingResponse(read_s3_response(s3_response), status_code=s3_response.status, headers=headers)
    except S3Error as s3_error:
        logging.error(f'S3 error occurred: {s3_error.message}', exc_info=True)
        raise HTTPException(status_code=s3_error.response.status, detail=s3_error.message)
    except Exception as e:
        logging.error(f'Internal error: {str(e)}', exc_info=True)
        raise HTTPException(status_code=500, detail="Internal error")

async def read_s3_response(s3_response: HTTPResponse):
    try:
        while True:
            data = s3_response.read(CHUNK_SIZE)
            if not data:
                break
            yield data
    finally:
        s3_response.close()
        s3_response.release_conn()
