from office365.runtime.client_value import ClientValue
from office365.runtime.client_value_collection import ClientValueCollection


class EmailProperties(ClientValue):

    def __init__(self, body, subject, to, from_address=None, cc=None, bcc=None, additional_headers=None):
        """

        :param str body:
        :param str subject:
        :param list[str] to:
        :param str or None from_address:
        :param list[str] or None cc:
        :param list[str] or None bcc:
        :param dict or None additional_headers:
        """
        super(EmailProperties, self).__init__()
        self.Body = body
        self.Subject = subject
        self.From = from_address
        self.To = ClientValueCollection(str, to)
        self.CC = ClientValueCollection(str, cc)
        self.BCC = ClientValueCollection(str, bcc)
        self.AdditionalHeaders = additional_headers

    @property
    def entity_type_name(self):
        return "SP.Utilities.EmailProperties"
