from office365.runtime.http.http_method import HttpMethod


class RequestOptions(object):
    """Request options"""

    def __init__(self, url):
        self.url = url
        self.data = None
        self.headers = {}
        self.auth = None
        self.method = HttpMethod.Get

    def set_header(self, name, value):
        self.headers[name] = value

    def set_headers(self, headers):
        for key in headers:
            self.set_header(key, headers[key])
