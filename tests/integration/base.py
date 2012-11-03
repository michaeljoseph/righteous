from testify import (TestCase, class_setup, setup)
import righteous
from ConfigParser import SafeConfigParser


class RighteousIntegrationTestCase(TestCase):

    @class_setup
    def initialise_righteous(self):
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

        if not righteous.config.settings.cookies:
            righteous.login()
        self.config = config

    @setup
    def prepare_test(self):
        self.username = self.auth['username']
