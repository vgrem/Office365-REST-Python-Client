from office365.runtime.client_value import ClientValue


class XmlSchemaFieldCreationInformation(ClientValue):

    def __init__(self, schemaXml=None, options=None):
        """
        :type schemaXml: str
        :type options: int or None
        """
        super(XmlSchemaFieldCreationInformation, self).__init__()
        self.SchemaXml = schemaXml
        self.Options = options

    @property
    def entity_type_name(self):
        return "SP.XmlSchemaFieldCreationInformation"
