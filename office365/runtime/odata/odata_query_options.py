def _normalize(key, value):
    if key == "select" or key == "expand":
        return ",".join(value)
    return value


class QueryOptions(object):

    def __init__(self, select=None, expand=None, filter_expr=None, orderBy=None, top=None, skip=None):
        """
        A query option is a set of query string parameters applied to a resource that can help control the amount
        of data being returned for the resource in the URL

        :param list[str] select: The $select system query option allows the clients to requests a limited set of
        properties for each entity or complex type.
        :param list[str] expand: The $expand system query option specifies the related resources to be included in
        line with retrieved resources.
        :param str filter_expr: The $filter system query option allows clients to filter a collection of resources
        that are addressed by a request URL.
        :param str orderBy: The $orderby system query option allows clients to request resources in either ascending
        order using asc or descending order using desc
        :param int top: The $top system query option requests the number of items in the queried collection to
        be included in the result.
        :param int skip: The $skip query option requests the number of items in the queried collection that
        are to be skipped and not included in the result.
        """
        if expand is None:
            expand = []
        if select is None:
            select = []
        self.select = select
        self.expand = expand
        self.filter = filter_expr
        self.orderBy = orderBy
        self.skip = skip
        self.top = top

    @property
    def is_empty(self):
        result = {k: v for (k, v) in self.__dict__.items() if v is not None and v}
        return not result

    def to_url(self):
        """Convert query options to url
        :return: str
        """
        return '&'.join(['$%s=%s' % (key, _normalize(key, value))
                         for (key, value) in self.__dict__.items() if value is not None and value])
