# righteous: Python RightScale API client

[![Build Status](https://secure.travis-ci.org/michaeljoseph/righteous.png)](http://travis-ci.org/michaeljoseph/righteous)
[![Stories in Ready](https://badge.waffle.io/michaeljoseph/righteous.png?label=ready)](https://waffle.io/michaeljoseph/righteous)
[![pypi version](https://badge.fury.io/py/righteous.png)](http://badge.fury.io/py/righteous)
[![# of downloads](https://pypip.in/d/righteous/badge.png)](https://crate.io/packages/righteous?version=latest)
[![code coverage](https://coveralls.io/repos/michaeljoseph/righteous/badge.png?branch=master)](https://coveralls.io/r/michaeljoseph/righteous?branch=master)

**righteous** is a Python client implementation of the [RightScale API](http://support.rightscale.com/15-References/RightScale_API_Reference_Guide) for EC2 instance management.

![righteous](https://github.com/michaeljoseph/righteous/raw/master/resources/righteous.jpg)

righteous provides an API and CLI to create, start/stop, delete, remove and introspect RightScale EC2 Servers.
This library implements RightScale API 1.0 and has only been tested with EC2 instances using ServerTemplates and managed in a Deployment.

### Installation

Get it from pypi (like it's hot):

    pip install righteous

### API Usage

First, initialise righteous (to access all the current functionality (besides creating new instances), you just need to provide the following authentication parameters):

```python
import righteous
username, password = 'me@domain.com', 'security'
# find your RightScale account_id by going to Settings -> Account Settings in the RightScale Dashboard
# The URL that is shown in your browser's location bar should look like the following: https://my.rightscale.com/accounts/1234.
account_id = 1234
righteous.initialise(username, password, account_id)

# list servers
servers = righteous.list_servers()
```

### CLI Usage

Configure the CLI by copying righteous.config.template to ~/.righteous
and customise appropriately.
	
	Righteous CLI.
	
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

List all the instances

    $ righteous list
    
Status of a single instance

    $ righteous status my-instance

Stop an instance

    $ righteous stop my-instance

Remove an instance

    $ righteous delete my-instance


### Development / Running the tests

    $ python setup.py test

The integration tests take a couple of minutes to run since they test all the current functionality (creating, starting, stopping and deleting environments, server templates and deployments)
against RightScale.
These tests require a configured `righteous.config` in the root of the directory, so copy and customise `righteous.config.template` before running:

    # FIXME
    $ testify tests.integration 


Michael Joseph 2012
