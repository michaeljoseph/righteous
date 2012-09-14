from uuid import uuid4
from testify import (TestCase, assert_equal, assert_not_equal, class_setup,
    class_teardown, setup, teardown)
import righteous
from ConfigParser import SafeConfigParser

class RighteousTestCase(TestCase):
    envs = []
    templates = []

    @class_setup
    def initialise_righteous(self):
        config = SafeConfigParser()
        config.read('righteous.config')
        if not config.has_section('auth'):
            raise Exception('Please create a righteous.config file with appropriate credentials')

        self.auth = dict((key,config.get('auth', key)) for key in config.options('auth'))
        self.server = dict((key,config.get('server-defaults', key)) for key in config.options('server-defaults'))
        righteous.init(self.auth['username'], self.auth['password'], self.auth['account_id'], **self.server)

        if not righteous.config.settings.cookies:
            righteous.login()
        self.config = config

    @setup
    def prepare_test(self):
        self.delete_server = True
        self.delete_template = False
        self.env = 'env-%s' % uuid4().hex
        self.template = 'template-%s' % uuid4().hex
        self.username = self.auth['username']

    def _create_server(self, instance_type='m1.small'):
        parameters = dict(envname=self.env, email=self.username, mode='unattended', branches='none')
        successful, location = righteous.create_and_start_server(self.env, instance_type, server_template_parameters=parameters)
        assert successful
        assert location is not None
        if self.delete_server:
            self.envs.append(self.env)

    def _create_template(self):
        if not self.config.has_section('server-templates'):
            raise Exception('Ensure that righteous.config has a server-templates section')
        multi_cloud_image = self.config.get('server-templates', 'multi_cloud_image')
        success, location = righteous.create_server_template(self.template, 'test template',
                multi_cloud_image)
        assert success
        assert location is not None
        if self.delete_template:
            self.templates.append(location)
        return location

    def test_list_server_templates(self):
        self.delete_template = True
        self._create_template()
        templates = righteous.list_server_templates()
        assert len(templates) > 0
        assert_equal(templates[0].keys(), [u'description', u'is_head_version', u'created_at', u'updated_at', u'href', u'version', u'nickname'])

    def test_server_template_info(self):
        self.delete_template = True
        template_href = self._create_template()
        template = righteous.server_template_info(template_href)
        assert template
        assert_equal(template['nickname'], self.template)

    def test_create_server_template(self):
        self.delete_template = True
        self._create_template()

    def test_delete_server_template(self):
        template_href = self._create_template()
        assert righteous.delete_server_template(template_href)

    def test_list_servers(self):
        servers = righteous.list_servers()
        assert 'servers' in servers
        self.delete_server = False

    def test_server_status(self):
        self._create_server()

        server = righteous.find_server(self.env)
        assert server is not None
        server_settings = righteous.server_settings(server['href'])
        assert server_settings is not None
        server_info = righteous.server_info(server['href'])
        assert server_info is not None
        assert_equal(server_settings['ec2-instance-type'], 'm1.small')
        assert_equal(server['state'], 'pending')

    def test_create_server(self):
        location = righteous.create_server(self.env, 'm1.small')
        assert_not_equal(location, None)
        self.envs.append(self.env)

    def test_create_and_start_server(self):
        self._create_server()

    def test_stop_server(self):
        self._create_server()

        server = righteous.find_server(self.env)
        successful = righteous.stop_server(server['href'])
        assert successful

    def test_delete_server(self):
        self._create_server()
        server = righteous.find_server(self.env)
        successful = righteous.stop_server(server['href'])
        assert successful

        stopped = False
        while not stopped:
            server = righteous.find_server(self.env)
            stopped = server['state'] == 'stopped'
        successful = righteous.delete_server(server['href'])
        assert successful

        self.delete_server = False

    @teardown
    def stop_servers(self):
        if self.delete_server:
            server = righteous.find_server(self.env)
            if server:
                righteous.stop_server(server['href'])

    @class_teardown
    def delete_servers(self):
        for env in self.envs:
            stopped = False
            while not stopped:
                server = righteous.find_server(env)
                if server:
                    stopped = server['state'] == 'stopped'
                else:
                    stopped = True
            righteous.delete_server(server['href'])
    
    @class_teardown
    def delete_templates(self):
        for template_href in self.templates:
            righteous.delete_server_template(template_href)

