from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_query import ServiceOperationQuery, CreateEntityQuery
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.runtime.utilities.http_method import HttpMethod
from office365.sharepoint.list import List


class ListCollection(ClientObjectCollection):
    """Lists collection"""
    def __init__(self, context, resource_path=None):
        super(ListCollection, self).__init__(context, List, resource_path)

    def get_by_title(self, list_title):
        """Retrieve List client object by title"""
        return List(self.context,
                    ResourcePathServiceOperation(self.context, self.resourcePath, "GetByTitle", [list_title]))

    def get_by_id(self, list_id):
        """Retrieve List client object by id"""
        return List(self.context,
                    ResourcePathServiceOperation(self.context, self.resourcePath, "GetById", [list_id]))

    def ensure_site_assets_library(self):
        """Gets a list that is the default asset location for images or other files, which the users
        upload to their wiki pages."""
        list_site_assets = List(self.context)
        qry = ServiceOperationQuery(self, HttpMethod.Post, "ensuresiteassetslibrary")
        self.context.add_query(qry, list_site_assets)
        return list_site_assets

    def ensure_site_pages_library(self):
        """Gets a list that is the default location for wiki pages."""
        list_site_pages = List(self.context)
        qry = ServiceOperationQuery(self, HttpMethod.Post, "ensuresitepageslibrary")
        self.context.add_query(qry, list_site_pages)
        return list_site_pages

    def add(self, list_creation_information):
        """Creates a List resource"""
        list_entry = List(self.context)
        qry = CreateEntityQuery(self, list_creation_information)
        self.context.add_query(qry, list_entry)
        self.add_child(list_entry)
        return list_entry
