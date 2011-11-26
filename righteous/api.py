import httplib2
from urllib import urlencode
import base64
from uuid import uuid4
try:
    import json as simplejson
except ImportError:
    import simplejson

# TODO: turn this into functions
class RightScaleClient:
    """
    Implements the RightScale API for EC2 instance management.
    http://support.rightscale.com/15-References/RightScale_API_Reference_Guide/02-Management/02-Servers
    """

    def __init__(self, username, password, account_id, debug=False):
        """
        Create an instance of the RightScale Client

        Args:
            username (str): rightscale username
            password (str): rightscale password
            account_id (str): rightscale account number

        Kwargs:
            debug (bool): output debug information
        """
        self.account_id = account_id
        self.username = username
        self.password = password

        self.api_base = 'https://my.rightscale.com/api/acct/%s' % account_id
        self.h = httplib2.Http(".cache")
        self.cookies = None
        self.debug = debug
        self.authenticated = self.login()

    def _headers(self, extra={}):
        h = {'X-API-VERSION': '1.0'}
        if extra:
            h.update(extra)
        if self.cookies:
            h['Cookie'] =  self.cookies
        return h

    def _request(self, path, method='GET', body=None, extra_headers={}):
        headers = self._headers(extra=extra_headers)
        response, content = self.h.request(path, method=method, body=body, headers=headers)
        if self.debug:
            print '%s %s' % (method, path)
            print response, content
        return response, content

    def login(self):
        """
        Logins to RightScale and stores the auth cookie for future requests
        """
        response, content = self._request('%s/login' % self.api_base, extra_headers={'Authorization':"Basic %s" % base64.encodestring('%s:%s' % (self.username, self.password))[:-1]})
        if response['status']=='204':
            self.cookies = response['set-cookie']
            return True
        return False

    def list_deployment_servers(self, deployment_id):
        """
        Lists servers in a deployment
        """
        response, content = self._request('%s/deployments/%s.js' % (self.api_base, deployment_id))
        return simplejson.loads(content)

    def server_info(self, server_href):
        """
        Detailed server information
        """
        response, content = self._request('%s.js' % server_href)
        return simplejson.loads(content)

    def server_settings(self, server_href):
        """
        Current server settings
        """
        response, content = self._request('%s/settings.js' % server_href)
        return simplejson.loads(content)

    def find_server(self, nickname):
        """
        Finds a server based on nickname
        """
        response, content = self._request('%s/servers.js?filter=nickname=%s' % (self.api_base, nickname))
        servers = simplejson.loads(content)
        return servers[0] if len(servers) else None

    def create_server(self, nickname, defaults):
        """
        Create a server.

        Args:
            nickname (str): the nickname of the server
            defaults (dict): server defaults
        """
        create_data = {'server[nickname]' : nickname}
        for key, value in defaults.items():
            create_data['server[%s]' % key] = value
        response, content = self._request('%s/servers' % self.api_base, method='POST', body=urlencode(create_data))
        location = response['location']
        return location

    def start_server(self, server_href):
        """
        Starts a server.
        """
        return self._request('%s/start' % server_href, method='POST')

    def update_input_parameters(self, server_href, parameters):
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
        return self._request('%s' % server_href, method='PUT', body=update, extra_headers={'Content-Type': 'application/x-www-form-urlencoded'})

    def create_and_start_server(self, nickname, defaults, parameters):
        """
        Creates and starts a server.

        Args:
            nickname (str): the nickname of the server
            defaults (dict): server defaults
            parameters (dict): server parameters
        """
        server_href = self.create_server(nickname, defaults)
        response, content = self.update_input_parameters(server_href, parameters)
        return self.start_server(server_href)

    def stop_server(self, server_href):
        """
        Stops a server.
        """
        return self._request('%s/stop' % server_href, method='POST')

    def delete_server(self, server_href):
        """
        Deletes a server from RightScale
        """
        return self._request('%s' % server_href, method='DELETE')


