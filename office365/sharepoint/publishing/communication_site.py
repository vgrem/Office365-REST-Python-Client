from office365.runtime.client_result import ClientResult
from office365.runtime.client_value import ClientValue
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity


class CommunicationSiteCreationRequest(ClientValue):

    def __init__(self, title, url, description=None, lcid=None, classification=None,
                 allow_filesharing_for_guest_users=None,
                 web_template_extension_id=None, site_design_id=None):
        """
        :param str title: Site title
        :param str title: Absolute site url
        :param str description:
        """
        self.Title = title
        self.Url = url
        self.Description = description
        self.lcid = lcid
        self.Classification = classification
        self.AllowFileSharingForGuestUsers = allow_filesharing_for_guest_users
        self.WebTemplateExtensionId = web_template_extension_id
        self.SiteDesignId = site_design_id

    @property
    def entity_type_name(self):
        return "SP.Publishing.CommunicationSiteCreationRequest"


class CommunicationSiteCreationResponse(ClientValue):

    def __init__(self, site_status=None, site_url=None):
        self.SiteStatus = site_status
        self.SiteUrl = site_url


class CommunicationSite(BaseEntity):
    """Represents a Communication Site."""

    def create(self, request):
        """
        Initiates creation of a Communication Site.

        - If the SiteStatus returns 1, the Communication Site is in the process of being created asynchronously.

        - If the SiteStatus returns 2 and the SiteUrl returns a non-empty, non-null value, the site was created
        synchronously and is available at the specified URL.

        - If the SiteStatus returns 2 and the SiteUrl returns an empty or null value, the site already exists but is
        inaccessible for some reason, such as being "locked".

        - If the SiteStatus returns 3 or 0, the Communication site failed to be created.

        :param CommunicationSiteCreationRequest request: Options for configuring the Communication Site that will
        be created.
        """
        result = ClientResult(self.context, CommunicationSiteCreationResponse())
        qry = ServiceOperationQuery(self, "Create", None, request, "request", result)
        self.context.add_query(qry)
        return result

    def get_status(self, site_url):
        """
        Retrieves the status of creation of a Communication site.

        If the SiteStatus returned is 0, then no work item for a site with the specified URL was found, and no site was
        found with the specified URL. This could mean either that a creation attempt hasn’t started yet, or that it
        failed with a “non-retryable” exception and did not preserve a work item for further attempts.

        If the SiteStatus returns 1, the Communication Site is in the process of being created asynchronously.

        If the SiteStatus returns 2 and the SiteUrl returns a non-empty, non-null value, the site was created
        synchronously and is available at the specified URL.

        If the SiteStatus returns 2 and the SiteUrl returns an empty or null value, the site already exists but
        is inaccessible for some reason, such as being “locked”.

        If the SiteStatus returns 3 or 0, the Communication site failed to be created.
        """
        response = ClientResult(self.context, CommunicationSiteCreationResponse())
        qry = ServiceOperationQuery(self, "Status", None, {'url': site_url}, None, response)
        self.context.add_query(qry)

        def _construct_status_request(request):
            request.method = HttpMethod.Get
            request.url += "?url='{0}'".format(site_url)

        self.context.before_execute(_construct_status_request)
        return response

    def enable(self, design_package_id):
        qry = ServiceOperationQuery(self, "Enable", None, {"designPackageId": design_package_id})
        self.context.add_query(qry)
        return self

    @property
    def entity_type_name(self):
        return "SP.Publishing.CommunicationSite"
