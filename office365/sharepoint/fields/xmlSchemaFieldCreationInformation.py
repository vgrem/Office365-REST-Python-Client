from office365.runtime.client_value import ClientValue


class XmlSchemaFieldCreationInformation(ClientValue):

    def __init__(self, schemaXml, options=None):
        """
        :type schemaXml: str
        :type options: int or None
        """
        super().__init__("SP")
        self.SchemaXml = schemaXml
        self.Options = options
