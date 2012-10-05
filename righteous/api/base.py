# coding: utf-8

"""
righteous.api

Implements the RightScale API for EC2 instance management.
"""

from .. import config
import sys
import base64
# HACK: to allow setup.py to import __version__ from righteous/__init__.py
try:
    import requests
except ImportError:
    pass
from logging import getLogger
log = getLogger(__name__)


def debug(message, *args):
    """
    Logs debug messages
    """
    log.debug(message, *args)
    if config.settings.debug:
        config.settings.debug.write('%s\n' % (message % args))


def _build_headers(headers=None):
    """
    Internal helper to build request headers
    """
    request_headers = {'X-API-VERSION': '1.0'}
    if headers:
        request_headers.update(headers)
    if config.settings.cookies:
        request_headers['Cookie'] = config.settings.cookies
    return request_headers


def _request(path, method='GET', body=None, headers={}, prepend_api_base=True):
    """
    Internal method to make API requests
    """
    if prepend_api_base:
        path = config.account_url + config.settings.account_id + path
    headers = _build_headers(headers=headers)
    debug('%s to %s with data=%s, headers=%s', method, path, body, headers)
    return requests.request(method, path, data=body, headers=headers,
        config=config.settings.requests_config or {})


def init(username, password, account_id, **kwargs):
    """
    Initialises righteous configuration

    :param username: String of a Rightscale username
    :param password: String of the user's password
    :param account_id: String of the Rightscale account_id
    :params kwargs: Key word arguments for additional configuration
    """

    if not username or not password or not account_id:
        raise Exception('Username, password and account_id are '
            'required parameters')

    config.settings.username = username
    config.settings.password = password
    config.settings.account_id = account_id
    config.settings.api_base = config.account_url + account_id

    config.settings.default_deployment_id = kwargs.get(
        'default_deployment_id', None)
    config.settings.debug = kwargs.get('debug', False)

    config.settings.create_server_parameters = {}
    for key, value in kwargs.items():
        config.settings.create_server_parameters[key] = value
        if key == 'default_deployment_id':
            href = '%s%s/deployments/%s' % (config.account_url, account_id,
                config.settings.default_deployment_id)
            config.settings.create_server_parameters['deployment_href'] = href

    if config.settings.debug:
        config.settings.requests_config = {'verbose': sys.stderr}
        config.settings.debug = sys.stderr


def login(username=None, password=None, account_id=None):
    """
    Logins to RightScale and stores the auth cookie for future requests

    :param username: (optional) String representing the username to login with
    :param password: (optional) String representing the password to login with
    :param account_id: (optional) String of the Rightscale account_id
    :return: Boolean indicating successful login
    """
    if not username or not password or not account_id:
        username = config.settings.username
        password = config.settings.password
        account_id = config.settings.account_id

    if not username or not password or not account_id:
        raise Exception('Username, password or account_id not specified in '
            'configuration or as an API parameter')

    auth_hash = '%s:%s' % (username, password)
    response = _request('/login', headers={
        'Authorization': 'Basic %s' % base64.encodestring(auth_hash)[:-1]
    })

    if response.status_code == 204:
        config.settings.cookies = response.headers['set-cookie']
        config.settings.username = username
        config.settings.password = password
        return True

    return False
