import json

from office365.runtime.client_value import ClientValue
from office365.runtime.compat import is_string_type


class ODataPathBuilder(object):

    @staticmethod
    def build(name, parameters=None):
        """
        Constructs path segment from operation name and parameters

        :type parameters: list or dict or ClientValue
        :type name: str
        """
        url = name or ""
        if isinstance(parameters, ClientValue):
            url += "(@v)?@v={0}".format(json.dumps(parameters.to_json()))
        elif parameters is not None:
            url += "("
            if isinstance(parameters, dict):
                url += ','.join(['%s=%s' % (key, ODataPathBuilder.encode_method_value(value)) for (key, value) in
                                 parameters.items() if value is not None])
            else:
                url += ','.join(['%s' % (ODataPathBuilder.encode_method_value(value)) for (i, value) in
                                 enumerate(parameters) if value is not None])
            url += ")"
        return url

    @staticmethod
    def encode_method_value(value):
        if is_string_type(value):
            value = value.replace("'", "''")

            # Same replacements as SQL Server
            # https://web.archive.org/web/20150101222238/http://msdn.microsoft.com/en-us/library/aa226544(SQL.80).aspx
            # https://stackoverflow.com/questions/4229054/how-are-special-characters-handled-in-an-odata-query#answer-45883747
            value = value.replace('%', '%25')
            value = value.replace('+', '%2B')
            value = value.replace('/', '%2F')
            value = value.replace('?', '%3F')
            value = value.replace('#', '%23')
            value = value.replace('&', '%26')

            value = "'{0}'".format(value)
        elif isinstance(value, bool):
            value = str(value).lower()
        return value
