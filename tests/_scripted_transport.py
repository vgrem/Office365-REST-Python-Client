"""Shared scripted HTTP transports for offline unit tests (no network).

Payload forms handled by both transports:

- plain ``bytes``/``bytearray`` -> ``200`` with ``application/octet-stream`` body
- a plain dict (e.g. ``{"d": {...}}``) -> ``200`` verbose JSON
- ``("deny",)`` -> ``403`` access-denied JSON
- ``{"status": int, "retry_after": int, "health_score": int, "body": dict|bytes}``
  -> status + throttling headers + body (``bytes`` bodies are octet-stream,
  which lets a test script a ``206`` partial-content range response)
- ``{"http_status": int, "headers": dict, "body": dict|bytes}`` -> an arbitrary
  status + custom headers + JSON/octet-stream body, used to script 202
  long-running-operation poll responses (``headers`` carries
  ``Location``/``Operation-Location``/``Retry-After``)

:class:`ScriptedTransport` returns payloads in call order;
:class:`RoutingTransport` picks the first route whose URL substring matches;
:class:`AsyncScriptedTransport` is the native-async twin that only implements
``execute_async``.
"""

from __future__ import annotations

import json as _json
from typing import Any

from office365.runtime.transport.base import BaseTransport
from requests import Response

_DENIED = {
    "error": {
        "code": "-2147024891, System.UnauthorizedAccessException",
        "message": {"value": "Access is denied."},
    }
}


def build_response(request, payload: Any) -> Response:
    """Build a :class:`requests.Response` for one scripted payload."""
    resp = Response()
    resp.url = request.url

    if isinstance(payload, (bytes, bytearray)):
        resp.status_code = 200
        resp.headers.update({"Content-Type": "application/octet-stream", "Content-Length": str(len(payload))})
        resp._content = bytes(payload)
    elif isinstance(payload, tuple) and payload[0] == "deny":
        resp.status_code = 403
        resp.headers.update({"Content-Type": "application/json"})
        resp._content = _json.dumps(_DENIED).encode("utf-8")
    elif isinstance(payload, dict) and "http_status" in payload:
        resp.status_code = int(payload["http_status"])
        resp.headers.update(payload.get("headers") or {})
        body = payload.get("body")
        if body is None:
            resp._content = b""
        elif isinstance(body, (bytes, bytearray)):
            resp.headers.setdefault("Content-Type", "application/octet-stream")
            resp._content = bytes(body)
        else:
            resp.headers.setdefault("Content-Type", "application/json")
            resp._content = _json.dumps(body).encode("utf-8")
    elif isinstance(payload, dict) and "status" in payload:
        resp.status_code = int(payload["status"])
        body = payload.get("body", {"d": {"results": []}})
        if isinstance(body, (bytes, bytearray)):
            resp.headers.update({"Content-Type": "application/octet-stream", "Content-Length": str(len(body))})
            resp._content = bytes(body)
        else:
            resp.headers.update({"Content-Type": "application/json"})
            resp._content = _json.dumps(body).encode("utf-8")
        if "retry_after" in payload:
            resp.headers["Retry-After"] = str(payload["retry_after"])
        if "health_score" in payload:
            resp.headers["X-SharePointHealthScore"] = str(payload["health_score"])
    else:
        resp.status_code = 200
        resp.headers.update({"Content-Type": "application/json;odata=verbose"})
        resp._content = _json.dumps(payload).encode("utf-8")
    # The body is materialised, so the response behaves like a fully-read one
    # (`iter_content` slices `_content` instead of reading a live `raw`).
    resp._content_consumed = True
    return resp


class ScriptedTransport(BaseTransport):
    """Returns one scripted response per call, in order."""

    def __init__(self, payloads: list[Any]) -> None:
        self._payloads = payloads
        self.calls = 0

    def execute(self, request):
        payload = self._payloads[self.calls]
        self.calls += 1
        return build_response(request, payload)


class RoutingTransport(BaseTransport):
    """Returns the payload of the first route whose key is a substring of the URL.

    Order-independent, so it is safe for concurrent requests.
    """

    def __init__(self, routes: list[tuple[str, Any]]) -> None:
        self._routes = routes
        self.calls: list[str] = []
        self.requests: list[Any] = []

    def execute(self, request):
        url = request.url
        self.calls.append(url)
        self.requests.append(request)
        for key, payload in self._routes:
            if key in url:
                return build_response(request, payload)
        raise AssertionError(f"RoutingTransport: no route matched {url}")


