from office365.entity import Entity
from office365.runtime.client_result import ClientResult
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.service_operation import ServiceOperationQuery


class Attachment(Entity):
    """A file or item (contact, event or message) attached to an event or message."""

    def download(self, file_object):
        """Downloads raw contents of a file or item attachment

        :type file_object: typing.IO
        """
        result = self.get_content()

        def _content_downloaded(resp):
            """
            :type resp: requests.Response
            """
            resp.raise_for_status()
            file_object.write(result.value)

        self.context.after_execute(_content_downloaded)
        return self

    def get_content(self):
        """
        Gets the raw contents of a file or item attachment
        """
        result = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "$value", None, None, None, result)

        def _construct_query(request):
            """
            :type request: office365.runtime.http.request_options.RequestOptions
            """
            request.method = HttpMethod.Get

        self.context.before_execute(_construct_query)
        self.context.add_query(qry)
        return result

    @property
    def name(self):
        """
        The attachment's file name.
        :rtype: str or None
        """
        return self.properties.get("name", None)

    @name.setter
    def name(self, value):
        """
        Sets the attachment's file name.
        :type: value: str
        """
        self.set_property("name", value)

    @property
    def content_type(self):
        """
        :rtype: str or None
        """
        return self.properties.get("contentType", None)

    @content_type.setter
    def content_type(self, value):
        """
        :type: value: str
        """
        self.set_property("contentType", value)

    @property
    def size(self):
        """

        :rtype: int or None
        """
        return self.properties.get("size", None)

    @property
    def last_modified_date_time(self):
        """
        The Timestamp type represents date and time information using ISO 8601 format and is always in UTC time.

        :rtype: int or None
        """
        return self.properties.get("lastModifiedDateTime", None)
