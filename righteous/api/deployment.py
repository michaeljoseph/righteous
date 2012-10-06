import omnijson as json
from urllib import urlencode, quote
from .base import _request, debug, lookup_by_href_or_nickname


def _lookup_deployment(deployment_href, nickname):
    """
    Convenience wrapper around `righteous.base.lookup_by_href_or_nickname`
    """
    return lookup_by_href_or_nickname(
        deployment_href, nickname, find_deployment)


def list_deployments():
    """
    Lists server deployment in an account

    :return: dict of server deployment information with the following keys:

    ::

        [u'href', u'description', u'tags', u'default_ec2_availability_zone',
         u'default_vpc_subnet_href', u'created_at', u'nickname', u'updated_at',
         u'servers']
    """
    response = _request('/deployments.js')
    return json.loads(response.content)


def find_deployment(nickname):
    """
    Finds a server deployment based on nickname

    :param nickname: (optional) String representing the nickname of the
                     deployment to lookup
    :return: dict of deployment information with the following keys:

    ::

        [u'href', u'description', u'tags', u'default_ec2_availability_zone',
         u'default_vpc_subnet_href', u'created_at', u'nickname', u'updated_at',
         u'servers']
    """
    response = _request('/deployments.js?filter=nickname=%s' % quote(nickname))
    deployments = json.loads(response.content)
    return deployments[0] if len(deployments) else None


def deployment_info(deployment_href, nickname=None):
    """
    Detailed server deployment information

    :param deployment_href: URL representing the deployment to retrieve
                            information about
    :param nickname: (optional) String representing the nickname of the
                     deployment
    :return: dict of deployment information with the following keys

    ::

        [u'href', u'description', u'tags', u'default_ec2_availability_zone',
         u'default_vpc_subnet_href', u'created_at', u'nickname', u'updated_at',
         u'servers']
    """
    response = _request('%s.js' % _lookup_deployment(
                                    deployment_href, nickname),
                        prepend_api_base=False)
    return json.loads(response.content)


def create_deployment(nickname, description):
    """
    Creates a server deployment

    :param nickname: Nickname of the new deployment
    :param description: Description of the new deployment
    """
    location = None
    create_data = {'deployment[nickname]': nickname,
                   'deployment[description]': description}
    response = _request('/deployments',
        method='POST', body=urlencode(create_data))

    success = response.status_code == 201
    if success:
        location = response.headers.get('location')
        debug('Created deployment %s: %s (%s:%s)' % (nickname, location,
            response.status_code, response.content))
    else:
        debug('Error creating deployment %s: %s' % (nickname,
            response.content))
    # TODO: error responses
    return success, location


def delete_deployment(deployment_href, nickname=None):
    """
    Deletes a server deployment

    :param deployment_href: URL representing the deployment to delete
    :param nickname: (optional) String representing the nickname of the
                     deployment
    :return: Boolean of operation success/failure
    """
    return _request(_lookup_deployment(deployment_href, nickname),
        method='DELETE', prepend_api_base=False).status_code == 200


def duplicate_deployment(deployment_href, nickname=None):
    """
    Duplicates a server deployment

    :param deployment_href: URL representing the deployment to duplicate
    :param nickname: (optional) String repesenting the nickname of the
                     deployment to duplicate
    :return: tuple of operation success Boolean and deployment href of the
             duplicated instance
    """
    location = None
    response = _request('%s/duplicate' %
        _lookup_deployment(deployment_href, nickname), method='POST',
        prepend_api_base=False)

    success = response.status_code == 201
    if success:
        location = response.headers.get('location')
        debug('Duplicated deployment %s: %s (%s:%s)' % (nickname, location,
            response.status_code, response.content))
    else:
        debug('Error duplicating deployment %s: %s' % (nickname,
            response.content))
    # TODO: error responses
    return success, location
