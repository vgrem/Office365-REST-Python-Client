from abc import ABCMeta, abstractmethod


class BaseAuthenticationContext:
    def __init__(self):
        pass

    __metaclass__ = ABCMeta

    @abstractmethod
    def authenticate_request(self, request_options):
        pass
