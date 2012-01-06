# coding: utf-8

"""
righteous.api


Implements the RightScale API for EC2 instance management.
http://support.rightscale.com/15-References/RightScale_API_Reference_Guide/02-Management/02-Servers
"""

import config
import sys, base64
import requests
from urllib import urlencode
try:
    import json as simplejson
except ImportError:
    import simplejson

def _debug(message):
    if config.settings.debug:
        config.settings.debug.write('%s\n' % message)

def _build_headers(headers={}):
    request_headers = {'X-API-VERSION': '1.0'}
    if headers:
        request_headers.update(headers)
    if config.settings.cookies:
        request_headers['Cookie'] = config.settings.cookies
    return request_headers

def _request(path, method='GET', body=None, headers={}):
    return requests.request(method, path, data=body, headers=_build_headers(headers=headers))

def init(account_defaults, server_defaults, debug=False):
    config.settings.api_base = 'https://my.rightscale.com/api/acct/%s' % account_defaults['account_id']
    config.settings.default_deployment_id = account_defaults['default_deployment_id']
    config.settings.debug = debug
    config.settings.account_defaults = account_defaults
    config.settings.server_defaults = server_defaults
    if config.settings.debug:
        requests.settings.verbose = sys.stderr
        config.settings.debug = sys.stderr
    if 'username' in account_defaults and 'password' in account_defaults:
        config.settings.username = account_defaults['username']
        config.settings.password = account_defaults['password']

def login(username=None, password=None):
    """
    Logins to RightScale and stores the auth cookie for future requests
    """
    if not username or not password:
        username = config.settings.username
        password = config.settings.password

    if not username or not password:
        raise Exception('Username and password not specified in configuration or on the command line')
    response = _request('%s/login' % config.settings.api_base, headers={'Authorization':"Basic %s" % base64.encodestring('%s:%s' % (username, password))[:-1]})
    if response.status_code == 204:
        config.settings.cookies = response.headers['set-cookie']
        return True
    return False

def list_deployment_servers(deployment_id=None):
    """
    Lists servers in a deployment
    """
    if not deployment_id:
        deployment_id = config.settings.default_deployment_id
    response = _request('%s/deployments/%s.js' % (config.settings.api_base, deployment_id))
    return simplejson.loads(response.content)


def find_server(nickname):
    """
    Finds a server based on nickname
    """
    response = _request('%s/servers.js?filter=nickname=%s' % (config.settings.api_base, nickname))
    servers = simplejson.loads(response.content)
    return servers[0] if len(servers) else None


def _lookup_server(server_href, nickname):
    if not nickname and not server_href:
        raise ValueError('Either nickname or server_href must be specified')

    if server_href:
        return server_href
    elif nickname:
        return find_server(nickname)['href']

def server_info(server_href, nickname=None):
    """
    Detailed server information
    """
    response = _request('%s.js' % _lookup_server(server_href, nickname))
    return simplejson.loads(response.content)

def server_settings(server_href, nickname=None):
    """
    Current server settings
    """
    response = _request('%s/settings.js' % _lookup_server(server_href, nickname))
    return simplejson.loads(response.content)

def start_server(server_href, nickname=None):
    """
    Starts a server.
    """
    return _request('%s/start' % _lookup_server(server_href, nickname), method='POST')

def stop_server(server_href, nickname=None):
    """
    Stops a server.
    """
    return _request('%s/stop' % _lookup_server(server_href, nickname), method='POST').status_code == 201

def delete_server(server_href, nickname=None):
    """
    Deletes a server from RightScale
    """
    return _request(_lookup_server(server_href, nickname), method='DELETE').status_code == 200

def create_server(nickname, defaults=None):
    """
    Create a server.

    Args:
        nickname (str): the nickname of the server
        defaults (dict): server defaults
    """
    if not defaults:
        defaults = config.settings.server_defaults
    create_data = {'server[nickname]' : nickname}
    for key, value in defaults.items():
        create_data['server[%s]' % key] = value
    response = _request('%s/servers' % config.settings.api_base, method='POST', body=urlencode(create_data))
    location = response.headers['location']
    _debug('Created %s: %s' % (nickname, location))
    return location

def update_input_parameters(server_href, parameters):
    """
    Updates/sets any ServerTemplate parameters for a server

    Args:
        server_href (url): the server reference url
        parameters (dict): ServerTemplate parameters
    """
    input_data = []
    for key,value in parameters.items():
        input_data.append('server[parameters][%s]=text:%s' % (key.upper(), value))
    update = '&'.join(input_data)
    return _request('%s' % server_href, method='PUT', body=update, headers={'Content-Type': 'application/x-www-form-urlencoded'})

def create_and_start_server(nickname, parameters):#defaults, parameters):
    """Creates and starts a server.
    Returns a tuple of operation status, href of the created, started server

    :param nickname: String representing the nickname of the server
    :param defaults: Dictionary of server creation default properties
    :param parameters: Dictionary of ServerTemplate parameters
    """
    server_href = create_server(nickname)#, defaults)
    response = update_input_parameters(server_href, parameters)
    start_server_response = start_server(server_href)
    success = start_server_response.status_code == 201
    location = start_server_response.headers['location'] if success else None
    return success, location
