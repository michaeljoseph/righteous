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
    """
    Initialises righteous configuration

    :param account_defaults: Dictionary
    :param server_defaults: Dictionary
    :param debug: (optional) Boolean controlling debug output
    """
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

    :param username: (optional) String representing the username to login with
    :param password: (optional) String representing the password to login with
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

def list_servers(deployment_id=None):
    """
    Lists servers in a deployment

    Returns JSON

    :param deployment_id: (optional) String representing Deployment to list servers from
    """
    if not deployment_id:
        deployment_id = config.settings.default_deployment_id
    response = _request('%s/deployments/%s.js' % (config.settings.api_base, deployment_id))
    return simplejson.loads(response.content)


def find_server(nickname):
    """
    Finds a server based on nickname

    :param nickname: (optional) String representing the nickname of the server to lookup
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

    :param server_href: URL representing the server to retrieve information about
    :param nickname: (optional) String representing the nickname of the server
    """
    response = _request('%s.js' % _lookup_server(server_href, nickname))
    return simplejson.loads(response.content)

def server_settings(server_href, nickname=None):
    """
    Current server settings

    :param server_href: URL representing the server to query settngs from
    :param nickname: (optional) String representing the nickname of the server
    """
    response = _request('%s/settings.js' % _lookup_server(server_href, nickname))
    return simplejson.loads(response.content)

def start_server(server_href, nickname=None):
    """
    Starts a server.

    :param server_href: URL representing the server to start
    :param nickname: (optional) String representing the nickname of the server
    """
    return _request('%s/start' % _lookup_server(server_href, nickname), method='POST')

def stop_server(server_href, nickname=None):
    """
    Stops a server.

    :param server_href: URL representing the server to stop
    :param nickname: (optional) String representing the nickname of the server
    """
    return _request('%s/stop' % _lookup_server(server_href, nickname), method='POST').status_code == 201

def delete_server(server_href, nickname=None):
    """
    Deletes a server from RightScale

    :param server_href: URL representing the server to delete
    :param nickname: (optional) String representing the nickname of the server
    """
    return _request(_lookup_server(server_href, nickname), method='DELETE').status_code == 200

def create_server(nickname, defaults=None):
    """
    Create a server.

    :param nickname: String representing the nickname of the server
    :param defaults: (optional) Dictionary of server creation default properties
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

def _update_input_parameters(server_href, parameters):
    """
    Updates/sets any ServerTemplate parameters for a server

    :param server_url: URL representing the server to update
    :param parameters: Dictionary of ServerTemplate parameters to update
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
    response = _update_input_parameters(server_href, parameters)
    start_server_response = start_server(server_href)
    success = start_server_response.status_code == 201
    location = start_server_response.headers['location'] if success else None
    return success, location
