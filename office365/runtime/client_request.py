from abc import abstractmethod
import requests
from requests import HTTPError
from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.types.EventHandler import EventHandler


class ClientRequest(object):

    def __init__(self, context):
        """
        Base request for OData/REST service

        :type context: office365.runtime.client_runtime_context.ClientRuntimeContext
        """
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
        """Execute client request

        :type request_options: RequestOptions
        """
        self.context.authenticate_request(request_options)
        if request_options.method == HttpMethod.Post:
            if request_options.is_bytes or request_options.is_file:
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
                                  verify=request_options.verify,
                                  stream=request_options.stream,
                                  proxies=request_options.proxies)
        return result

    def add_query(self, query):
        """
        :type query: ClientQuery

        """
        self._queries.append(query)
