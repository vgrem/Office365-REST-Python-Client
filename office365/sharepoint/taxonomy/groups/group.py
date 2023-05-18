from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.taxonomy.item import TaxonomyItem
from office365.sharepoint.taxonomy.item_collection import TaxonomyItemCollection
from office365.sharepoint.taxonomy.sets.set import TermSet


class TermGroup(TaxonomyItem):
    """Represents the top-level container in a TermStore object."""

    @property
    def term_sets(self):
        return self.properties.get("termSets",
                                   TaxonomyItemCollection(self.context, TermSet,
                                                          ResourcePath("termSets", self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "termSets": self.term_sets
            }
            default_value = property_mapping.get(name, None)
        return super(TermGroup, self).get_property(name, default_value)
