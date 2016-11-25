class ODataPathParser(object):
    @staticmethod
    def parse_path_string(string):
        pass

    @staticmethod
    def from_method(method_name, method_parameters):
        url = ""
        if method_name:
            url = method_name

        url += "("
        if method_parameters:
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
            value = "'{0}'".format(value)
        elif isinstance(value, bool):
            value = str(value).lower()
        return value
