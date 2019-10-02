from abc import ABCMeta, abstractmethod


class BaseTokenProvider(object):
    """ Base Token provide"""
    __metaclass__ = ABCMeta

    @abstractmethod
    def acquire_token(self, parameters):
        pass
