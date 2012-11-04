from uuid import uuid4
from testify import assert_equal, class_teardown, setup
import righteous
from .base import RighteousIntegrationTestCase


class ServerTemplateTestCase(RighteousIntegrationTestCase):
    templates = []

    @setup
    def prepare_test(self):
        super(ServerTemplateTestCase, self).prepare_test()
        self.delete_template = True
        self.template = 'template-%s' % uuid4().hex

    @class_teardown
    def delete_templates(self):
        for template_href in self.templates:
            righteous.delete_server_template(template_href)

    def _create_template(self):
        if not self.config.has_section('server-templates'):
            raise Exception('Ensure that righteous.config has a '
                            'server-templates section')
        multi_cloud_image = self.config.get(
            'server-templates', 'multi_cloud_image')
        success, location = righteous.create_server_template(
            self.template, 'test template', multi_cloud_image)
        assert success
        assert location is not None
        if self.delete_template:
            self.templates.append(location)
        return location

    def test_list_server_templates(self):
        self._create_template()
        templates = righteous.list_server_templates()
        assert len(templates) > 0
        assert_equal(
            sorted(templates[0].keys()),
            sorted([u'description', u'is_head_version', u'created_at',
                    u'updated_at', u'href', u'version', u'nickname']))

    def test_server_template_info(self):
        template_href = self._create_template()
        template = righteous.server_template_info(template_href)
        assert template
        assert_equal(template['nickname'], self.template)

    def test_create_server_template(self):
        self._create_template()

    def test_delete_server_template(self):
        template_href = self._create_template()
        assert righteous.delete_server_template(template_href)
        self.delete_template = False
