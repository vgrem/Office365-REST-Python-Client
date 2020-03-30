def _normalize(key, value):
    if key == "select" or key == "expand":
        return ",".join(value)
    return value


class QueryOptions(object):

    def __init__(self):
        self.select = None
        self.expand = None
        self.filter = None
        self.orderBy = None
        self.skip = None
        self.top = None

    @property
    def is_empty(self):
        result = {k: v for (k, v) in self.__dict__.items() if v is not None}
        return not result

    def to_url(self):
        """Convert query options to url"""
        return '&'.join(['$%s=%s' % (key, _normalize(key, value))
                         for (key, value) in self.__dict__.items() if value is not None])
