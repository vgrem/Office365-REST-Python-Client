from office365.entity_collection import EntityCollection
from office365.onedrive.sitepages.site_page import SitePage
from office365.onedrive.sitepages.title_area import TitleArea
from office365.runtime.http.request_options import RequestOptions


class SitePageCollection(EntityCollection[SitePage]):
    """Sites container"""

    def __init__(self, context, resource_path=None):
        super(SitePageCollection, self).__init__(context, SitePage, resource_path)

    def add(self, title):
        """
        Create a new sitePage in the site pages list in a site.

        """

        def _construct_request(request):
            # type: (RequestOptions) -> None
            request.set_header("Content-Type", "application/json")

        return (
            super(SitePageCollection, self)
            .add(
                title=title,
                name="{0}.aspx".format(title),
                pageLayout="article",
                titleArea=TitleArea(),
            )
            .before_execute(_construct_request)
        )
