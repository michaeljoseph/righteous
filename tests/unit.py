#!/usr/bin/env python
# coding: utf-8

import sys
import base64
from testify import *
import requests
import righteous
from righteous import config
from righteous.api import _build_headers
from flexmock import flexmock
try:
    import json as simplejson
except ImportError:
    import simplejson


class RighteousUnitTestCase(TestCase):

    def test_build_headers(self):
        config.settings.cookies = None
        assert_equal(_build_headers(), {'X-API-VERSION': '1.0'})

    def test_additional_headers(self):
        config.settings.cookies = None
        headers = {'foo': 'bar'}
        assert_equal(_build_headers(headers), {'X-API-VERSION': '1.0', 'foo': 'bar'})

    def test_cookie_headers(self):
        config.settings.cookies = 'cookie_value'
        headers = {'baz': 'bar'}
        assert_equal(_build_headers(headers), {'X-API-VERSION': '1.0', 'baz': 'bar', 'Cookie': 'cookie_value'})

    def test_a_request(self):
        username, password, account_id = 'user', 'pass', 'account_id'
        righteous.init(username, password, account_id)
        mock_request = flexmock(requests)
        headers =  {'X-API-VERSION': '1.0'}
        mock_request.should_receive('request').with_args('GET', 'https://my.rightscale.com/api/acct/account_id/test', data=None, headers=headers, config={})
        righteous.api._request('/test')

    def test_aa_request_no_prepend(self):
        username, password, account_id = 'user', 'pass', 'account_id'
        righteous.init(username, password, account_id)
        mock_request = flexmock(requests)
        headers =  {'X-API-VERSION': '1.0'}
        mock_request.should_receive('request').with_args('GET', '/test', data=None, headers=headers, config={})
        righteous.api._request('/test', prepend_api_base=False)

    def test_init(self):
        assert_raises(Exception, righteous.init)

    def test_init_with_args(self):
        righteous.init('user', 'pass', 'account')
        assert_equal(righteous.config.settings.username, 'user')

    def test_init_with_kwargs(self):
        righteous.init('user', 'pass', 'account', debug=True, foo='bar')
        assert_equal(righteous.config.settings.username, 'user')
        assert_equal(righteous.config.settings.debug, sys.stderr)
        assert_equal(righteous.config.settings.create_server_parameters['foo'], 'bar')

    def test_a_login(self):
        assert_raises(Exception, righteous.login)

    def test_login_with_init_credentials(self):
        username, password, account_id = 'user', 'pass', 'account_id'
        righteous.init(username, password, account_id)
        mock_request = flexmock(righteous.api)
        mock_response = flexmock(status_code=204, headers={'set-cookie': 'foo'})

        auth = base64.encodestring('%s:%s' % (username, password))[:-1]
        mock_request.should_receive('_request').with_args('/login', headers={'Authorization': 'Basic %s' % auth}).and_return(mock_response)
        righteous.login()

    def test_b_login_with_credentials(self):
        username, password, account_id = 'foo', 'bar', '123'
        mock_request = flexmock(righteous.api)
        mock_response = flexmock(status_code=204, headers={'set-cookie': 'foo'})

        auth = base64.encodestring('%s:%s' % (username, password))[:-1]
        mock_request.should_receive('_request').with_args('/login', headers={'Authorization': 'Basic %s' % auth}).and_return(mock_response)
        righteous.login(username, password, account_id)

    def test_list_servers(self):
        assert_raises(Exception, righteous.list_servers)

    def test_lookup_server(self):
        assert_raises(ValueError, righteous.api._lookup_server, None, None)

    def test_update_input_parameters(self):
        server_href = 'http://foo'
        parameters = {'foo': 'bar', 'baz': 'buzz'}

        expected = 'server[parameters][FOO]=text:bar&server[parameters][BAZ]=text:buzz'

        mock_request = flexmock(righteous.api)
        mock_request.should_receive('_request').with_args(server_href, method='PUT', body=expected, headers={'Content-Type': 'application/x-www-form-urlencoded'}, prepend_api_base=False)
        righteous.api.set_server_parameters(server_href, parameters)
