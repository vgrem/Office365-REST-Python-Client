import xml.etree.ElementTree as ET
from abc import ABCMeta, abstractmethod

from office365.runtime.odata.odata_model import ODataModel


class ODataBaseReader(object):
    """OData reader"""
    def __init__(self):
        pass

    __metaclass__ = ABCMeta

    @abstractmethod
    def generate_model(self):
        pass
