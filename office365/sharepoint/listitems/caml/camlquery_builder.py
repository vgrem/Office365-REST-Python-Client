import logging

from office365.sharepoint.listitems.caml.camlQuery import CamlQuery
from office365.sharepoint.listitems.caml.utils import to_camel

logger = logging.getLogger(__name__)


def recursive_builder(queries, operator='And'):
    if queries:
        query = queries.pop()
        if len(queries) == 0:
            return query
        elif len(queries) == 1:
            last_query = queries.pop()
            return f'<{operator}>' + query + last_query + f'</{operator}>'
        else:
            return f'<{operator}>' + query + recursive_builder(queries, operator) + f'</{operator}>'
    return ''


class CamlQueryBuilder:
    """
    Helper Class to Build CamlQuery objects

    qry = CamlQueryBuilder(filters, scope).get_query()
    list_obj = self.context.web.lists.get_by_title('folder_name')
    items = list_obj.get_items(qry)

    examples:
    dict() => ''
    {'donor': 'Australia'}              => <Eq><FieldRef Name="Donor" /><Value Type="Text">Australia</Value></Eq>
    {'donor__not': 'Australia'}         => <Neq><FieldRef Name="Donor" /><Value Type="Text">Australia</Value></Neq>

    {'recipient_office__contains': 'Afghanistan'} =>
    <Contains><FieldRef Name="RecipientOffice" /><Value Type="Text">Afghanistan</Value></Contains>

    {'report_end_date__gt': '2019-10-10'} =>
    <Gt><FieldRef Name="ReportEndDate" /><Value Type="DateTime">2019-10-10T00:00:00Z</Value></Gt>

    {'report_end_date__gte': '2019-10-10'} =>
    <Geq><FieldRef Name="ReportEndDate" /><Value Type="DateTime">2019-10-10T00:00:00Z</Value></Geq>

    {'report_end_date__lt': '2019-10-10'} =>
    <Lt><FieldRef Name="ReportEndDate" /><Value Type="DateTime">2019-10-10T00:00:00Z</Value></Lt>

    {'report_end_date__lte': '2019-10-10'} =>
    <Leq><FieldRef Name="ReportEndDate" /><Value Type="DateTime">2019-10-10T00:00:00Z</Value></Leq>

    {'report_group': 'Grant,US Gov'} =>
    <Or>
        <Eq><FieldRef Name="ReportGroup" /><Value Type="Text">US Gov</Value></Eq>
        <Eq><FieldRef Name="ReportGroup" /><Value Type="Text">Grant</Value></Eq>
    </Or>

    {'donor': 'Australia', 'recipient_office__contains': 'Afghanistan'},
    <And>
        <Contains><FieldRef Name="RecipientOffice" /><Value Type="Text">Afghanistan</Value></Contains>
        <Eq><FieldRef Name="Donor" /><Value Type="Text">Australia</Value></Eq>
     </And>

    {'donor': 'Australia', 'recipient_office__contains': 'Afghanistan', 'donor_report_category': 'Financial'}
    <And>
        <Eq><FieldRef Name="DonorReportCategory" /><Value Type="Text">Financial</Value></Eq>
        <And>
            <Contains><FieldRef Name="RecipientOffice" /><Value Type="Text">Afghanistan</Value></Contains>
            <Eq><FieldRef Name="Donor" /><Value Type="Text">Australia</Value></Eq>
        </And>
    </And>
    """
    date_operators = ['Geq', 'Gt', 'Leq', 'Lt']
    mapping_operator = {
        'gte': 'Geq',
        'gt': 'Gt',
        'lte': 'Leq',
        'lt': 'Lt',
        'not': 'Neq',
        'contains': 'Contains',
        'eq': 'Eq',
    }

    filters = {}

    def __init__(self, filters, scope=None):
        super().__init__()
        self.scope = scope

        if filters:
            self.filters = filters

    def create_query(self):
        where_condition = ''

        if self.filters.keys():
            filter_queries = []
            for filter_name, filter_value in self.filters.items():
                querystring_operator = filter_name.split('__')[-1]
                operator = self.mapping_operator.get(querystring_operator, 'Eq')

                filter_name = to_camel(filter_name.split('__')[0])
                if operator in self.date_operators:
                    column_type, value = 'DateTime', "{}T00:00:00Z".format(filter_value)  # 2016-03-26
                    query = '<{}><FieldRef Name="{}" /><Value Type="{}">{}</Value></{}>'.format(
                        operator, filter_name, column_type, value, operator)
                elif operator == 'Contains':
                    column_type = 'Text'
                    query = '<{}><FieldRef Name="{}" /><Value Type="{}">{}</Value></{}>'.format(
                            operator, filter_name, column_type, filter_value, operator)
                else:
                    column_type, values = 'Text', filter_value.split(',')
                    queries = ['<{}><FieldRef Name="{}" /><Value Type="{}">{}</Value></{}>'.format(
                        operator, filter_name, column_type, value, operator) for value in values]
                    query = recursive_builder(queries, 'Or')
                filter_queries.append(query)
            where_condition = recursive_builder(filter_queries)
            if len(filter_queries) > 1:
                where_condition = f"<And>{where_condition}</And>"

        scope = f' Scope="{self.scope}"' if self.scope else ''
        query = f'<View{scope}><Query><Where>{where_condition}</Where></Query></View>'
        return query

    def get_query(self):
        return CamlQuery.create_custom_query(self.create_query())
