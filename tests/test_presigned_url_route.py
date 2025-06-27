from fastapi import status
from fastapi.testclient import TestClient
from requests.auth import HTTPBasicAuth
from minio.error import S3Error

from app import app
from app import security
from app.model import PresignedUrlResponse

client = TestClient(app)

USER = 'example.user'
PASSWORD = 'test'
BUCKET = 'test_bucket'
FILENAME = 'file.txt'


def test_get_presigned_url_ok_default_expiration(mocker):

    # GIVEN
    minio_mock = mocker.patch('app.presigned_url.minio_common.Minio')
    minio_mock.return_value.presigned_get_object.return_value = "http://new-presigned-url"

    auth = HTTPBasicAuth(username=USER, password=PASSWORD)
    security.BASIC_AUTH_CONFIG_DIR = 'tests/samples/test-basic-auth-user-data'

    expected_response = PresignedUrlResponse(
        status='URL retrieved successfully',
        expiration_hours=7*24,
        url='https://new-presigned-url'
    )

    # WHEN
    response = client.post(
        '/get-presigned-url',
        auth=auth,
        data={'filename': FILENAME}
    )

    # THEN
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == expected_response


def test_get_presigned_url_ok_nondefault_expiration(mocker):

    # GIVEN
    minio_mock = mocker.patch('app.presigned_url.minio_common.Minio')
    minio_mock.return_value.presigned_get_object.return_value = "http://new-presigned-url"

    auth = HTTPBasicAuth(username=USER, password=PASSWORD)
    security.BASIC_AUTH_CONFIG_DIR = 'tests/samples/test-basic-auth-user-data'

    expected_response = PresignedUrlResponse(
        status='URL retrieved successfully',
        expiration_hours=48,
        url='https://new-presigned-url'
    )

    # WHEN
    response = client.post(
        '/get-presigned-url',
        auth=auth,
        data={'filename': FILENAME, 'expiration_hours': 48}
    )

    # THEN
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == expected_response


def test_get_presigned_url_user_not_authorized(mocker):
    # GIVEN
    auth = HTTPBasicAuth(username='other', password=PASSWORD)
    security.BASIC_AUTH_CONFIG_DIR = 'tests/samples/test-basic-auth-user-data'

    # WHEN
    response = client.post(
        '/get-presigned-url',
        auth=auth,
        data={'filename': FILENAME}
    )

    # THEN
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Login required'}
    assert response.headers['WWW-Authenticate'] == 'Basic'


def test_get_presigned_url_password_incorrect(mocker):
    # GIVEN
    auth = HTTPBasicAuth(username=USER, password='wrong')
    security.BASIC_AUTH_CONFIG_DIR = 'tests/samples/test-basic-auth-user-data'

    # WHEN
    response = client.post(
        '/get-presigned-url',
        auth=auth,
        data={'filename': FILENAME}
    )

    # THEN
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Login required'}
    assert response.headers['WWW-Authenticate'] == 'Basic'


def test_get_presigned_url_value_error(mocker):
    # GIVEN
    put_mock = mocker.patch('app.presigned_url.get_presigned_url')
    put_mock.side_effect = ValueError('error')

    auth = HTTPBasicAuth(username=USER, password=PASSWORD)
    security.BASIC_AUTH_CONFIG_DIR = 'tests/samples/test-basic-auth-user-data'

    expected_response = PresignedUrlResponse(
        status='ValueError on creating presigned URL: error',
        expiration_hours=7*24,
        url=None
    )

    # WHEN
    response = client.post(
        '/get-presigned-url',
        auth=auth,
        data={'filename': FILENAME}
    )

    # THEN
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {'detail': expected_response.dict()}


def test_get_presigned_url_internal_error(mocker):
    # GIVEN
    put_mock = mocker.patch('app.presigned_url.get_presigned_url')
    put_mock.side_effect = Exception()

    auth = HTTPBasicAuth(username=USER, password=PASSWORD)
    security.BASIC_AUTH_CONFIG_DIR = 'tests/samples/test-basic-auth-user-data'

    expected_response = PresignedUrlResponse(
        status='Internal error',
        expiration_hours=7*24,
        url=None
    )

    # WHEN
    response = client.post(
        '/get-presigned-url',
        auth=auth,
        data={'filename': FILENAME}
    )

    # THEN
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {'detail': expected_response.dict()}
