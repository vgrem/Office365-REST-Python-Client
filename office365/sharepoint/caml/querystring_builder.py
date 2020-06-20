import logging

from office365.sharepoint.caml.utils import to_camel

logger = logging.getLogger(__name__)


class QueryStringBuilder:
    """class to map web-querystring dictionary to sharepoint-querystring"""
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
