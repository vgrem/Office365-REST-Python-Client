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
        self._context = context
        self._queries = []
        self.beforeExecute = EventHandler()
        self.afterExecute = EventHandler()

    @property
    def context(self):
        return self._context

    @property
    def queries(self):
        """
        :rtype: list[ClientQuery]
        """
        return self._queries

    def add_query(self, query, to_begin=False):
        """
        :type to_begin: bool
        :type query: office365.runtime.queries.client_query.ClientQuery
        """
        if to_begin:
            self._queries.insert(0, query)
        else:
            self._queries.append(query)

    def remove_query(self, query):
        """
        :type query: office365.runtime.queries.client_query.ClientQuery
        """
        self._queries.remove(query)

    @abstractmethod
    def build_request(self, query):
        """
        :type query: office365.runtime.queries.client_query.ClientQuery
        :rtype: office365.runtime.http.request_options.RequestOptions
        """
        pass

    @abstractmethod
    def process_response(self, response, query):
        """
        :type response: requests.Response
        :type query: office365.runtime.queries.client_query.ClientQuery
        """
        pass

    def execute_query(self, query):
        """Submit a pending request to the server

        :type query: office365.runtime.queries.client_query.ClientQuery
        """
        try:
            request = self.build_request(query)
            self.beforeExecute.notify(request)
            response = self.execute_request_direct(request)
            response.raise_for_status()
            self.process_response(response, query)
            self.afterExecute.notify(response)
        except HTTPError as e:
            raise ClientRequestException(*e.args, response=e.response)

    def execute_request_direct(self, request_options):
        """Execute client request

        :type request_options: office365.runtime.http.request_options.RequestOptions
        """
        self.context.authenticate_request(request_options)
        if request_options.method == HttpMethod.Post:
            if request_options.is_bytes or request_options.is_file:
                response = requests.post(url=request_options.url,
                                         headers=request_options.headers,
                                         data=request_options.data,
                                         auth=request_options.auth,
                                         verify=request_options.verify)
            else:
                response = requests.post(url=request_options.url,
                                         headers=request_options.headers,
                                         json=request_options.data,
                                         auth=request_options.auth,
                                         verify=request_options.verify)
        elif request_options.method == HttpMethod.Patch:
            response = requests.patch(url=request_options.url,
                                      headers=request_options.headers,
                                      json=request_options.data,
                                      auth=request_options.auth,
                                      verify=request_options.verify)
        elif request_options.method == HttpMethod.Delete:
            response = requests.delete(url=request_options.url,
                                       headers=request_options.headers,
                                       auth=request_options.auth,
                                       verify=request_options.verify)
        elif request_options.method == HttpMethod.Put:
            response = requests.put(url=request_options.url,
                                    data=request_options.data,
                                    headers=request_options.headers,
                                    auth=request_options.auth,
                                    verify=request_options.verify)
        else:
            response = requests.get(url=request_options.url,
                                    headers=request_options.headers,
                                    auth=request_options.auth,
                                    verify=request_options.verify,
                                    stream=request_options.stream,
                                    proxies=request_options.proxies)
        return response

    def __iter__(self):
        while len(self._queries) > 0:
            qry = self._queries.pop(0)
            yield qry
