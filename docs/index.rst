.. righteous documentation master file, created by
   sphinx-quickstart on Fri Jan  6 16:35:09 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: ../resources/righteous.jpg

righteous: A Python Rightscale API/CLI
======================================

Release v\ |release|

**righteous** is a Python client implementation of the `RightScale API <http://support.rightscale.com/15-References/RightScale_API_Reference_Guide>`_ for EC2 instance management.

.. image:: https://secure.travis-ci.org/michaeljoseph/righteous.png

righteous provides an API and CLI to create, start/stop, delete, remove and introspect RightScale EC2 Servers.
This library implements RightScale API 1.0 and has only been tested with EC2 instances using ServerTemplates and managed in a Deployment.

Configuration
-------------

Create a file called `~/.righteous` with the following customised contents:

::

  [auth]
  username: username@domain.com
  password: password
  account_id: 123

  [server-defaults]
  default_deployment_id: 45623
  ec2_security_groups_href: https://my.rightscale.com/api/acct/123/ec2_security_groups/789
  ec2_availability_zone: us-east-1a
  ec2_ssh_key_href: https://my.rightscale.com/api/acct/123/ec2_ssh_keys/998
  cloud_id: 1
  server_template_href: https://my.rightscale.com/api/acct/123/ec2_server_templates/74732
  instance_type: m1.small
  m1.small: https://my.rightscale.com/api/acct/123/ec2_server_templates/74732
  m1.large: https://my.rightscale.com/api/acct/123/ec2_server_templates/117240

CLI
---

::

  righteous
  Interact with the RightScale Server API.

  Usage:
    righteous [options] list
    righteous [options] create <environment> <instance-type> (<server-template-key>=<server-template-value>)...
    righteous [options] stop <environment>...
    righteous [options] status <environment>...
    righteous [options] delete <environment>...
    righteous --version

  Options:
    -c FILE --config=FILE        Specify the configuration file location, default is ~/.righteous
    -v --verbose                 Show debug output          
    -h --help                    Show this screen.

Server API
----------

.. module:: righteous
.. autofunction:: initialise
.. autofunction:: login
.. autofunction:: list_servers
.. autofunction:: find_server
.. autofunction:: server_info
.. autofunction:: server_settings
.. autofunction:: create_and_start_server
.. autofunction:: stop_server
.. autofunction:: delete_server

ServerTemplate API
------------------

.. autofunction:: list_server_templates
.. autofunction:: server_template_info
.. autofunction:: create_server_template
.. autofunction:: delete_server_template

Deployment API
--------------

.. autofunction:: list_deployments
.. autofunction:: find_deployment
.. autofunction:: deployment_info
.. autofunction:: create_deployment
.. autofunction:: delete_deployment
.. autofunction:: duplicate_deployment
