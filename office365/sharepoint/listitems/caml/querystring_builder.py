import logging

from office365.sharepoint.listitems.caml.utils import to_camel

logger = logging.getLogger(__name__)


class QueryStringBuilder:
    """
    Helper Class to Build querystring for sharepoint's API

    querystring = QueryStringBuilder(filters).get_querystring()
    folder = self.get_folder('folder_name')
    files = folder.files.filter(querystring)

    examples:
    dict()                                      => ''
    {'name': 'toro'}                            => "Name eq 'toro'
    {'name__not': 'toro'}                       => "Name ne 'toro'
    {'name__contains': 'toro'}                  => "substringof('toro', Name)
    {'name': 'toro,loco'}                       => "(Name eq 'toro' or Name eq 'loco')
    {'date__gt': '2019-10-10'}                  => "Date gt datetime'2019-10-10T00:00:00Z'
    {'date__gte': '2019-10-10'}                 => "Date ge datetime'2019-10-10T00:00:00Z'
    {'date__lt': '2019-10-10'}                  => "Date lt datetime'2019-10-10T00:00:00Z'
    {'date__lte': '2019-10-10'}                 => "Date le datetime'2019-10-10T00:00:00Z'
    """
    date_operators = ['ge', 'gt', 'le', 'lt']
    mapping_operator = {
        'gte': 'ge',
        'gt': 'gt',
        'lte': 'le',
        'lt': 'lt',
        'not': 'ne',
        'contains': 'substringof'
    }
    search = []
    filters = {}

    def __init__(self, filters):
        super().__init__()
        if filters:
            self.filters = filters

    def get_filter_querystring(self):
        filter_queries = []
        for filter_name, filter_value in self.filters.items():
            # operator
            querystring_operator = filter_name.split('__')[-1]
            operator = self.mapping_operator.get(querystring_operator, 'eq')
            # filter
            filter_name = to_camel(filter_name.split('__')[0])
            if operator in self.date_operators:
                values = ["{}T00:00:00Z".format(filter_value)]  # 2016-03-26
                query = ' or '.join([f"{filter_name} {operator} datetime'{value}'" for value in values])
            elif operator == 'substringof':
                values = filter_value.split(',')
                query = ' or '.join([f"{operator}('{value}', {filter_name})" for value in values])

            else:
                values = filter_value.split(',')
                query = ' or '.join([f"{filter_name} {operator} '{value}'" for value in values])
                if len(values) > 1:
                    query = f'({query})'
            filter_queries.append(query)
            logger.info(query)
        return str(" and ".join(filter_queries))

    def get_querystring(self):
        return self.get_filter_querystring() or ''
