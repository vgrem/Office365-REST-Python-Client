from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.changes.change import Change


class ChangeCollection(BaseEntityCollection):

    def __init__(self, context, resource_path=None):
        super(ChangeCollection, self).__init__(context, Change, resource_path)

    def set_property(self, name, value, persist_changes=False):
        self.resolve_change_type(value)
        super(ChangeCollection, self).set_property(name, value)

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
        from office365.sharepoint.changes.change_item import ChangeItem

        if "ListId" in properties and "WebId" in properties:
            self._item_type = ChangeList
        elif "ItemId" in properties and "ListId" in properties:
            self._item_type = ChangeItem
        elif "WebId" in properties:
            self._item_type = ChangeWeb
        elif "UserId" in properties:
            self._item_type = ChangeUser
        elif "GroupId" in properties:
            self._item_type = ChangeGroup
        elif "ContentTypeId" in properties:
            self._item_type = ChangeContentType
        elif "AlertId" in properties:
            self._item_type = ChangeAlert
        elif "FieldId" in properties:
            self._item_type = ChangeField
