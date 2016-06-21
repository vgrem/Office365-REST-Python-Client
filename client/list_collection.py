from client_object_collection import ClientObjectCollection
from list import List
from client.runtime.client_action_type import ClientActionType
from client.runtime.client_query import ClientQuery


class ListCollection(ClientObjectCollection):
    """Lists collection"""

    def get_by_title(self, list_title):
        """Retrieve List client object by title"""
        return List(self.context, "getbytitle('{0}')".format(list_title), self.resource_path)

    def get_by_id(self, list_id):
        """Retrieve List client object by id"""
        return List(self.context, "getbyid('{0}')".format(list_id), self.resource_path)

    def ensure_site_assets_library(self):
        """Gets a list that is the default asset location for images or other files, which the users
        upload to their wiki pages."""
        list_site_assets = List(self.context)
        qry = ClientQuery(self.url + "/ensuresiteassetslibrary", ClientActionType.Update)
        self.context.add_query(qry, list_site_assets)
        return list_site_assets

    def ensure_site_pages_library(self):
        """Gets a list that is the default location for wiki pages."""
        list_site_pages = List(self.context)
        qry = ClientQuery(self.url + "/ensuresitepageslibrary", ClientActionType.Update)
        self.context.add_query(qry, list_site_pages)
        return list_site_pages

    def add(self, list_creation_information):
        """Creates a List resource"""
        payload = list_creation_information.metadata
        list_new = List(self.context)
        qry = ClientQuery.create_create_query(self.url, payload)
        self.context.add_query(qry, list_new)
        self.add_child(list_new)
        return list_new
