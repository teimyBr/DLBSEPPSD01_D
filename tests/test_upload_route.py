from fastapi import status
from fastapi.testclient import TestClient
from requests.auth import HTTPBasicAuth
from minio.error import S3Error

from app import app
from app import security
from app.model import UploadResponse

client = TestClient(app)

USER = 'example.user'
PASSWORD = 'test'
PREFIX = 'folder/'
FILENAME = 'file.txt'


def test_upload_ok(tmp_path, mocker):
    # GIVEN
    mocker.patch('app.upload.minio_common.Minio')

    path = tmp_path / FILENAME
    path.write_bytes(b'test')

    auth = HTTPBasicAuth(username=USER, password=PASSWORD)
    security.BASIC_AUTH_CONFIG_DIR = 'tests/samples/test-basic-auth-user-data'

    expected_response = UploadResponse(
        status='Upload successful',
        file=f'{PREFIX}{FILENAME}'
    )

    # WHEN
    with path.open('rb') as file:
        response = client.post(
            '/upload',
            auth=auth,
            data={'prefix': PREFIX},
            files={'file': file}
        )

    # THEN
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == expected_response


def test_upload_no_prefix(tmp_path, mocker):
    # GIVEN
    mocker.patch('app.upload.minio_common.Minio')

    path = tmp_path / FILENAME
    path.write_bytes(b'test')

    auth = HTTPBasicAuth(username=USER, password=PASSWORD)
    security.BASIC_AUTH_CONFIG_DIR = 'tests/samples/test-basic-auth-user-data'

    expected_response = UploadResponse(
        status='Upload successful',
        file=f'{FILENAME}'
    )

    # WHEN
    with path.open('rb') as file:
        response = client.post(
            '/upload',
            auth=auth,
            files={'file': file}
        )

    # THEN
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == expected_response


def test_upload_user_not_authorized(tmp_path, mocker):
    # GIVEN
    path = tmp_path / FILENAME
    path.write_bytes(b'test')

    auth = HTTPBasicAuth(username='other', password=PASSWORD)
    security.BASIC_AUTH_CONFIG_DIR = 'tests/samples/test-basic-auth-user-data'

    # WHEN
    with path.open('rb') as file:
        response = client.post(
            '/upload',
            auth=auth,
            files={'file': file}
        )

    # THEN
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Login required'}
    assert response.headers['WWW-Authenticate'] == 'Basic'


def test_upload_password_incorrect(tmp_path, mocker):
    # GIVEN
    path = tmp_path / FILENAME
    path.write_bytes(b'test')

    auth = HTTPBasicAuth(username=USER, password='wrong')
    security.BASIC_AUTH_CONFIG_DIR = 'tests/samples/test-basic-auth-user-data'

    # WHEN
    with path.open('rb') as file:
        response = client.post(
            '/upload',
            auth=auth,
            files={'file': file}
        )

    # THEN
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Login required'}
    assert response.headers['WWW-Authenticate'] == 'Basic'


def test_upload_internal_error(tmp_path, mocker):
    # GIVEN
    put_mock = mocker.patch('app.upload.put_file_to_bucket')
    put_mock.side_effect = Exception()

    path = tmp_path / FILENAME
    path.write_bytes(b'test')

    auth = HTTPBasicAuth(username=USER, password=PASSWORD)
    security.BASIC_AUTH_CONFIG_DIR = 'tests/samples/test-basic-auth-user-data'

    expected_response = UploadResponse(
        status='Internal error',
        file=f'{PREFIX}{FILENAME}'
    )

    # WHEN
    with path.open('rb') as file:
        response = client.post(
            '/upload',
            auth=auth,
            data={'prefix': PREFIX},
            files={'file': file}
        )

    # THEN
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert response.json() == {'detail': expected_response.dict()}
