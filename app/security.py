import logging
import os
import secrets

from fastapi import HTTPException, status
from fastapi.security import HTTPBasicCredentials

BASIC_AUTH_CONFIG_DIR = '/etc/basic-auth-user-data'


def check_credentials(credentials: HTTPBasicCredentials):
    password = get_password_for_user(credentials.username)
    if password == None:
        logging.debug(f'No credentials found for {credentials.username}')
        deny()
    if not secrets.compare_digest(credentials.password, password):
        logging.debug(f'Password incorrect for {credentials.username}')
        deny()


def deny():
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Login required',
        headers={'WWW-Authenticate': 'Basic'},
    )


def get_password_for_user(username: str):
    if os.path.isdir(BASIC_AUTH_CONFIG_DIR):
        user_db_file = BASIC_AUTH_CONFIG_DIR
    else:
        logging.warning('No basic auth config found - aborting.')
        deny()
    known_users = read_users_from_files(user_db_file)
    logging.debug(f'Known users: {known_users}')
    return known_users.get(username, None)


def read_users_from_files(dirname: str):
    """
    Scan the given directory for files and parse those into username / password pairs which are returned
    as a dict. The username is the filename and the password the file content (stripped of whitespace).
    """
    def read_password_from_file(filename: str):
        with open(filename, 'r') as user_file:
            return user_file.read().strip()
    return {
        filename: read_password_from_file(os.path.join(dirname, filename))
        for filename in [
            filename for filename in os.listdir(dirname)
            if os.path.isfile(os.path.join(dirname, filename))
        ]
    }
