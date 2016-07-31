from abc import abstractmethod, ABCMeta


class BaseTokenProvider(object):
    """ Base Token provide"""
    __metaclass__ = ABCMeta

    @abstractmethod
    def acquire_token(self):
        pass
