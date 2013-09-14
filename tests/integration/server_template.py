from uuid import uuid4
import righteous
from .base import RighteousIntegrationTestCase


class ServerTemplateTestCase(RighteousIntegrationTestCase):
    templates = []

    def setUp(self):
        super(ServerTemplateTestCase, self).prepare_test()
        self.delete_template = True
        self.template = 'template-%s' % uuid4().hex

    def tearDownClass(self):
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
        self.assertTrue(success)
        self.assertTrue(location is not None)
        if self.delete_template:
            self.templates.append(location)
        self.assertTrue(location)

    def test_list_server_templates(self):
        self._create_template()
        templates = righteous.list_server_templates()
        self.assertTrue(len(templates) > 0)
        self.assertEqual(
            sorted(templates[0].keys()),
            sorted([u'description', u'is_head_version', u'created_at',
                    u'updated_at', u'href', u'version', u'nickname'])
        )

    def test_server_template_info(self):
        template_href = self._create_template()
        template = righteous.server_template_info(template_href)
        self.assertTrue(template)
        self.assertEqual(template['nickname'], self.template)

    def test_create_server_template(self):
        self._create_template()

    def test_delete_server_template(self):
        template_href = self._create_template()
        self.assertTrue(righteous.delete_server_template(template_href))
        self.delete_template = False
