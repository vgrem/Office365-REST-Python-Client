import requests

from client.runtime.client_action_type import ClientActionType
from client.runtime.context_web_information import ContextWebInformation
from client.runtime.utilities.http_method import HttpMethod


class ClientRequest(object):
    """SharePoint client request"""

    def __init__(self, url, auth_context):
        self.url = url
        self.auth_context = auth_context
        self.defaultHeaders = {'content-type': 'application/json;odata=verbose',
                               'accept': 'application/json;odata=verbose'}
        self.contextWebInformation = None

    @staticmethod
    def process_response_json(response):
        if response.content:
            json = response.json()
            if 'error' in json:
                raise ValueError("Response error:", json['error']['message']['value'])
            return json
        return {}

    def execute_query(self, query):
        headers = {}
        "Execute client request"
        if query.action_type == ClientActionType.Delete:
            headers["X-HTTP-Method"] = "DELETE"
            headers["IF-MATCH"] = '*'
        elif query.action_type == ClientActionType.Update:
            headers["X-HTTP-Method"] = "MERGE"
            headers["IF-MATCH"] = '*'
        url = query.url
        data = query.parameters
        method = HttpMethod.Get
        if query.action_type != ClientActionType.Read:
            method = HttpMethod.Post
        result = self.execute_query_direct(url, headers, data, method)
        return self.process_response_json(result)

    def execute_query_direct(self, request_url, headers=None, data=None, method=HttpMethod.Get):
        """Execute client request"""
        if data is None:
            data = {}
        if headers is None:
            headers = {}
        try:
            self.auth_context.authenticate_request(headers)
            for key in self.defaultHeaders:
                headers[key] = self.defaultHeaders[key]
            if data or 'X-HTTP-Method' in headers or method is HttpMethod.Post:
                self.ensure_form_digest(headers)
                result = requests.post(url=request_url, headers=headers, json=data)
            else:
                result = requests.get(url=request_url, headers=headers)
            return result
        except requests.exceptions.RequestException as e:
            return "Error: {}".format(e)

    def ensure_form_digest(self, headers):
        if not self.contextWebInformation:
            self.request_form_digest()
        headers['X-RequestDigest'] = self.contextWebInformation.form_digest_value

    def request_form_digest(self):
        """Request Form Digest"""
        url = self.url + "/_api/contextinfo"
        headers = self.defaultHeaders
        self.auth_context.authenticate_request(headers)
        result = requests.post(url=url, headers=headers)
        json = result.json()
        self.contextWebInformation = ContextWebInformation()
        self.contextWebInformation.from_json(json['d']['GetContextWebInformation'])
