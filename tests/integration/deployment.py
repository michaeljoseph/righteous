from uuid import uuid4
from .base import RighteousIntegrationTestCase
from testify import assert_equal, assert_not_equal, class_teardown, setup
import righteous


class DeploymentTestCase(RighteousIntegrationTestCase):
    deployments = []

    @setup
    def prepare_test(self):
        super(DeploymentTestCase, self).prepare_test()
        self.delete_deployment = True
        self.deployment = 'deployment-%s' % uuid4().hex

    @class_teardown
    def delete_deployments(self):
        for deployment_href in self.deployments:
            righteous.delete_deployment(deployment_href)

    def test_list_deployments(self):
        deployments = righteous.list_deployments()
        assert len(deployments) > 0
        assert_equal(sorted(deployments[0].keys()),
            sorted([u'href', u'description', u'tags',
                u'default_ec2_availability_zone', u'default_vpc_subnet_href',
                u'created_at', u'nickname', u'updated_at', u'servers']))

    def _create_deployment(self):
        success, location = righteous.create_deployment(self.deployment,
            'test deployment')
        assert success
        assert location is not None
        if self.delete_deployment:
            self.deployments.append(location)
        return location

    def test_find_deployment(self):
        deployment_href = self._create_deployment()
        deployment = righteous.find_deployment(self.deployment)
        assert_equal(deployment['nickname'], self.deployment)
        assert_equal(deployment['href'], deployment_href)

    def test_create_deployment(self):
        self._create_deployment()

    def test_deployment_info(self):
        deployment_href = self._create_deployment()
        deployment = righteous.deployment_info(deployment_href)
        assert deployment
        assert_equal(deployment['nickname'], self.deployment)
        assert_equal(deployment['description'], 'test deployment')

    def test_delete_deployment(self):
        self.delete_deployment = False
        deployment_href = self._create_deployment()
        assert righteous.delete_deployment(deployment_href)

    def test_duplicate_deployment(self):
        deployment_href = self._create_deployment()
        success, location = righteous.duplicate_deployment(deployment_href)
        assert success
        assert_not_equal(deployment_href, location)
        duplicated_deployment = righteous.deployment_info(location)
        assert_equal(duplicated_deployment['nickname'],
            self.deployment + ' v1')
        self.deployments.append(location)
