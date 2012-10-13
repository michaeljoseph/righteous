import unittest
import requests
import righteous
from righteous import config
from righteous.config import Settings
from mock import Mock, patch


class RighteousTestCase(unittest.TestCase):

    def setup_patching(self, request_module):
        self.requests_patcher = patch(request_module)
        self.request = self.requests_patcher.start()
        self.response = Mock(spec=requests.Response,
            status_code=200,
            headers={},
            text='')
        self.request.return_value = self.response
        self.initialise_settings()

    def tearDown(self):
        if hasattr(self, 'requests_patcher'):
            self.requests_patcher.stop()
            self.initialise_settings()

    def initialise_settings(self):
        config.account_url = 'https://my.rightscale.com/api/acct/'
        config.settings = Settings()
        config.settings.debug = False
        config.settings.cookies = None
        config.settings.username = None
        config.settings.password = None
        config.settings.account_id = None
        config.settings.requests_config = {}


class ApiTestCase(RighteousTestCase):

    def setUp(self):
        righteous.init('user', 'pass', 'account_id')

    def tearDown(self):
        self.initialise_settings()
