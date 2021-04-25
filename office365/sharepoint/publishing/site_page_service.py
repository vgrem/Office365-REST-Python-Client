from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.administration.org_assets import OrgAssets
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.files.file import File
from office365.sharepoint.publishing.file_picker_options import FilePickerOptions
from office365.sharepoint.publishing.primary_city_time import PrimaryCityTime
from office365.sharepoint.publishing.site_page_metadata_collection import SitePageMetadataCollection


class SitePageService(BaseEntity):

    def __init__(self, context):
        """Represents a set of APIs to use for managing site pages."""
        super().__init__(context, ResourcePath("SP.Publishing.SitePageService"))

    def pages(self):
        return self.properties.get("pages",
                                   SitePageMetadataCollection(self.context, ResourcePath("pages", self.resource_path)))

    @property
    def entity_type_name(self):
        return "SP.Publishing.SitePageService"

    @staticmethod
    def get_time_zone(context, city_name):
        """
        Gets time zone data for specified city.

        :param office365.sharepoint.client_context.ClientContext context:
        :param str city_name: The name of the city.
        :return: PrimaryCityTime
        """
        return_type = PrimaryCityTime(context)
        svc = SitePageService(context)
        params = {"cityName": city_name}
        qry = ServiceOperationQuery(svc, "GetTimeZone", params, None, None, return_type)
        qry.static = True
        context.add_query(qry)
        return return_type

    @staticmethod
    def compute_file_name(context, title):
        """

        :param office365.sharepoint.client_context.ClientContext context: Client context
        :param str title: The title of the page.
        """
        return_type = ClientResult(context)
        svc = SitePageService(context)
        params = {"title": title}
        qry = ServiceOperationQuery(svc, "ComputeFileName", params, None, None, return_type)
        qry.static = True
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_available_full_page_applications():
        pass

    @staticmethod
    def get_current_user_memberships():
        pass

    @staticmethod
    def is_file_picker_external_image_search_enabled():
        pass

    @staticmethod
    def org_assets(context):
        """

        :param office365.sharepoint.client_context.ClientContext context: Client context
        """
        return_type = OrgAssets()
        svc = SitePageService(context)
        qry = ServiceOperationQuery(svc, "OrgAssets", None, None, None, return_type)
        qry.static = True
        context.add_query(qry)
        return return_type

    @staticmethod
    def file_picker_tab_options(context):
        """

        :param office365.sharepoint.client_context.ClientContext context: Client context
        """
        return_type = FilePickerOptions()
        svc = SitePageService(context)
        qry = ServiceOperationQuery(svc, "FilePickerTabOptions", None, None, None, return_type)
        qry.static = True
        context.add_query(qry)
        return return_type

    def add_image(self, page_name, image_file_name, image_stream):
        """
        Adds an image to the site assets library of the current web.
        Returns a File object ([MS-CSOMSPT] section 3.2.5.64) that represents the image.

        :param str image_stream: The image stream.
        :param str image_file_name: Indicates the file name of the image to be added.
        :param str page_name: Indicates the name of that site page that the image is to be used in.
        :return: File
        """
        return_type = File(self.context)
        params = {"pageName": page_name, "imageFileName": image_file_name, "imageStream": image_stream}
        qry = ServiceOperationQuery(self, "AddImage", params, None, None, return_type)
        qry.static = True
        self.context.add_query(qry)
        return return_type
