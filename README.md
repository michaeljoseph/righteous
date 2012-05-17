# righteous! : Python RightScale API client

**righteous!** is a Python client implementation of the [RightScale API](http://support.rightscale.com/15-References/RightScale_API_Reference_Guide/02-Management/02-Servers) for EC2 instance management.

![righteous](https://github.com/michaeljoseph/righteous/raw/master/resources/righteous.jpg)

[![Build Status](https://secure.travis-ci.org/michaeljoseph/righteous.png)](http://travis-ci.org/michaeljoseph/righteous)

righteous provides an API to create, start/stop, delete, remove and introspect RightScale EC2 Servers.
This library implements RightScale API 1.0 and has only been tested with EC2 instances using ServerTemplates and managed in a Deployment.

### Installation

Get it from pypi (like it's hot):

    pip install righteous

### API Usage

First, initialise righteous (to access read-only functionality, you just need to provide the following authentication parameters):

```python
    import righteous
    username, password = 'me@domain.com', 'security'
    # find your RightScale account_id by
    account_id = 123
    righteous.init(username, password, account_id)
```

### CLI Usage

Configure the CLI by copying righteous.config.template to ~/.righteous
and customise appropriately

List all the instances

    $ righteous -l
    
Status of a single instance

    $ righteous -s my-instance

Stop an instance

    $ righteous -k my-instance

See all the options

    $ righteous -h

### Development / Running the tests

    $ pip install -r requirements.txt
    $ testify test.unit
    $ testify test.integration 

The integration tests take a couple of  minutes to run since they tests all the current functionality (creating, starting, stopping, deleting environments)
against RightScale.  These tests require a configured righteous.config in the root of the directory (copy and customise righteous.config.template)


Michael Joseph 2012

