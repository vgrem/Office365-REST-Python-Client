from office365.runtime.client_value_object import ClientValueObject


class CamlQuery(ClientValueObject):
    """Specifies a Collaborative Application Markup Language (CAML) query on a list or joined lists."""

    def __init__(self):
        super(CamlQuery, self).__init__()
        self.DatesInUtc = None
        self.FolderServerRelativeUrl = None
        self.ViewXml = None
        self.metadata_type = "SP.CamlQuery"

    @staticmethod
    def create_all_items_query():
        qry = CamlQuery()
        qry.view_xml = "<View Scope=\"RecursiveAll\"><Query></Query></View>"
        return qry

    @staticmethod
    def create_all_folders_query():
        qry = CamlQuery()
        qry.view_xml = "<View Scope=\"RecursiveAll\"><Query>" \
                       "<Where><Eq><FieldRef Name=\"FSObjType\" /><Value Type=\"Integer\">1</Value></Eq></Where>" \
                       "</Query></View>"
        return qry

    @property
    def payload(self):
        return {'query': super(CamlQuery, self).payload}
