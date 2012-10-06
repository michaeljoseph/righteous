from testify import assert_equal, setup
from urllib import urlencode
from .base import ApiTestCase
import righteous


class DeploymentTestCase(ApiTestCase):
    @setup
    def setup(self):
        self.setup_patching('righteous.api.deployment._request')
        super(DeploymentTestCase, self).setup()

    def test_list_deployments(self):
        righteous.init('user', 'pass', 'account_id',
            default_deployment_id='foo')
        self.response.content = '{}'
        righteous.list_deployments()
        self.request.assert_called_once_with('/deployments.js')

    def test_find_deployment_no_result(self):
        self.response.content = '[]'
        deployment = righteous.find_deployment('bruce')
        request_url = '/deployments.js?filter=nickname=bruce'
        self.request.assert_called_once_with(request_url)
        assert not deployment

    def test_deployment_info(self):
        self.response.content = '{}'
        righteous.deployment_info('/deployment/ref')
        self.request.assert_called_once_with('/deployment/ref.js',
            prepend_api_base=False)

    def test_create_deployment(self):
        nickname = 'devops'
        description = 'devops deployment'
        create_data = {
            'deployment[nickname]': nickname,
            'deployment[description]': description,
        }
        expected = urlencode(create_data)

        righteous.create_deployment(nickname, description)
        self.request.assert_called_once_with('/deployments', method='POST',
            body=expected)

    def test_delete_deployment(self):
        self.response.content = '{}'
        assert righteous.delete_deployment('/deployment/ref')
        self.request.assert_called_once_with('/deployment/ref',
            method='DELETE', prepend_api_base=False)

    def test_duplicate_deployment(self):
        self.response.status_code = 201
        self.response.headers['location'] = '/deployment/new_ref'
        success, location = righteous.duplicate_deployment('/deployment/ref')
        assert success
        self.request.assert_any_call('/deployment/ref/duplicate',
            method='POST')
        assert_equal(location, '/deployment/new_ref')
