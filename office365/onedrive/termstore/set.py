from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.onedrive.internal.paths.children import ChildrenPath
from office365.onedrive.termstore.localized_name import LocalizedName
from office365.onedrive.termstore.relation import Relation
from office365.onedrive.termstore.term import Term, TermCollection
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath


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
        result = ClientResult(self.context, Set(self.context))

        def _group_loaded(set_create_info):
            result.value = super(SetCollection, self).add(**set_create_info)

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

        return result.value


class Set(Entity):
    """
    Represents the set used in a term store. The set represents a unit which contains a collection of hierarchical
    terms. A group can contain multiple sets.
    """

    @property
    def children(self):
        """Children terms of set in term store."""
        return self.properties.get('children',
                                   TermCollection(self.context, ChildrenPath(self.resource_path, "terms"), self))

    @property
    def parent_group(self):
        """The parent group that contains the set."""
        from office365.onedrive.termstore.group import Group
        return self.properties.get('parentGroup',
                                   Group(self.context, ResourcePath("parentGroup", self.resource_path)))

    @property
    def relations(self):
        """Indicates which terms have been pinned or reused directly under the set."""
        return self.properties.get('relations',
                                   EntityCollection(self.context, Relation,
                                                    ResourcePath("relations", self.resource_path)))

    @property
    def terms(self):
        """All the terms under the set."""
        return self.properties.get('terms',
                                   EntityCollection(self.context, Term, ResourcePath("terms", self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "parentGroup": self.parent_group
            }
            default_value = property_mapping.get(name, None)
        return super(Set, self).get_property(name, default_value)

    @property
    def entity_type_name(self):
        return None
