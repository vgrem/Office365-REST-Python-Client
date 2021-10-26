from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.sharepoint.publishing.site_page_fields_data import SitePageFieldsData
from office365.sharepoint.publishing.site_page_metadata import SitePageMetadata


class SitePage(SitePageMetadata):
    """Represents a Site Page."""

    def checkout_page(self):
        """Checks out the current Site Page if it is available to be checked out."""
        site_page = SitePage(self.context)
        qry = ServiceOperationQuery(self, "CheckoutPage", None, None, None, site_page)
        self.context.add_query(qry)
        return site_page

    def copy(self):
        """Creates a copy of the current Site Page and returns the resulting new SitePage."""
        qry = ServiceOperationQuery(self, "Copy")
        self.context.add_query(qry)
        return self

    def discard_page(self):
        """Discards the current checked out version of the Site Page.  Returns the resulting SitePage after discard."""
        qry = ServiceOperationQuery(self, "DiscardPage")
        self.context.add_query(qry)
        return self

    def save_page(self, page_stream):
        """
        Updates the current Site Page with the provided pageStream content.

        :param str page_stream: The binary stream to save for the current Site Page.
        :return:
        """
        pass

    def save_draft(self, title, canvas_content=None, topic_header=None):
        """
        Updates the Site Page with the provided sitePage metadata and checks in a minor version if the page library
        has minor versions enabled.

        :param str title: The title of Site Page
        :param str canvas_content:
        :param str topic_header:
        """
        payload = SitePageFieldsData(title=title, canvas_content=canvas_content, topic_header=topic_header)
        result = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "SaveDraft", None, payload, "sitePage", result)
        self.context.add_query(qry)
        return result

    def save_page_as_draft(self, page_stream):
        """
        Updates the Site Page with the provided pageStream content and checks in a minor version if the page library
        has minor versions enabled.

        :param str page_stream: The binary stream to save for the current Site Page.
        :return:
        """
        pass

    def save_page_as_template(self):
        pass

    def publish(self):
        """
        Publishes a major version of the current Site Page.  Returns TRUE on success, FALSE otherwise.

        :return:
        """
        result = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "Publish", None, None, None, result)
        self.context.add_query(qry)
        return result

    def share_page_preview_by_email(self, message, recipient_emails):
        pass

    @property
    def canvas_content(self):
        """
        Gets the CanvasContent1 for the current Site Page.

        :rtype: str or None
        """
        return self.properties.get("CanvasContent1", None)

    @canvas_content.setter
    def canvas_content(self, value):
        """
        Sets the CanvasContent1 for the current Site Page.

        :rtype: str or None
        """
        self.set_property("CanvasContent1", value)

    @property
    def layout_web_parts_content(self):
        """
        Gets the LayoutWebPartsContent field for the current Site Page.

        :rtype: str or None
        """
        return self.properties.get("LayoutWebpartsContent", None)

    @layout_web_parts_content.setter
    def layout_web_parts_content(self, value):
        """
        Sets the LayoutWebPartsContent field for the current Site Page.

        :rtype: str or None
        """
        self.set_property("LayoutWebpartsContent", value)

    @property
    def entity_type_name(self):
        return "SP.Publishing.SitePage"
