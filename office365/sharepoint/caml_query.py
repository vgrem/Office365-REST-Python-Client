from office365.runtime.client_value_object import ClientValueObject


class CamlQuery(ClientValueObject):
    """Specifies a Collaborative Application Markup Language (CAML) query on a list or joined lists."""

    def __init__(self):
        super(CamlQuery, self).__init__()
        self.DatesInUtc = None
        self.FolderServerRelativeUrl = None
        self.ViewXml = None

    @staticmethod
    def create_all_items_query():
        qry = CamlQuery()
        qry.ViewXml = "<View Scope=\"RecursiveAll\"><Query></Query></View>"
        return qry

    @staticmethod
    def create_all_folders_query():
        qry = CamlQuery()
        qry.ViewXml = "<View Scope=\"RecursiveAll\"><Query>" \
                      "<Where><Eq><FieldRef Name=\"FSObjType\" /><Value Type=\"Integer\">1</Value></Eq></Where>" \
                      "</Query></View>"
        return qry

    @staticmethod
    def create_custom_query(query):
        qry = CamlQuery()
        qry.ViewXml = query
        return qry

    def to_json(self, data_format):
        return {"query": super(CamlQuery, self).to_json(data_format)}

    @property
    def typeName(self):
        return 'SP.CamlQuery'
