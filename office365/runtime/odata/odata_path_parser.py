from requests.compat import basestring


class ODataPathParser(object):
    @staticmethod
    def parse_path_string(string):
        pass

    @staticmethod
    def from_method(method_name, method_parameters=None):
        url = ""
        if method_name:
            url = method_name

        if method_parameters is not None:
            url += "("
            if isinstance(method_parameters, dict):
                url += ','.join(['%s=%s' % (key, ODataPathParser.encode_method_value(value)) for (key, value) in
                                 method_parameters.items()])
            else:
                url += ','.join(['%s' % (ODataPathParser.encode_method_value(value)) for (i, value) in
                                 enumerate(method_parameters)])
            url += ")"
        return url

    @staticmethod
    def encode_method_value(value):
        if isinstance(value, basestring):
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
