# righteous! : Python RightScale API client

**righteous!** is a Python client implementation of the [RightScale API](http://support.rightscale.com/15-References/RightScale_API_Reference_Guide) for EC2 instance management.

![righteous](https://github.com/michaeljoseph/righteous/raw/master/resources/righteous.jpg)

[![Build Status](https://secure.travis-ci.org/michaeljoseph/righteous.png)](http://travis-ci.org/michaeljoseph/righteous)

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
righteous.init(username, password, account_id)

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

    $ pip install -r requirements.txt
    $ testify tests.unit

The integration tests take a couple of  minutes to run since they tests all the current functionality (creating, starting, stopping, deleting environments)
against RightScale.  These tests require a configured righteous.config in the root of the directory (copy and customise righteous.config.template)

    $ testify tests.integration 


Michael Joseph 2012

