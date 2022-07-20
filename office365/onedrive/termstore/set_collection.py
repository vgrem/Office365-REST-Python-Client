from office365.entity_collection import EntityCollection
from office365.onedrive.termstore.localized_name import LocalizedName
from office365.onedrive.termstore.set import Set
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.create_entity import CreateEntityQuery


class SetCollection(EntityCollection):

    def __init__(self, context, resource_path=None, parent_group=None):
        """
        :param office365.onedrive.termstore.group.Group parent_group: The parent group that contains the set
        """
        super(SetCollection, self).__init__(context, Set, resource_path)
        self._parent_group = parent_group

    def add(self, name, parent_group=None):
        """Create a new set object.

        :param office365.onedrive.termstore.group.Group parent_group: The parent group that contains the set.
        :param str name: Default name (in en-US localization).
        """
        return_type = Set(self.context)
        self.add_child(return_type)

        def _group_loaded(set_create_info):
            qry = CreateEntityQuery(self, set_create_info, return_type)
            self.context.add_query(qry)

        if self._parent_group is not None:
            props = {
                "localizedNames": ClientValueCollection(LocalizedName, [LocalizedName(name)])
            }
            self._parent_group.ensure_property("id", _group_loaded, props)
        elif parent_group is not None:
            props = {
                "parentGroup": {"id": parent_group.id},
                "localizedNames": ClientValueCollection(LocalizedName, [LocalizedName(name)])
            }
            parent_group.ensure_property("id", _group_loaded, props)
        else:
            raise TypeError("Parameter 'parent_group' is not set")

        return return_type
