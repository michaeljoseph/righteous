import sys
import base64
from testify import TestCase, assert_equal, setup, teardown, assert_raises
from urllib import urlencode
import requests
import righteous
from righteous import config
from righteous.api import _build_headers
from righteous.config import Settings
from mock import Mock, patch
import omnijson as json

class RighteousTestCase(TestCase):

    @setup
    def setup(self):
        self.requests_patcher = patch('righteous.api._request')
        self.request = self.requests_patcher.start()
        self.response = Mock(spec=requests.Response,
            status_code=200, 
            headers={},
            text='')
        self.request.return_value = self.response
        self.initialise_settings()

    @teardown
    def teardown(self):
        self.requests_patcher.stop()
        self.initialise_settings()

    def initialise_settings(self):
        config.settings = Settings()
        config.settings.debug = False
        config.settings.cookies = None
        config.settings.username = None
        config.settings.password = None
        config.settings.account_id = None
        config.settings.requests_config = {}

class BuildHeaderTestCase(RighteousTestCase):

    def test_build_headers(self):
        assert_equal(_build_headers(), {'X-API-VERSION': '1.0'})

    def test_additional_headers(self):
        headers = {'foo': 'bar'}
        assert_equal(_build_headers(headers), {'X-API-VERSION': '1.0', 'foo': 'bar'})

    def test_cookie_headers(self):
        config.settings.cookies = 'cookie_value'
        headers = {'baz': 'bar'}
        assert_equal(_build_headers(headers), {'X-API-VERSION': '1.0', 'baz': 'bar', 'Cookie': 'cookie_value'})


class InitialiseTestCase(RighteousTestCase):

    def test_init(self):
        assert_raises(Exception, righteous.init)

    def test_init_with_null_arg(self):
        assert_raises(Exception, righteous.init, 'user', 'pass', None)

    def test_init_with_args(self):
        righteous.init('user', 'pass', 'account')
        assert_equal(righteous.config.settings.username, 'user')

    def test_init_with_kwargs(self):
        righteous.init('user', 'pass', 'account', debug=True, foo='bar')
        assert_equal(righteous.config.settings.username, 'user')
        assert_equal(righteous.config.settings.debug, sys.stderr)
        assert_equal(righteous.config.settings.create_server_parameters['foo'], 'bar')

    def test_init_deployment_id(self):
        righteous.init('user', 'pass', 'account', default_deployment_id='22')

        assert_equal(righteous.config.settings.default_deployment_id, '22')
        server_parameters = righteous.config.settings.create_server_parameters
        assert_equal(server_parameters['deployment_href'], 
            'https://my.rightscale.com/api/acct/account/deployments/22')


class RequestsTestCase(TestCase):

    def test_request(self):
        username, password, account_id = 'user', 'pass', 'account_id'
        righteous.init(username, password, account_id, debug=False)
        headers =  {'X-API-VERSION': '1.0'}

        with patch('righteous.api.requests') as mock_requests:
            righteous.api._request('/test')
            mock_requests.request.assert_called_once_with('GET', 'https://my.rightscale.com/api/acct/account_id/test', headers=headers, config={}, data=None)

    def test_request_no_prepend(self):
        username, password, account_id = 'user', 'pass', 'account_id'
        righteous.init(username, password, account_id, debug=False)
        headers =  {'X-API-VERSION': '1.0'}

        with patch('righteous.api.requests') as mock_requests:
            righteous.api._request('/test', prepend_api_base=False)
            mock_requests.request.assert_called_once_with('GET', '/test', headers=headers, config={}, data=None)


class LoginTestCase(RighteousTestCase):

    def test_login(self):
        assert_raises(Exception, righteous.login)

    def test_login_failure(self):
        assert not righteous.login('foo', 'bar', 'buzz')

    def test_login_with_init_credentials(self):
        username, password, account_id = 'user', 'pass', 'account_id'
        auth = base64.encodestring('%s:%s' % (username, password))[:-1]

        righteous.init(username, password, account_id)

        self.response.status_code = 204
        self.response.headers['set-cookie'] = 'cookie_value' 
        login_result = righteous.login()
        assert login_result
        self.request.assert_called_once_with('/login', headers={'Authorization': 'Basic %s' % auth})

    def test_login_with_credentials(self):
        username, password, account_id = 'foo', 'bar', '123'
        auth = base64.encodestring('%s:%s' % (username, password))[:-1]

        self.response.status_code = 204
        self.response.headers['set-cookie'] = 'cookie_value' 
        login_result = righteous.login(username, password, account_id)
        assert login_result
        self.request.assert_called_once_with('/login', headers={'Authorization': 'Basic %s' % auth})


