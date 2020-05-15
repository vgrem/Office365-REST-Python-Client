from abc import abstractmethod
import requests
from requests import HTTPError
from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.utilities.EventHandler import EventHandler


class ClientRequest(object):
    """Base request for OData/REST service"""

    def __init__(self, context):
        self.context = context
        self._queries = []
        self.beforeExecute = EventHandler()
        self.afterExecute = EventHandler()

    @property
    def queries(self):
        return self._queries

    @abstractmethod
    def build_request(self):
        pass

    @abstractmethod
    def process_response(self, response):
        pass

    def execute_query(self):
        """Submit a pending request to the server"""
        try:
            request = self.build_request()
            self.beforeExecute.notify(request)
            response = self.execute_request_direct(request)
            response.raise_for_status()
            self.process_response(response)
            self.afterExecute.notify(response)
        except HTTPError as e:
            raise ClientRequestException(*e.args, response=e.response)

    def execute_request_direct(self, request_options):
        """Execute client request"""
        self.context.authenticate_request(request_options)
        if request_options.method == HttpMethod.Post:
            if hasattr(request_options.data, 'decode') and callable(request_options.data.decode):
                result = requests.post(url=request_options.url,
                                       headers=request_options.headers,
                                       data=request_options.data,
                                       auth=request_options.auth,
                                       verify=request_options.verify)
            elif hasattr(request_options.data, 'read') and callable(request_options.data.read):
                result = requests.post(url=request_options.url,
                                       headers=request_options.headers,
                                       data=request_options.data,
                                       auth=request_options.auth,
                                       verify=request_options.verify)
            else:
                result = requests.post(url=request_options.url,
                                       headers=request_options.headers,
                                       json=request_options.data,
                                       auth=request_options.auth,
                                       verify=request_options.verify)
        elif request_options.method == HttpMethod.Patch:
            result = requests.patch(url=request_options.url,
                                    headers=request_options.headers,
                                    json=request_options.data,
                                    auth=request_options.auth,
                                    verify=request_options.verify)
        elif request_options.method == HttpMethod.Delete:
            result = requests.delete(url=request_options.url,
                                     headers=request_options.headers,
                                     auth=request_options.auth,
                                     verify=request_options.verify)
        elif request_options.method == HttpMethod.Put:
            result = requests.put(url=request_options.url,
                                  data=request_options.data,
                                  headers=request_options.headers,
                                  auth=request_options.auth,
                                  verify=request_options.verify)
        else:
            result = requests.get(url=request_options.url,
                                  headers=request_options.headers,
                                  auth=request_options.auth,
                                  verify=request_options.verify)
        return result

    def add_query(self, query):
        self._queries.append(query)
