from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.sharepoint.publishing.site_page_metadata import SitePageMetadata


class SitePage(SitePageMetadata):
    """Represents a site Page."""

    def checkout_page(self):
        """Checks out the current Site Page if it is available to be checked out."""
        site_page = SitePage(self.context)
        qry = ServiceOperationQuery(self, "CheckoutPage", None, None, None, site_page)
        self.context.add_query(qry)
        return site_page

    def copy(self):
        """Creates a copy of the current Site Page and returns the resulting new SitePage."""
        qry = ServiceOperationQuery(self, "Copy", None, None, None, None)
        self.context.add_query(qry)
        return self

    def discard_page(self):
        """Discards the current checked out version of the Site Page.  Returns the resulting SitePage after discard."""
        qry = ServiceOperationQuery(self, "DiscardPage", None, None, None, None)
        self.context.add_query(qry)
        return self

    def save_page(self, page_stream):
        """
        Updates the current Site Page with the provided pageStream content.

        :param str page_stream: The binary stream to save for the current Site Page.
        :return:
        """
        pass

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
        pass

    def share_page_preview_by_email(self, message, recipient_emails):
        pass
