#!/usr/bin/env python
# coding: utf-8

import os
from uuid import uuid4
import unittest
import righteous
try:
    import json as simplejson
except ImportError:
    import simplejson


class RighteousTestCase(unittest.TestCase):
    envs = []

    def setUp(self):
        # ['deployment_href', 'instance_type', 'ec2_security_groups_href', 'cloud_id', 'ec2_ssh_key_href', 'ec2_availability_zone', 'server_template_href']
        server_defaults_file = 'server_defaults.json'
        # ['username', 'password', 'default_deployment_id', 'account_id']
        account_defaults_file = 'account_defaults.json'

        if not os.path.exists(server_defaults_file) or not os.path.exists(account_defaults_file):
            raise Exception('Ensure the files %s and %s exists and are populated' % (server_defaults_file, account_defaults_file))

        self.server_defaults = simplejson.loads(open(server_defaults_file).read())
        self.account_defaults = simplejson.loads(open(account_defaults_file).read())

        righteous.init(self.account_defaults, self.server_defaults, debug=True)
        if not righteous.config.settings.cookies:
            righteous.login()

        self.delete_server = True
        self.env = 'env-%s' % uuid4().hex

    def _create_server(self):
        parameters = dict(envname=self.env, email=self.account_defaults['username'], mode='unattended', branches='none')
        successful, location = righteous.create_and_start_server(self.env, parameters)
        self.assertTrue(successful)
        self.assertTrue(location is not None)
        if self.delete_server:
            self.envs.append(self.env)

    def test_create_and_start_server(self):
        self._create_server()

    def test_delete_server(self):
        self._create_server()
        server = righteous.find_server(self.env)
        successful = righteous.stop_server(server['href'])
        self.assertTrue(successful)

        stopped = False
        while not stopped:
            server = righteous.find_server(self.env)
            stopped = server['state'] == 'stopped'
        successful = righteous.delete_server(server['href'])
        self.assertTrue(successful)

        self.delete_server = False

    def test_list_servers(self):
        self._create_server()

        servers = righteous.list_deployment_servers()
        self.assertTrue('servers' in servers)

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

    def test_stop_server(self):
        self._create_server()

        server = righteous.find_server(self.env)
        successful = righteous.stop_server(server['href'])
        self.assertTrue(successful)

    def tearDown(self):
        if self.delete_server:
            server = righteous.find_server(self.env)
            righteous.stop_server(server['href'])

    # tearDownClass for python2.6
    def test_zz(self):
        self.delete_server = False
        print self.envs
        for env in self.envs:
            print env
            stopped = False
            while not stopped:
                server = righteous.find_server(env)
                stopped = server['state'] == 'stopped'
            successful = righteous.delete_server(server['href'])

if __name__ == '__main__':
    unittest.main()



