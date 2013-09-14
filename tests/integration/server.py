from uuid import uuid4
import righteous
from .base import RighteousTestCase


class ServerTestCase(RighteousTestCase):
    envs = []

    def setUp(self):
        super(RighteousTestCase, self).prepare_test()
        self.delete_server = True
        self.env = 'env-%s' % uuid4().hex

    def tearDown(self):
        if self.delete_server:
            server = righteous.find_server(self.env)
            if server:
                righteous.stop_server(server['href'])

    def tearDownClass(self):
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
        self.assertTrue(successful)
        self.assertTrue(location is not None)
        if self.delete_server:
            self.envs.append(self.env)

    def test_list_servers(self):
        servers = righteous.list_servers()
        self.assertTrue('servers' in servers)
        self.delete_server = False

    def test_server_status(self):
        self._create_server()

        server = righteous.find_server(self.env)
        self.assertTrue(server is not None)
        server_settings = righteous.server_settings(server['href'])
        self.assertTrue(server_settings is not None)
        server_info = righteous.server_info(server['href'])
        self.assertTrue(server_info is not None)
        self.assertEqual(server_settings['ec2-instance-type'], 'm1.small')
        self.assertEqual(server['state'], 'pending')

    def test_create_server(self):
        location = righteous.create_server(self.env, 'm1.small')
        self.assertNotEqual(location, None)
        self.envs.append(self.env)

    def test_create_and_start_server(self):
        self._create_server()

    def test_stop_server(self):
        self._create_server()

        server = righteous.find_server(self.env)
        self.assertTrue(righteous.stop_server(server['href']))

    def test_delete_server(self):
        self._create_server()
        server = righteous.find_server(self.env)
        self.assertTrue(righteous.stop_server(server['href']))

        stopped = False
        while not stopped:
            server = righteous.find_server(self.env)
            stopped = server['state'] == 'stopped'
        self.assertTrue(righteous.delete_server(server['href']))
        self.delete_server = False
