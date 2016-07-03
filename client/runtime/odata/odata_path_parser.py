class ODataPathParser(object):
    @staticmethod
    def parse_path_string(string):
        pass

    @staticmethod
    def from_method(method_name, method_parameters):
        url = ""
        if method_name:
            url = method_name

        if method_parameters:
            url + "(" + ','.join(['$%s=%s' % (key, value) for (key, value) in method_parameters.items()]) + ")"

        return url

