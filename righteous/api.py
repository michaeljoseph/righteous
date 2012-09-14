# coding: utf-8

"""
righteous.api

Implements the RightScale API for EC2 instance management.
"""

from . import config
import re
import sys
import base64
# HACK: to allow setup.py to import __version__ from righteous/__init__.py
try:
    import requests
    import omnijson as json
except ImportError:
    pass
from urllib import urlencode
from logging import getLogger
log = getLogger(__name__)

ACCOUNT_URL = 'https://my.rightscale.com/api/acct/'


def debug(message, *args):
    log.debug(message, *args)
    if config.settings.debug:
        config.settings.debug.write('%s\n' % (message % args))


def _build_headers(headers=None):
    request_headers = {'X-API-VERSION': '1.0'}
    if headers:
        request_headers.update(headers)
    if config.settings.cookies:
        request_headers['Cookie'] = config.settings.cookies
    return request_headers


def _request(path, method='GET', body=None, headers={}, prepend_api_base=True):
    if prepend_api_base:
        path = ACCOUNT_URL + config.settings.account_id + path
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
    config.settings.api_base = ACCOUNT_URL + account_id

    config.settings.default_deployment_id = kwargs.get(
        'default_deployment_id', None)
    config.settings.debug = kwargs.get('debug', False)

    config.settings.create_server_parameters = {}
    for key, value in kwargs.items():
        config.settings.create_server_parameters[key] = value
        if key == 'default_deployment_id':
            href = '%s%s/deployments/%s' % (ACCOUNT_URL, account_id,
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


def list_servers(deployment_id=None):
    """
    Lists servers in a deployment

    Returns JSON

    :param deployment_id: (optional) String representing Deployment to list
                          servers from
    """
    if not deployment_id:
        deployment_id = config.settings.default_deployment_id

    if not deployment_id:
        raise Exception('Deployment id not specified in configuration or as '
            'an API parameter')

    response = _request('/deployments/%s.js' % deployment_id)
    return json.loads(response.content)


def find_server(nickname):
    """
    Finds a server based on nickname

    :param nickname: (optional) String representing the nickname of the server
                     to lookup
    """
    response = _request('/servers.js?filter=nickname=%s' % nickname)

    servers = json.loads(response.content)
    return servers[0] if len(servers) else None


def _lookup_server(server_href, nickname):
    if not nickname and not server_href:
        raise ValueError('Either nickname or server_href must be specified')

    if server_href:
        return server_href
    elif nickname:
        server = find_server(nickname)
        if server and 'href' in server:
            return server['href']
        else:
            raise Exception('No environment named %s found' % nickname)


def server_info(server_href, nickname=None):
    """
    Detailed server information

    :param server_href: URL representing the server to query
    :param nickname: (optional) String representing the nickname of the server
    """
    response = _request('%s.js' %
        _lookup_server(server_href, nickname), prepend_api_base=False)
    return json.loads(response.content)


def server_settings(server_href, nickname=None):
    """
    Current server settings

    :param server_href: URL representing the server to query settngs from
    :param nickname: (optional) String representing the nickname of the server
    """
    response = _request('%s/settings.js' %
        _lookup_server(server_href, nickname), prepend_api_base=False)
    return json.loads(response.content)


def start_server(server_href, nickname=None):
    """
    Starts a server.

    :param server_href: URL representing the server to start
    :param nickname: (optional) String representing the nickname of the server
    """
    return _request('%s/start' %
        _lookup_server(server_href, nickname), method='POST',
        prepend_api_base=False)


def stop_server(server_href, nickname=None):
    """
    Stops a server.

    :param server_href: URL representing the server to stop
    :param nickname: (optional) String representing the nickname of the server
    """
    return _request('%s/stop' %
        _lookup_server(server_href, nickname), method='POST',
        prepend_api_base=False).status_code == 201


def delete_server(server_href, nickname=None):
    """
    Deletes a server from RightScale

    :param server_href: URL representing the server to delete
    :param nickname: (optional) String representing the nickname of the server
    """
    return _request(_lookup_server(server_href, nickname),
        method='DELETE', prepend_api_base=False).status_code == 200


def create_server(nickname, instance_type, create_server_parameters=None):
    """
    Create a server.

    :param nickname: String representing the nickname of the server
    :param instance_type: String of the EC2 instance type
    :param create_server_parameters: (optional) Dictionary of
                                     server creation parameters
    """
    if not create_server_parameters:
        create_server_parameters = config.settings.create_server_parameters

    create_data = {'server[nickname]': nickname}

    # TODO: error if no instance type key exists
    instance_server_href = create_server_parameters[instance_type]
    create_server_parameters = dict((k, v) for k, v in
        create_server_parameters.items() if not k.startswith('m1'))

    for key, value in create_server_parameters.items():
        create_data['server[%s]' % key] = value
    create_data['server[server_template_href]'] = instance_server_href

    response = _request('/servers', method='POST', body=urlencode(create_data))
    location = response.headers.get('location')
    debug('Created %s: %s (%s:%s)' % (nickname, location,
        response.status_code, response.content))
    # TODO: error responses
    return location


def set_server_parameters(server_href, parameters):
    """
    Updates/sets any ServerTemplate parameters for a server

    :param server_url: URL representing the server to update
    :param parameters: Dictionary of ServerTemplate parameters to set
    """
    input_data = []
    for key, value in parameters.items():
        input_data.append('server[parameters][%s]=text:%s'
            % (key.upper(), value))
    update = '&'.join(input_data)
    return _request(server_href, method='PUT', body=update,
        headers={'Content-Type': 'application/x-www-form-urlencoded'},
        prepend_api_base=False)


def create_and_start_server(nickname, instance_type,
        create_server_parameters=None, server_template_parameters=None):
    """Creates and starts a server.
    Returns a tuple of operation status, href of the created, started server

    :param nickname: String representing the nickname of the server
    :param instance_type: String of the EC2 instance type
    :param create_server_parameters: (optional) Dictionary of
                                     server creation parameters
    :param server_template_parameters: (optional) Dictionary of
                                       ServerTemplate parameters
    """
    server_href = create_server(nickname, instance_type,
        create_server_parameters)

    if server_href:
        location = None
        if server_template_parameters:
            set_server_parameters(server_href, server_template_parameters)

        start_server_response = start_server(server_href)
        success = start_server_response.status_code == 201
        if success:
            location = start_server_response.headers['location']
        else:
            debug('Start server %s failed with %s' % (server_href,
                start_server_response.content))

        return success, location
    else:
        return False, None


def list_server_templates():
    """Lists ServerTemplates

    Returns JSON
    """
    response = _request('/server_templates.js')
    return json.loads(response.content)


def _extract_template_id(template_href):
    """
    Returns the template id from an href

    :param template_href: String representing the server template
                          href
    """
    result = re.match(ACCOUNT_URL + config.settings.account_id +
                      '/ec2_server_templates/(\d+)',
                      template_href)
    if result:
        return result.groups()[0]
    return None


def server_template_info(template_href):
    """Details ServerTemplate information

    Returns JSON

    :param template_href: String representing the server template
                          href
    """
    response = _request('/server_templates/%s.js' %
                        _extract_template_id(template_href))
    template = json.loads(response.content)
    if template:
        return template
    else:
        return None


def create_server_template(nickname, description, multi_cloud_image_href):
    """Create a new ServerTemplate

    Returns a tuple of operation status, href of the created, started server

    :param nickname: String of the template nickname
    :param description: String describing the ServerTemplate
    :param multi_cloud_image_href: String of the template image href
    """
    location = None
    success = False
    create_data = {
        'server_template[nickname]': nickname,
        'server_template[description]': description,
        'server_template[multi_cloud_image_href]': multi_cloud_image_href,
    }

    response = _request('/server_templates', method='POST',
                        body=urlencode(create_data))
    success = response.status_code == 201
    if success:
        location = response.headers.get('location')
        debug('Created ServerTemplate %s: %s (%s:%s)' % (nickname, location,
            response.status_code, response.content))
    # TODO: error responses
    return success, location


def delete_server_template(server_template_href):
    """Deletes a ServerTemplate

    :param server_template_href: String of the ServerTemplate to delete
    """
    return _request('/server_templates/%s.js' %
                    _extract_template_id(server_template_href),
                    method='DELETE').status_code == 200
