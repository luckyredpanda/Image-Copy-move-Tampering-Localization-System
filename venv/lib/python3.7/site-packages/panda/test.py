# -*- coding: utf-8 -*-
import unittest, re
from nose.tools import *
import panda


class PropertiesTest(unittest.TestCase):
    def setUp(self):
        self.i = _panda_instance()

    def test_cloud_id(self):
        eq_(self.i.cloud_id, 'my-cloud-id')

    def test_access_key(self):
        eq_(self.i.access_key, 'my-access-key')

    def test_secret_key(self):
        eq_(self.i.secret_key, 'my-secret-key')

    def test_api_host(self):
        eq_(self.i.api_host, 'api.pandastream.com')

    def test_api_port(self):
        eq_(self.i.api_port, 443)


class UtilsTest(unittest.TestCase):
    def setUp(self):
        self.i = _panda_instance()

    def test_api_url(self):
        eq_(self.i.api_url(), 'https://api.pandastream.com:443/v2')

    def test_https_api_url(self):
        self.i.api_port = 443
        eq_(self.i.api_url(), 'https://api.pandastream.com:443/v2')


class SignatureTest(unittest.TestCase):
    def setUp(self):
        self.i = panda.Panda(access_key='my_access_key', secret_key='my_secret_key', api_host='myapihost', api_port=85, cloud_id='my_cloud_id')

    def test_simple_signed_params(self):
        result = self.i.signed_params('POST', '/videos.json', {}, '2009-11-04T17:54:11+00:00')
        expectation = {
            'access_key': "my_access_key",
            'timestamp': "2009-11-04T17:54:11+00:00",
            'cloud_id': 'my_cloud_id',
            'signature': 'TI2n/dsSllxFhxcEShRGKWtDSqxu+kuJUPs335NavMo=',
        }
        eq_(result, expectation)

    def test_signed_params_with_arguments(self):
        result = self.i.signed_params('POST', '/videos.json', {'param1': 'one', 'param2': 'two'}, '2009-11-04T17:54:11+00:00')
        expectation = {
            'access_key': "my_access_key",
            'timestamp': "2009-11-04T17:54:11+00:00",
            'cloud_id': 'my_cloud_id',
            'signature': 'w66goW6Ve5CT9Ibbx3ryvq4XM8OfIfSZe5oapgZBaUs=',
            'param1': 'one',
            'param2': 'two',
        }
        eq_(result, expectation)

    def test_signed_params_with_file_argument(self):
        result = self.i.signed_params('POST', '/videos.json', {'param1': 'one', 'param2': 'two',
            'file': 'file data'}, '2009-11-04T17:54:11+00:00')
        expectation = {
            'access_key': "my_access_key",
            'timestamp': "2009-11-04T17:54:11+00:00",
            'cloud_id': 'my_cloud_id',
            'signature': 'w66goW6Ve5CT9Ibbx3ryvq4XM8OfIfSZe5oapgZBaUs=',
            'param1': 'one',
            'param2': 'two',
            'file': 'file data'
        }
        eq_(result, expectation)

    def test_signed_params_with_non_string_arguments(self):
        result = self.i.signed_params('POST', '/videos.json', {1: 'one', 'param2': 2}, '2009-11-04T17:54:11+00:00')
        expectation = {
            'access_key': "my_access_key",
            'timestamp': "2009-11-04T17:54:11+00:00",
            'cloud_id': 'my_cloud_id',
            'signature': 'n/tGZ9Pt70k+pprejGf8Khzxw9R1cAfrklh8lcjn+W0=',
            1: 'one',
            'param2': 2,
        }
        eq_(result, expectation)

    def test_signed_params_with_difficult_characters(self):
        result = self.i.signed_params('POST', '/videos.json', {'tilde': '~', 'space': ' ', 'slash': '/'}, '2009-11-04T17:54:11+00:00')
        expectation = {
            'access_key': "my_access_key",
            'timestamp': "2009-11-04T17:54:11+00:00",
            'cloud_id': 'my_cloud_id',
            'signature': 'DHf9ERJmKQbcu8MCLP1Evv3BV2yIQo15MoTe9YV/rs8=',
            'tilde': '~',
            'space': ' ',
            'slash': '/',
        }
        eq_(result, expectation)

    def test_signed_params_with_unicode_characters(self):
        result = self.i.signed_params(
            'POST',
            '/videos/upload.json',
            {'file_name': u'original♥.mp4'},
            '2014-12-22T17:54:11+00:00')
        expectation = {
            'access_key': "my_access_key",
            'timestamp': "2014-12-22T17:54:11+00:00",
            'cloud_id': 'my_cloud_id',
            'signature': 'NBK3+4HtaolBLi0I1Ai9MEXQvCG+T96E7PEIKf4CMwM=',
            'file_name': u'original♥.mp4'
        }
        eq_(result, expectation)


class TimestampTest(unittest.TestCase):
    def test_timestamp_includes_timezone(self):
        ok_(re.search(':\d\d(\.\d+)?(\+|-)\d\d:\d\d$', panda.generate_timestamp()))


def _panda_instance():
    return panda.Panda(cloud_id='my-cloud-id', access_key='my-access-key', secret_key='my-secret-key')
