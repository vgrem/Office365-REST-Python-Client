from abc import ABCMeta, abstractmethod


class BaseTokenProvider(object):
    """ Base token provider"""
    __metaclass__ = ABCMeta

    @abstractmethod
    def acquire_token(self, parameters):
        pass

    @abstractmethod
    def is_authenticated(self):
        pass
