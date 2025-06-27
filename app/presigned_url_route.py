import logging
from fastapi import Depends, APIRouter, Form, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from datetime import timedelta

from . import presigned_url
from . import security
from . import util
from .model import PresignedUrlResponse

router = APIRouter()
api_security = HTTPBasic()

EXPIRATION_DEFAULT = 7 * 24  # 7 days


@router.post(
    '/get-presigned-url', response_model=PresignedUrlResponse,
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_400_BAD_REQUEST: {'model': PresignedUrlResponse}})
def presigned_url_route(
        credentials: HTTPBasicCredentials = Depends(api_security),
        filename: str = Form(...),
        expiration_hours: int = Form(EXPIRATION_DEFAULT)):
    """
    Create a presigned URL for downloading the given file from the S3 Bucket,
    with the optionally provided expiry time (default 7 days).
    """

    security.check_credentials(credentials)

    resp = PresignedUrlResponse(
        status='URL retrieved successfully',
        expiration_hours=expiration_hours
    )

    expiration_delta = timedelta(hours=expiration_hours)

    try:
        result_url = presigned_url.get_presigned_url(
            filename, expiration_delta)
        resp.url = result_url
        return resp
    except ValueError as e:
        resp.status = f'ValueError on creating presigned URL: {e}'
        util.raise_http_exception(status.HTTP_400_BAD_REQUEST, resp)
    except:
        logging.error(f'Internal error', exc_info=True)
        resp.status = f'Internal error'
        util.raise_http_exception(status.HTTP_500_INTERNAL_SERVER_ERROR, resp)
