from office365.runtime.client_value import ClientValue


class ContentTypeId(ClientValue):

    def __init__(self, string_value=None):
        """
        Represents the content type identifier (ID) of a content type.

        :param str string_value: Hexadecimal string value of content type identifier. String value MUST start with "0x".
        """
        super().__init__("SP")
        self.StringValue = string_value
