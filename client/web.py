from client_object import ClientObject
from list_collection import ListCollection
from web_collection import WebCollection
from client.folder_collection import FolderCollection
from client.group_collection import GroupCollection
from client.user_collection import UserCollection
from client.runtime.client_query import ClientQuery


class Web(ClientObject):
    """Web client object. Refer this link https://msdn.microsoft.com/en-us/library/office/dn499819.aspx for a details"""

    def __init__(self, context):
        super(Web, self).__init__(context, "web")

    def update(self, properties_to_update):
        """Update web"""
        payload = {'__metadata': {'type': self.entity_type_name}}
        for key in properties_to_update:
            payload[key] = properties_to_update[key]
        qry = ClientQuery.create_update_query(self, payload)
        self.context.add_query(qry)

    def delete_object(self):
        """Delete web"""
        qry = ClientQuery.create_delete_query(self)
        self.context.add_query(qry)
        # self.removeFromParentCollection()

    @property
    def webs(self):
        """Get child webs"""
        if self.is_property_available('Webs'):
            return self.properties['Webs']
        else:
            return WebCollection(self.context, "webs", self.resource_path)

    @property
    def folders(self):
        """Get folder resources"""
        if self.is_property_available('Folders'):
            return self.properties['Folders']
        else:
            return FolderCollection(self.context, "folders", self.resource_path)

    @property
    def lists(self):
        """Get web list collection"""
        if self.is_property_available('Lists'):
            return self.properties['Lists']
        else:
            return ListCollection(self.context, "lists", self.resource_path)

    @property
    def site_users(self):
        """Get site users"""
        if self.is_property_available('SiteUsers'):
            return self.properties['SiteUsers']
        else:
            return UserCollection(self.context, "siteusers", self.resource_path)

    @property
    def site_groups(self):
        """Gets the collection of groups for the site collection."""
        if self.is_property_available('SiteGroups'):
            return self.properties['SiteGroups']
        else:
            return GroupCollection(self.context, "sitegroups", self.resource_path)
