from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.onedrive.internal.paths.children import ChildrenPath
from office365.onedrive.termstore.localized_label import LocalizedLabel
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath


class TermCollection(EntityCollection):

    def __init__(self, context, resource_path=None, parent_set=None):
        """
        :param office365.onedrive.termstore.set.Set parent_set: The parent set that contains the term
        """
        super(TermCollection, self).__init__(context, Term, resource_path)
        self._parent_set = parent_set

    def add(self, label):
        """Create a new term object.

        :param str label: The name of the label.
        :rtype: Term
        """
        result = ClientResult(self.context, Term(self.context))

        def _set_loaded():
            props = {
                "labels": ClientValueCollection(LocalizedLabel, [LocalizedLabel(label)])
            }
            result.value = super(TermCollection, self).add(**props)

        self._parent_set.ensure_property("id", _set_loaded)
        return result.value


class Term(Entity):
    """Represents a term used in a term store. A term can be used to represent an object which can then
    be used as a metadata to tag content. Multiple terms can be organized in a hierarchical manner within a set."""

    @property
    def created_datetime(self):
        """Timestamp at which the term was created."""
        return self.properties.get('createdDateTime', None)

    @property
    def children(self):
        """Children of current term."""
        return self.properties.get('children',
                                   EntityCollection(self.context, Term, ChildrenPath(self.resource_path, "terms")))

    @property
    def relations(self):
        """To indicate which terms are related to the current term as either pinned or reused."""
        from office365.onedrive.termstore.relation import Relation
        return self.properties.get('relations',
                                   EntityCollection(self.context, Relation,
                                                    ResourcePath("relations", self.resource_path)))

    @property
    def set(self):
        """The set in which the term is created."""
        from office365.onedrive.termstore.set import Set
        return self.properties.get('set', Set(self.context, ResourcePath("set", self.resource_path)))

    @property
    def entity_type_name(self):
        return None
