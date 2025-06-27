import logging
from fastapi import Depends, APIRouter, File, Form, UploadFile, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from . import upload
from . import security
from . import util
from .model import UploadResponse

router = APIRouter()
api_security = HTTPBasic()


@router.post(
    '/upload',
    response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
def bucket_upload(
        credentials: HTTPBasicCredentials = Depends(api_security),
        prefix: str = Form(''),
        file: UploadFile = File(...)):
    '''
    Upload a file to an S3 Bucket. Prefix will be added before the filename if
    specified (e.g. 'foldername/').
    '''

    security.check_credentials(credentials)

    resp = UploadResponse(
        status='Upload successful',
        bucket='',
        file=f'{prefix}{file.filename}'
    )

    try:
        s3_resp = upload.put_file_to_bucket(
            prefix, file.filename, file.file, file.content_type)
        resp.bucket = s3_resp.bucket_name
        return resp
    except:
        logging.error(f'Internal error', exc_info=True)
        resp.status = f'Internal error'
        util.raise_http_exception(status.HTTP_500_INTERNAL_SERVER_ERROR, resp)
