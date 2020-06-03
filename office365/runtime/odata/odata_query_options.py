def _normalize(key, value):
    if key == "select" or key == "expand":
        return ",".join(value)
    return value


class QueryOptions(object):
    """OData query options"""

    def __init__(self):
        self.select = None  # type: list or None
        self.expand = None  # type: list or None
        self.filter = None  # type: str or None
        self.orderBy = None  # type: str or None
        self.skip = None  # type: int or None
        self.top = None  # type: int or None

    @property
    def is_empty(self):
        result = {k: v for (k, v) in self.__dict__.items() if v is not None}
        return not result

    def to_url(self):
        """Convert query options to url
        :return: str
        """
        return '&'.join(['$%s=%s' % (key, _normalize(key, value))
                         for (key, value) in self.__dict__.items() if value is not None])
