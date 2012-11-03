from uuid import uuid4
from testify import (
    assert_equal, assert_not_equal, class_teardown, setup, teardown)
import righteous
from .base import RighteousTestCase


class ServerTestCase(RighteousTestCase):
    envs = []

    @setup
    def prepare_test(self):
        super(RighteousTestCase, self).prepare_test()
        self.delete_server = True
        self.env = 'env-%s' % uuid4().hex

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

    def _create_server(self, instance_type='m1.small'):
        parameters = dict(
            envname=self.env, email=self.username, mode='unattended',
            branches='none')
        successful, location = righteous.create_and_start_server(
            self.env, instance_type, server_template_parameters=parameters)
        assert successful
        assert location is not None
        if self.delete_server:
            self.envs.append(self.env)

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
