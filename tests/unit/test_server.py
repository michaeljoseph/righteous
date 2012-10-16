from righteous.compat import urlencode
from .base import ApiTestCase
import righteous
from righteous.config import account_url


class ServerTestCase(ApiTestCase):

    def setUp(self):
        self.setup_patching('righteous.api.server._request')
        super(ServerTestCase, self).setUp()

    def test_list_servers_unconfigured(self):
        self.assertRaises(Exception, righteous.list_servers)

    def test_list_servers(self):
        righteous.init('user', 'pass', 'account_id',
            default_deployment_id='foo')
        self.response.content = '{}'
        righteous.list_servers()
        self.request.assert_called_once_with('/deployments/foo.js')

    def test_find_server_no_result(self):
        self.response.content = '[]'
        server = righteous.find_server('aldous')
        request_url = '/servers.js?filter=nickname=aldous'
        self.request.assert_called_once_with(request_url)
        assert not server

    def test_server_info(self):
        self.response.content = '{}'
        response = righteous.server_info('/server/ref')
        self.assertEqual(response, {})
        self.request.assert_called_once_with('/server/ref.js',
            prepend_api_base=False)

    def test_server_settings(self):
        self.response.content = '{}'
        response = righteous.server_settings('/server/ref')
        self.assertEqual(response, {})

    def test_start_server(self):
        self.response.content = '{}'
        righteous.start_server('/server/ref')
        self.request.assert_called_once_with('/server/ref/start',
            method='POST', prepend_api_base=False)

    def test_stop_server(self):
        self.response.status_code = 201
        assert righteous.stop_server('/server/ref')
        self.request.assert_called_once_with('/server/ref/stop', method='POST',
            prepend_api_base=False)

    def test_delete_server(self):
        self.response.content = '{}'
        assert righteous.delete_server('/server/ref')
        self.request.assert_called_once_with('/server/ref', method='DELETE',
            prepend_api_base=False)

    def test_create_server(self):
        nickname = 'foo'
        create_server_parameters = {
            'server_template_href':
                account_url + '281/ec2_server_templates/52271',
            'm1.small':
                account_url + '281/ec2_server_templates/52271',
            'm1.large':
                account_url + '281/ec2_server_templates/122880',
        }
        create_data = {
            'server[nickname]': nickname,
            'server[server_template_href]':
                create_server_parameters['m1.large']
        }
        expected = urlencode(create_data)

        righteous.create_server(nickname, 'm1.large',
            create_server_parameters=create_server_parameters)
        self.request.assert_called_once_with('/servers', method='POST',
            body=expected)

    ## TODO: test create failure
    def test_create_server_with_init_params(self):
        create_server_parameters = {
            'm1.small': account_url + '123/ec2_server_templates/52271',
            'm1.large': account_url + '123/ec2_server_templates/273583',
        }
        create_data = {
            'server[nickname]':
                'torv',
            'server[server_template_href]':
                create_server_parameters['m1.large']
        }
        expected = urlencode(create_data)

        righteous.init('user', 'pass', 'account', **create_server_parameters)
        righteous.create_server('torv', 'm1.large')
        self.request.assert_called_once_with('/servers', method='POST',
            body=expected)

    def test_set_server_parameters(self):
        server_href = 'http://foo'
        parameters = {'foo': 'bar', 'baz': 'buzz'}

        expected = ('server[parameters][BAZ]=text:buzz&'
                    'server[parameters][FOO]=text:bar')

        righteous.set_server_parameters(server_href, parameters)
        self.request.assert_called_once_with(server_href, method='PUT',
            body=expected,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            prepend_api_base=False)

    def test_create_and_start_server_fails(self):
        create_server_parameters = {
            'm1.small': account_url + '123/ec2_server_templates/52271',
        }
        righteous.init('user', 'pass', 'account', **create_server_parameters)

        success, location = righteous.create_and_start_server('titanic',
            'm1.small')
        assert not success
        assert not location

    def test_create_and_start_server(self):
        create_server_parameters = {
            'm1.small': account_url + '123/ec2_server_templates/52271',
        }
        righteous.init('user', 'pass', 'account', **create_server_parameters)
        new_server_href = '/server/new'
        self.response.status_code = 201
        self.response.headers['location'] = new_server_href
        success, location = righteous.create_and_start_server('arduous',
            'm1.small', server_template_parameters={'envname': 'arduous'})
        assert success

        self.assertEqual(self.request.call_count, 3)

        # create server
        create_data = {
            'server[nickname]':
                'arduous',
            'server[server_template_href]':
                create_server_parameters['m1.small']
        }
        create_expected = urlencode(create_data)
        self.request.assert_any_call('/servers', method='POST',
            body=create_expected)

        # set server parameters
        self.request.assert_any_call(new_server_href, method='PUT',
            body='server[parameters][ENVNAME]=text:arduous',
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            prepend_api_base=False)

        # start server
        self.request.assert_any_call(new_server_href + '/start', method='POST',
            prepend_api_base=False)
