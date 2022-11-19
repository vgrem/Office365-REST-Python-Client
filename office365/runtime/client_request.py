from abc import abstractmethod

import requests
from requests import HTTPError

from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.types.event_handler import EventHandler


class ClientRequest(object):

    def __init__(self):
        """
        Abstract request client
        """
        self.beforeExecute = EventHandler()
        self.afterExecute = EventHandler()

    @abstractmethod
    def build_request(self, query):
        """
        Builds a request

        :type query: office365.runtime.queries.client_query.ClientQuery
        :rtype: office365.runtime.http.request_options.RequestOptions
        """
        pass

    def build_custom_request(self, query):
        """
        Builds a request

        :type query: office365.runtime.queries.client_query.ClientQuery
        :rtype: office365.runtime.http.request_options.RequestOptions
        """
        request = self.build_request(query)
        self.beforeExecute.notify(request)
        return request

    @abstractmethod
    def process_response(self, response, query):
        """
        :type response: requests.Response
        :type query: office365.runtime.queries.client_query.ClientQuery
        """
        pass

    def execute_query(self, query):
        """
        Submits a pending request to the server

        :type query: office365.runtime.queries.client_query.ClientQuery
        """
        try:
            request = self.build_request(query)
            response = self.execute_request_direct(request)
            response.raise_for_status()
            self.process_response(response, query)
            self.afterExecute.notify(response)
        except HTTPError as e:
            raise ClientRequestException(*e.args, response=e.response)

    def execute_request_direct(self, request):
        """Execute the client request

        :type request: office365.runtime.http.request_options.RequestOptions
        """
        self.beforeExecute.notify(request)
        if request.method == HttpMethod.Post:
            if request.is_bytes or request.is_file:
                response = requests.post(url=request.url,
                                         headers=request.headers,
                                         data=request.data,
                                         auth=request.auth,
                                         verify=request.verify,
                                         proxies=request.proxies)
            else:
                response = requests.post(url=request.url,
                                         headers=request.headers,
                                         json=request.data,
                                         auth=request.auth,
                                         verify=request.verify,
                                         proxies=request.proxies)
        elif request.method == HttpMethod.Patch:
            response = requests.patch(url=request.url,
                                      headers=request.headers,
                                      json=request.data,
                                      auth=request.auth,
                                      verify=request.verify,
                                      proxies=request.proxies)
        elif request.method == HttpMethod.Delete:
            response = requests.delete(url=request.url,
                                       headers=request.headers,
                                       auth=request.auth,
                                       verify=request.verify,
                                       proxies=request.proxies)
        elif request.method == HttpMethod.Put:
            response = requests.put(url=request.url,
                                    data=request.data,
                                    headers=request.headers,
                                    auth=request.auth,
                                    verify=request.verify,
                                    proxies=request.proxies)
        else:
            response = requests.get(url=request.url,
                                    headers=request.headers,
                                    auth=request.auth,
                                    verify=request.verify,
                                    stream=request.stream,
                                    proxies=request.proxies)
        return response
