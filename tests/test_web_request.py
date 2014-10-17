import unittest
from unittest import mock
from aiohttp.web import Request
from aiohttp.multidict import MultiDict
from aiohttp.protocol import HttpVersion
from aiohttp.protocol import Request as RequestImpl


class TestWebRequest(unittest.TestCase):

    def make_request(self, method, path, headers=()):
        self.app = mock.Mock()
        self.transport = mock.Mock()
        message = RequestImpl(self.transport, method, path)
        message.headers.extend(headers)
        self.payload = mock.Mock()
        self.protocol = mock.Mock()
        req = Request(self.app, message, self.payload, self.protocol)
        return req

    def test_ctor(self):
        req = self.make_request('GeT', '/path/to?a=1&b=2')

        self.assertIs(self.app, req.app)
        self.assertEqual('GET', req.method)
        self.assertEqual(HttpVersion(1, 1), req.version)
        self.assertEqual(None, req.host)
        self.assertEqual('/path/to?a=1&b=2', req.path_qs)
        self.assertEqual('/path/to', req.path)
        self.assertEqual('a=1&b=2', req.query_string)
        self.assertEqual(MultiDict([('a', '1'), ('b', '2')]), req.GET)
        self.assertIs(self.payload, req.payload)
        self.assertFalse(req.closing)

    def test_content_type_not_specified(self):
        req = self.make_request('Get', '/')
        self.assertEqual('application/octet-stream', req.content_type)

    def test_content_type_from_spec(self):
        req = self.make_request('Get', '/',
                                {'content-type': 'application/json'})
        self.assertEqual('application/json', req.content_type)

    def test_content_type_from_spec_with_charset(self):
        req = self.make_request('Get', '/',
                                {'content-type': 'text/html; charset=UTF-8'})
        self.assertEqual('text/html', req.content_type)
        self.assertEqual('UTF-8', req.charset)

    def test_calc_content_type_on_getting_charset(self):
        req = self.make_request('Get', '/',
                                {'content-type': 'text/html; charset=UTF-8'})
        self.assertEqual('UTF-8', req.charset)
        self.assertEqual('text/html', req.content_type)

    def test_urlencoded_querystring(self):
        req = self.make_request(
            'GET',
            '/yandsearch?text=%D1%82%D0%B5%D0%BA%D1%81%D1%82')
        self.assertEqual({'text': 'текст'}, req.GET)

    def test_non_ascii_path(self):
        req = self.make_request('GET', '/путь')
        self.assertEqual('/путь', req.path)

    def test_content_length(self):
        req = self.make_request('Get', '/', {'Content-Length': '123'})

        self.assertEqual(123, req.content_length)