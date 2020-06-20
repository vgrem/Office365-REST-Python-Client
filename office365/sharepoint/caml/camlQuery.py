from office365.runtime.clientValue import ClientValue
from office365.sharepoint.views.viewScope import ViewScope


class CamlQuery(ClientValue):
    """Specifies a Collaborative Application Markup Language (CAML) query on a list or joined lists."""

    def __init__(self):
        super(CamlQuery, self).__init__()
        self.DatesInUtc = None
        self.FolderServerRelativeUrl = None
        self.ViewXml = None

    @staticmethod
    def parse(query_expr, scope=ViewScope.DefaultValue):
        """
        Construct CamlQuery object from expression
        :type query_expr: str
        :type scope: ViewScope
        """
        qry = CamlQuery()
        qry.ViewXml = "<View Scope=\"{0}\"><Query>{1}</Query></View>".format(scope, query_expr)
        return qry

    @staticmethod
    def create_custom_query(query):
        qry = CamlQuery()
        qry.ViewXml = query
        return qry

    @staticmethod
    def create_all_items_query():
        return CamlQuery.parse("", ViewScope.RecursiveAll)

    @staticmethod
    def create_all_folders_query():
        qry_text = "<Where><Eq><FieldRef Name=\"FSObjType\" /><Value Type=\"Integer\">1</Value></Eq></Where>"
        return CamlQuery.parse(qry_text, ViewScope.RecursiveAll)

    @staticmethod
    def create_all_files_query():
        qry_text = "<Where><Eq><FieldRef Name=\"FSObjType\" /><Value Type=\"Integer\">0</Value></Eq></Where>"
        return CamlQuery.parse(qry_text, ViewScope.RecursiveAll)

    @property
    def entity_type_name(self):
        return 'SP.CamlQuery'