class AsyncScriptedTransport(BaseTransport):
    """Returns one scripted response per call, natively on the event loop.

    Only the asynchronous path is implemented. The synchronous :meth:`execute`
    raises, so a test that accidentally drives this transport from blocking code
    fails loudly instead of silently passing through a worker thread.
    """

    def __init__(self, payloads: list[Any]) -> None:
        self._payloads = payloads
        self.calls = 0

    def execute(self, request):
        raise NotImplementedError("AsyncScriptedTransport only supports execute_async")

    async def execute_async(self, request):
        payload = self._payloads[self.calls]
        self.calls += 1
        return build_response(request, payload)


def parse_batch_requests(request) -> list:
    """Split a ``/_api/$batch`` request body into the individual requests it carries.

    Sub-requests keep their absolute URL (the wire format uses one), so a route
    table keyed on a URL substring matches them exactly as it matches a request
    sent on its own.
    """
    from email import message_from_bytes
    from email.message import Message

    from office365.runtime.http.http_method import HttpMethod
    from office365.runtime.http.request_options import RequestOptions

    def _parts(message: Message):
        for part in message.get_payload():
            if not isinstance(part, Message):
                continue
            if part.get_content_type() == "application/http":
                yield part
            elif part.is_multipart():  # a change set wraps its own application/http parts
                yield from _parts(part)

    def _to_request(part: Message):
        payload = part.get_payload(decode=True)
        assert isinstance(payload, bytes)
        # The serialized batch body separates lines with ``\n`` (the MIME writer
        # re-flowed them), while a hand-built body may use ``\r\n\r\n``.
        head, _, body = payload.replace(b"\r\n", b"\n").partition(b"\n\n")
        lines = [line for line in head.decode("utf-8", "replace").split("\n") if line]
        method, url, _ = lines[0].split(" ", 2)
        req = RequestOptions(url)
        req.method = HttpMethod(method)
        req.data = _json.loads(body) if body.strip() else None
        return req

    return [_to_request(part) for part in _parts(message_from_bytes(request.data))]


def build_batch_response(request, responses: list) -> Response:
    """Compose a ``multipart/mixed`` batch response out of individual responses."""
    boundary = "batchresponse_boundary"
    parts = []
    for resp in responses:
        headers = "".join(f"{key}: {value}\r\n" for key, value in resp.headers.items())
        inner = f"HTTP/1.1 {resp.status_code} Sub Response\r\n{headers}\r\n".encode() + resp.content
        parts.append(
            b"--"
            + boundary.encode()
            + b"\r\nContent-Type: application/http\r\nContent-Transfer-Encoding: binary\r\n\r\n"
            + inner
            + b"\r\n"
        )
    resp = Response()
    resp.url = request.url
    resp.status_code = 200
    resp.headers.update({"Content-Type": f"multipart/mixed; boundary={boundary}"})
    resp._content = b"".join(parts) + b"--" + boundary.encode() + b"--\r\n"
    resp._content_consumed = True
    return resp


class MethodRoutingTransport(BaseTransport):
    """Routes by ``(HTTP method, URL substring)``, and expands ``$batch`` payloads.

    A batch request is parsed into its sub-requests, each one is routed through the
    same table and executed independently, and the individual responses are
    re-composed into a multipart reply. A code path that starts batching therefore
    keeps working against per-endpoint routes, and ``requests`` still records one
    entry per logical request (``batches`` records how they were grouped).
    """

    def __init__(self, routes) -> None:
        self._routes = routes
        self.requests = []
        self.batches: list[list[str]] = []

    def execute(self, request):
        if request.url.endswith("/$batch"):
            return self._execute_batch(request)
        return self.dispatch(request)

    def dispatch(self, request):
        """Route one request through the table, recording it.

        A callable payload is invoked with the request, which lets a route model
        server state (e.g. a collection that gains what another route wrote).
        """
        self.requests.append(request)
        for method, key, payload in self._routes:
            if method is not None and request.method != method:
                continue
            if key in request.url:
                return build_response(request, payload(request) if callable(payload) else payload)
        raise AssertionError(f"no route for {request.method} {request.url}")

    def _execute_batch(self, request):
        parts = parse_batch_requests(request)
        self.batches.append([part.url for part in parts])
        return build_batch_response(request, [self.dispatch(part) for part in parts])
