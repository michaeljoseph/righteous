import omnijson as json
from urllib import urlencode, quote
from .base import _request, debug, lookup_by_href_or_nickname
from .. import config


def _lookup_server(server_href, nickname):
    """
    Convenience wrapper around `righteous.base.lookup_by_href_or_nickname`
    """
    return lookup_by_href_or_nickname(server_href, nickname, find_server)


def list_servers(deployment_id=None):
    """
    Lists servers in a deployment

    :param deployment_id: (optional) String representing Deployment to list
                          servers from
    :return: dict of server deployment information:
        http://reference.rightscale.com/api1.0/ApiR1V0/Docs/ApiDeployments.html
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
    :return: dict of server information with the following keys:

    ::

        [u'deployment_href', u'tags', u'created_at', u'server_type',
         u'updated_at', u'server_template_href', u'current_instance_href',
         u'state', u'href', u'nickname']
    """
    response = _request('/servers.js?filter=nickname=%s' % quote(nickname))

    servers = json.loads(response.content)
    return servers[0] if len(servers) else None


def server_info(server_href, nickname=None):
    """
    Detailed server information

    :param server_href: URL representing the server to query
    :param nickname: (optional) String representing the nickname of the server
    :return: dict of server information with the following keys:

    ::

        [u'deployment_href', u'parameters', u'tags', u'created_at',
         u'server_type', u'updated_at', u'server_template_href',
         u'current_instance_href', u'state', u'href', u'nickname']
    """
    response = _request('%s.js' %
        _lookup_server(server_href, nickname), prepend_api_base=False)
    return json.loads(response.content)


def server_settings(server_href, nickname=None):
    """
    Current server settings

    :param server_href: URL representing the server to query settings from
    :param nickname: (optional) String representing the nickname of the server
    :return: dict of server settings with the following keys:

    ::

       [u'ec2-security-groups-href', u'private-ip-address',
        u'ec2-ssh-key-href', u'private-dns-name', u'locked', u'dns-name',
        u'pricing', u'cloud_id', u'ec2-availability-zone', u'aws-platform',
        u'ip-address', u'aws-product-codes', u'aws-id', u'ec2-instance-type',
        u'launched-by']
    """
    response = _request('%s/settings.js' %
        _lookup_server(server_href, nickname), prepend_api_base=False)
    return json.loads(response.content)


def start_server(server_href, nickname=None):
    """
    Starts a server.

    :param server_href: URL representing the server to start
    :param nickname: (optional) String representing the nickname of the server
    :return: `requests.Response`
    """
    return _request('%s/start' %
        _lookup_server(server_href, nickname), method='POST',
        prepend_api_base=False)


def stop_server(server_href, nickname=None):
    """
    Stops a server.

    :param server_href: URL representing the server to stop
    :param nickname: (optional) String representing the nickname of the server
    :return: `requests.Response`
    """
    return _request('%s/stop' %
        _lookup_server(server_href, nickname), method='POST',
        prepend_api_base=False).status_code == 201


def delete_server(server_href, nickname=None):
    """
    Deletes a server from RightScale

    :param server_href: URL representing the server to delete
    :param nickname: (optional) String representing the nickname of the server
    :return: Boolean of operation success/failure
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
    :return: server href of the new server
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
    debug('Created server %s: %s (%s:%s)' % (nickname, location,
        response.status_code, response.content))
    # TODO: error responses
    return location


def set_server_parameters(server_href, parameters):
    """
    Updates/sets any ServerTemplate parameters for a server

    :param server_url: URL representing the server to update
    :param parameters: Dictionary of ServerTemplate parameters to set
    :return: `requests.Response`
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
    """
    Creates and starts a server.
    Returns a tuple of operation status, href of the created, started server

    :param nickname: String representing the nickname of the server
    :param instance_type: String of the EC2 instance type
    :param create_server_parameters: (optional) Dictionary of
                                     server creation parameters
    :param server_template_parameters: (optional) Dictionary of
                                       ServerTemplate parameters
    :return: tuple of operation success and server href of the new instance
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
