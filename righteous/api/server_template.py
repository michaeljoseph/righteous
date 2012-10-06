import re
from urllib import urlencode
import omnijson as json
from .. import config
from .base import _request, debug


def list_server_templates():
    """
    Lists ServerTemplates

    :return: list of dicts of server information with the following keys:

    ::

        [u'description', u'is_head_version', u'created_at', u'updated_at',
         u'href', u'version', u'nickname']
    """
    response = _request('/server_templates.js')
    return json.loads(response.content)


def _extract_template_id(template_href):
    """
    Returns the template id from an href

    :param template_href: String representing the server template
                          href
    :return: String of the template_id or None
    """
    result = re.match(config.account_url + config.settings.account_id +
                      '/ec2_server_templates/(\d+)',
                      template_href)
    if result:
        return result.groups()[0]
    return None


def server_template_info(template_href):
    """
    Details ServerTemplate information

    :param template_href: String representing the server template
                          href
    :return: dict of server template information, with the following keys:

    ::

        [u'description', u'is_head_version', u'created_at', u'updated_at',
         u'href', u'version', u'nickname']
    """
    response = _request('/server_templates/%s.js' %
                        _extract_template_id(template_href))
    template = json.loads(response.content)
    if template:
        return template
    else:
        return None


def create_server_template(nickname, description, multi_cloud_image_href):
    """
    Create a new ServerTemplate

    Returns a tuple of operation status, href of the created, started server

    :param nickname: String of the template nickname
    :param description: String describing the ServerTemplate
    :param multi_cloud_image_href: String of the template image href
    :return: tuple of operation success and new server template href
    """
    location = None
    create_data = {
        'server_template[nickname]': nickname,
        'server_template[description]': description,
        'server_template[multi_cloud_image_href]': multi_cloud_image_href,
    }

    response = _request('/server_templates', method='POST',
                        body=urlencode(create_data))
    success = response.status_code == 201
    if success:
        location = response.headers.get('location')
        debug('Created server template %s: %s (%s:%s)' % (nickname, location,
            response.status_code, response.content))
    # TODO: error responses
    return success, location


def delete_server_template(server_template_href):
    """
    Deletes a ServerTemplate

    :param server_template_href: String of the ServerTemplate to delete
    :return: Boolean of operation success/failure
    """
    return _request('/server_templates/%s.js' %
                    _extract_template_id(server_template_href),
                    method='DELETE').status_code == 200
