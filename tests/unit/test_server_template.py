from righteous.compat import urlencode
import omnijson as json
from .base import ApiTestCase
import righteous
from righteous.config import account_url


class ServerTemplateTestCase(ApiTestCase):

    def setUp(self):
        self.setup_patching('righteous.api.server_template._request')
        super(ServerTemplateTestCase, self).setUp()

    def test_list_server_templates(self):
        self.response.content = '{}'
        righteous.list_server_templates()
        self.request.assert_called_once_with('/server_templates.js')

    def test_server_template_info(self):
        template_href = account_url + 'account_id/ec2_server_templates/111'
        server_template = [{
            'href': template_href,
            'nickname': 'spurious'
        }]
        self.response.content = json.dumps(server_template)
        response = righteous.server_template_info(template_href)
        self.assertEqual(response, server_template)
        self.request.assert_called_once_with('/server_templates/111.js')

    def test_server_template_info_not_found(self):
        template_href = account_url + 'account_id/ec2_server_templates/111'
        self.response.content = '[]'
        response = righteous.server_template_info(template_href)
        self.assertEqual(response, None)
        self.request.assert_called_once_with('/server_templates/111.js')

    def test_create_server_template(self):
        nickname = 'templator'
        description = 'uber template for the masses'
        cloud_image_href = '/foo/bar'

        new_template_href = '/template/new'
        self.response.status_code = 201
        self.response.headers['location'] = new_template_href

        success, location = righteous.create_server_template(nickname,
            description, cloud_image_href)
        assert success
        self.assertEqual(location, new_template_href)

        body = urlencode({
            'server_template[nickname]': nickname,
            'server_template[description]': description,
            'server_template[multi_cloud_image_href]': cloud_image_href,
        })

        self.request.assert_called_once_with('/server_templates',
            method='POST', body=body)

    def test_delete_server_template(self):
        template_href = account_url + 'account_id/ec2_server_templates/111'
        self.response.content = '{}'
        assert righteous.delete_server_template(template_href)

        self.request.assert_called_once_with('/server_templates/111.js',
            method='DELETE')
