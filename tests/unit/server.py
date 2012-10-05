import json
from testify import assert_equal, setup, assert_raises
from urllib import urlencode
from .base import ApiTestCase
import righteous


class LookupServerTestCase(ApiTestCase):
    @setup
    def setup(self):
        self.setup_patching('righteous.api.server._request')
        super(LookupServerTestCase, self).setup()

    def test_lookup_server_unconfigured(self):
        assert_raises(ValueError, righteous.api.server._lookup_server, None, None)

    def test_lookup_server_href(self):
        href = righteous.api.server._lookup_server('/foo/bar', None)
        assert_equal(href, '/foo/bar')

    def test_lookup_server_nickname(self):
        self.response.content = json.dumps([{'href': '/naruto'}])
        href = righteous.api.server._lookup_server(None, 'naruto')
        assert_equal(href, '/naruto')

    def test_lookup_server_nickname_failure(self):
        self.response.content = '[]'
        assert_raises(Exception, righteous.api.server._lookup_server, None, 'unknown')

class ServerTestCase(ApiTestCase):
    @setup
    def setup(self):
        self.setup_patching('righteous.api.server._request')
        super(ServerTestCase, self).setup()

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
        self.request.assert_called_once_with('/my/ref', method='DELETE', prepend_api_base=False)

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
