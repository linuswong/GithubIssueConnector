import json
from unittest.mock import Mock

import pytest
import requests


@pytest.fixture(autouse=True)
def http_send(monkeypatch):
    """Block live HTTP; each requesting test must supply a mocked response."""
    send = Mock(side_effect=AssertionError("Live HTTP is forbidden in these tests."))
    monkeypatch.setattr(requests.adapters.HTTPAdapter, "send", send)
    return send


@pytest.fixture
def serve_page(http_send):
    """Supply controlled JSON at the HTTP boundary while keeping real Requests."""
    def serve(page, status=200):
        response = requests.Response()
        response.status_code = status
        response.encoding = "utf-8"
        response._content = json.dumps(page).encode("utf-8")

        def respond(prepared, **kwargs):
            response.request = prepared
            response.url = prepared.url
            return response

        http_send.side_effect = respond

    return serve
