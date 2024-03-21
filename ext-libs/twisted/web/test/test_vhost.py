import asyncio
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

import pytest
from twisted.test.requesthelp import DummyRequest
from twisted.web.http import NOT_FOUND
from twisted.web.resource import Resource
from twisted.web.vhost import NameVirtualHost

class TestNameVirtualHost(pytest.TestCase):
    """Tests for NameVirtualHost."""

    async def test_render_without_host(self) -> None:
        """
        NameVirtualHost.render returns the result of rendering the
        instance's default if it is not None and there is no Host header
        in the request.
        """
        virtual_host_resource = NameVirtualHost()
        virtual_host_resource.default = Resource()
        virtual_host_resource.default.render = lambda request: b"correct result"  # type: ignore
        request = DummyRequest(b"")

        response = await virtual_host_resource.render(request)

        self.assertEqual(response, b"correct result")

    async def test_render_without_host_no_default(self) -> None:
        """
        NameVirtualHost.render returns a response with a status of NOT
        FOUND if the instance's default is None and there is no Host
        header in the request.
        """
        virtual_host_resource = NameVirtualHost()
        request = DummyRequest(b"")

        with self.assertRaises(NOT_FOUND):
            await virtual_host_resource.render(request)

    async def test_render_with_host(self) -> None:
        """
        NameVirtualHost.render returns the result of rendering the resource
        which is the value in the instance's host dictionary corresponding
        to the key indicated by the value of the Host header in the request.
        """
        virtual_host_resource = NameVirtualHost()
        virtual_host_resource.host = {b"example.org": Resource()}
        virtual_host_resource.host[b"example.org"].render = lambda request: b"winner"  # type: ignore

        request = DummyRequest(b"")
        request.headers[b"host"] = b"example.org"

        response = await virtual_host_resource.render(request)

        self.assertEqual(response, b"winner")

    async def test_render_with_host_port(self) -> None:
        """
        The port portion of the Host header should not be considered.
        """
        virtual_host_resource = NameVirtualHost()
        virtual_host_resource.host = {b"example.org": Resource()}
        virtual_host_resource.host[b"example.org"].render = lambda request: b"winner"  # type: ignore

        request = DummyRequest(b"")
        request.headers[b"host"] = b"example.org:8000"

        response = await virtual_host_resource.render(request)

        self.assertEqual(response, b"winner")

    async def test_render_with_unknown_host(self) -> None:
        """
        NameVirtualHost.render returns the result of rendering the
        instance's default if it is not None and there is no host
        matching the value of the Host header in the request.
        """
        virtual_host_resource = NameVirtualHost()
        virtual_host_resource.default = Resource()
        virtual_host_resource.default.render = lambda request: b"correct data"  # type: ignore
        request = DummyRequest(b"")
        request.headers[b"host"] = b"example.com"

        response = await virtual_host_resource.render(request)

        self.assertEqual(response, b"correct data")

    async def test_render_with_unknown_host_no_default(self) -> None:
        """
        NameVirtualHost.render returns a response with a status of NOT
        FOUND if the instance's default is None and there is no host
        matching the value of the Host header in the request.
        """
        virtual_host_resource = NameVirtualHost()
        request = DummyRequest(b"")
        request.headers[b"host"] = b"example.com"

        with self.assertRaises(NOT_FOUND):
            await virtual_host_resource.render(request)

