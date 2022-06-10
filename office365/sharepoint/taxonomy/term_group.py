from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.taxonomy.item import TaxonomyItem, TaxonomyItemCollection
from office365.sharepoint.taxonomy.term_set import TermSet


class TermGroup(TaxonomyItem):
    """Represents the top-level container in a TermStore object."""

    @property
    def term_sets(self):
        return self.properties.get("termSets",
                                   TaxonomyItemCollection(self.context, TermSet,
                                                          ResourcePath("termSets", self.resource_path)))

    def get_property(self, name, default_value=None):
        if name == "termSets":
            default_value = self.term_sets
        return super(TermGroup, self).get_property(name, default_value)
