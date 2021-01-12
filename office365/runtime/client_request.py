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
        self._current_query = None
        self.beforeExecute = EventHandler()
        self.afterExecute = EventHandler()

    def __iter__(self):
        for qry in self._queries:
            yield qry

    @property
    def context(self):
        return self._context

    @property
    def current_query(self):
        """
        :rtype: office365.runtime.queries.client_query.ClientQuery
        """
        return self._current_query

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
        self._current_query = query

    def remove_query(self, query):
        self._queries.remove(query)
        self._current_query = None

    @abstractmethod
    def build_request(self):
        """
        :rtype: office365.runtime.http.request_options.RequestOptions
        """
        pass

    @abstractmethod
    def process_response(self, response):
        """
        :type response: requests.Response
        """
        pass

    def execute_query(self):
        """Submit a pending request to the server"""
        while self.next_query():
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

        :type request_options: office365.runtime.http.request_options.RequestOptions
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

    def next_query(self):
        list(iter(self))
        if len(self._queries) == 0:
            self._current_query = None
        else:
            self._current_query = self._queries.pop(0)
        return self._current_query is not None