class ApiTestCase(RighteousTestCase):

    @setup
    def setup(self):
        righteous.init('user', 'pass', 'account_id')

    def test_lookup_server_unconfigured(self):
        assert_raises(ValueError, righteous.api._lookup_server, None, None)

    def test_lookup_server_href(self):
        href = righteous.api._lookup_server('/foo/bar', None)
        assert_equal(href, '/foo/bar')

    def test_lookup_server_nickname(self):
        self.response.content = json.dumps([{'href': '/naruto'}])
        href = righteous.api._lookup_server(None, 'naruto')
        assert_equal(href, '/naruto')

    def test_lookup_server_nickname_failure(self):
        self.response.content = '[]'
        assert_raises(Exception, righteous.api._lookup_server, None, 'unknown')

    def test_list_servers_unconfigured(self):
        assert_raises(Exception, righteous.list_servers)

    def test_list_servers(self):
        righteous.init('user', 'pass', 'account_id', default_deployment_id='foo')
        self.response.content = '{}'
        righteous.list_servers()
        self.request.assert_called_once_with('/deployments/foo.js')

    def test_find_server_no_result(self):
        self.response.content = '[]'
        server = righteous.find_server('aldous')
        self.request.assert_called_once_with('/servers.js?filter=nickname=aldous')
        assert not server

    def test_server_info(self):
        self.response.content = '{}'
        response = righteous.server_info('/my/ref')
        assert_equal(response, {})
        self.request.assert_called_once_with('/my/ref.js', prepend_api_base=False)

    def test_server_settings(self):
        self.response.content = '{}'
        response = righteous.server_settings('/my/ref')
        assert_equal(response, {})

    def test_start_server(self):
        self.response.content = '{}'
        righteous.start_server('/my/ref')
        self.request.assert_called_once_with('/my/ref/start', method='POST', prepend_api_base=False)

    def test_stop_server(self):
        self.response.status_code = 201
        assert righteous.stop_server('/my/ref')
        self.request.assert_called_once_with('/my/ref/stop', method='POST', prepend_api_base=False)

    def test_delete_server(self):
        self.response.content = '{}'
        assert righteous.delete_server('/my/ref')

    def test_create_server(self):
        nickname = 'foo'
        create_server_parameters = {
            'server_template_href': 'https://my.rightscale.com/api/acct/281/ec2_server_templates/52271',
            'm1.small': 'https://my.rightscale.com/api/acct/281/ec2_server_templates/52271',
            'm1.large': 'https://my.rightscale.com/api/acct/281/ec2_server_templates/122880',
        }
        create_data = {
            'server[nickname]' : nickname,
            'server[server_template_href]': create_server_parameters['m1.large']
        }
        expected = urlencode(create_data)

        righteous.create_server(nickname, 'm1.large', create_server_parameters=create_server_parameters)
        self.request.assert_called_once_with('/servers', method='POST', body=expected)

    def test_create_server_with_init_params(self):
        create_server_parameters = {
            'm1.small': 'https://my.rightscale.com/api/acct/123/ec2_server_templates/52271',
            'm1.large': 'https://my.rightscale.com/api/acct/123/ec2_server_templates/273583',
        }
        create_data = {
            'server[nickname]' : 'torv',
            'server[server_template_href]': create_server_parameters['m1.large']
        }
        expected = urlencode(create_data)

        righteous.init('user', 'pass', 'account', **create_server_parameters)
        righteous.create_server('torv', 'm1.large')
        self.request.assert_called_once_with('/servers', method='POST', body=expected)

    def test_set_server_parameters(self):
        server_href = 'http://foo'
        parameters = {'foo': 'bar', 'baz': 'buzz'}

        expected = 'server[parameters][FOO]=text:bar&server[parameters][BAZ]=text:buzz'

        righteous.set_server_parameters(server_href, parameters)
        self.request.assert_called_once_with(server_href, method='PUT', body=expected, headers={'Content-Type': 'application/x-www-form-urlencoded'}, prepend_api_base=False)

    # TODO: test that create_server_parameters not containing an instance key errors
    #def test_create_and_start_server_fails(self):
        #success, location = righteous.create_and_start_server('titanic', 'm1.small')
        #assert not success
        #assert not location

    def test_create_and_start_server_fails(self):
        create_server_parameters = {
            'm1.small': 'https://my.rightscale.com/api/acct/123/ec2_server_templates/52271',
        }
        righteous.init('user', 'pass', 'account', **create_server_parameters)
        
        success, location = righteous.create_and_start_server('titanic', 'm1.small')
        assert not success
        assert not location

    def test_create_and_start_server(self):
        create_server_parameters = {
            'm1.small': 'https://my.rightscale.com/api/acct/123/ec2_server_templates/52271',
        }
        righteous.init('user', 'pass', 'account', **create_server_parameters)
        new_server_href = '/server/new'
        self.response.status_code = 201
        self.response.headers['location'] = new_server_href 
        success, location = righteous.create_and_start_server('arduous', 'm1.small', server_template_parameters={'envname':'arduous'})
        assert success

        assert_equal(self.request.call_count, 3)

        # create server
        create_data = {
            'server[nickname]': 'arduous',
            'server[server_template_href]': create_server_parameters['m1.small']
        }
        create_expected = urlencode(create_data)
        self.request.assert_any_call('/servers', method='POST', body=create_expected)

        # set server parameters
        self.request.assert_any_call(new_server_href, method='PUT', body='server[parameters][ENVNAME]=text:arduous', headers={'Content-Type': 'application/x-www-form-urlencoded'}, prepend_api_base=False)

        # start server
        self.request.assert_any_call(new_server_href+'/start', method='POST', prepend_api_base=False)
