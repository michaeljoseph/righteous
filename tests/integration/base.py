import righteous
from ConfigParser import SafeConfigParser
from ..compat import unittest

class RighteousIntegrationTestCase(unittest.TestCase):

    def setUp(self):
        config = SafeConfigParser()
        config.read('righteous.config')
        if not config.has_section('auth'):
            raise Exception('Please create a righteous.config file with '
                            'appropriate credentials')

        self.auth = dict(
            (key, config.get('auth', key))
            for key in config.options('auth'))
        self.server = dict(
            (key, config.get('server-defaults', key))
            for key in config.options('server-defaults'))

        righteous.init(
            self.auth['username'], self.auth['password'],
            self.auth['account_id'], **self.server)


        self.config = config
        self.username = self.auth['username']


    def test_login(self):
        self.assertTrue(righteous.login())
