from abc import abstractmethod
import requests
from requests import HTTPError
from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.utilities.http_method import HttpMethod


class ClientRequest(object):
    """Generic client request for OData/REST service"""

    def __init__(self, context):
        self.context = context
        self._queries = []
        self._events = {}

    def clear(self):
        self._queries = []
        self._events = {}

    @abstractmethod
    def build_request(self):
        pass

    @abstractmethod
    def process_response(self, response):
        pass

    def execute_query(self):
        """Submit pending request to the server"""
        for request in self.build_request():
            try:
                response = self.execute_request_direct(request)
                response.raise_for_status()
                self.process_response(response)
            except HTTPError as e:
                raise ClientRequestException(*e.args, response=e.response)
        self.clear()

    def execute_request_direct(self, request_options):
        """Execute client request"""
        self.context.authenticate_request(request_options)
        if request_options.method == HttpMethod.Post:
            if hasattr(request_options.data, 'decode') and callable(request_options.data.decode):
                result = requests.post(url=request_options.url,
                                       headers=request_options.headers,
                                       data=request_options.data,
                                       auth=request_options.auth)
            elif hasattr(request_options.data, 'read') and callable(request_options.data.read):
                result = requests.post(url=request_options.url,
                                       headers=request_options.headers,
                                       data=request_options.data,
                                       auth=request_options.auth)
            else:
                result = requests.post(url=request_options.url,
                                       headers=request_options.headers,
                                       json=request_options.data,
                                       auth=request_options.auth)
        elif request_options.method == HttpMethod.Patch:
            result = requests.patch(url=request_options.url,
                                    headers=request_options.headers,
                                    json=request_options.data,
                                    auth=request_options.auth)
        elif request_options.method == HttpMethod.Delete:
            result = requests.delete(url=request_options.url,
                                     headers=request_options.headers,
                                     auth=request_options.auth)
        elif request_options.method == HttpMethod.Put:
            result = requests.put(url=request_options.url,
                                  data=request_options.data,
                                  headers=request_options.headers,
                                  auth=request_options.auth)
        else:
            result = requests.get(url=request_options.url,
                                  headers=request_options.headers,
                                  auth=request_options.auth)
        return result

    def add_query(self, query, result_object=None):
        self._queries.append(query)
        if result_object is not None:
            query.return_type = result_object

    def before_execute_request(self, event):
        self._events['before'] = event

    def after_execute_request(self, event):
        self._events['after'] = event
