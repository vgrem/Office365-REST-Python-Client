from office365.runtime.clientValue import ClientValue


class ContentTypeId(ClientValue):

    def __init__(self, stringValue=None):
        """
        Represents the content type identifier (ID) of a content type.

        :param str stringValue: Hexadecimal string value of content type identifier. String value MUST start with "0x".
        """
        super().__init__("SP")
        self.StringValue = stringValue
