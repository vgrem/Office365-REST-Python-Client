from office365.runtime.client_value import ClientValue
from office365.sharepoint.views.viewScope import ViewScope


class CamlQuery(ClientValue):

    def __init__(self, datesInUtc=True, viewXml=None, listItemCollectionPosition=None,
                 folderServerRelativeUrl=None, allowIncrementalResults=True):
        """
        Specifies a Collaborative Application Markup Language (CAML) query on a list or joined lists.

        :type bool allowIncrementalResults: Specifies whether the incremental results can be returned.
        :param ListItemCollectionPosition listItemCollectionPosition: Specifies the information required to
            get the next page of data for the list view.
        :param str viewXml: Specifies the XML schema that defines the list view.
        :param str or None folderServerRelativeUrl: Specifies the server-relative URL of a list folder from which
            results are to be returned.
        :param bool datesInUtc: Specifies whether the query returns dates in Coordinated Universal Time (UTC) format.
        """
        super(CamlQuery, self).__init__()
        self.DatesInUtc = datesInUtc
        self.FolderServerRelativeUrl = folderServerRelativeUrl
        self.AllowIncrementalResults = allowIncrementalResults
        self.ViewXml = viewXml
        self.ListItemCollectionPosition = listItemCollectionPosition

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
