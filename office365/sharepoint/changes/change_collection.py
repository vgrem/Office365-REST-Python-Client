from office365.runtime.client_object_collection import ClientObjectCollection
from office365.sharepoint.changes.change import Change


class ChangeCollection(ClientObjectCollection):

    def __init__(self, context, resource_path=None):
        super(ChangeCollection, self).__init__(context, Change, resource_path)

    def create_typed_object(self, properties):
        self.resolve_change_type(properties)
        return super(ChangeCollection, self).create_typed_object(properties)

    def resolve_change_type(self, properties):
        """

        :type properties: dict
        """
        from office365.sharepoint.changes.change_user import ChangeUser
        from office365.sharepoint.changes.change_group import ChangeGroup
        from office365.sharepoint.changes.change_list import ChangeList
        from office365.sharepoint.changes.change_web import ChangeWeb
        from office365.sharepoint.changes.change_content_type import ChangeContentType
        from office365.sharepoint.changes.change_alert import ChangeAlert
        from office365.sharepoint.changes.change_field import ChangeField

        if "WebId" in properties:
            self._item_type = ChangeWeb
        elif "UserId" in properties:
            self._item_type = ChangeUser
        elif "GroupId" in properties:
            self._item_type = ChangeGroup
        elif "ListId" in properties:
            self._item_type = ChangeList
        elif "ContentTypeId" in properties:
            self._item_type = ChangeContentType
        elif "AlertId" in properties:
            self._item_type = ChangeAlert
        elif "FieldId" in properties:
            self._item_type = ChangeField
