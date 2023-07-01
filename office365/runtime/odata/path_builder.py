import json
import re

from office365.runtime.client_value import ClientValue
from office365.runtime.compat import is_string_type
from office365.runtime.paths.resource_path import ResourcePath


class ODataPathBuilder(object):

    @staticmethod
    def parse(path_str):
        """
        Parses path from a string

        :param str path_str:
        """
        segments = [n for n in re.split(r"[('')]|/", path_str) if n]
        if not segments:
            raise TypeError("Invalid path")
        path = None
        for segment in segments:
            path = ResourcePath(segment, path)
        return path
