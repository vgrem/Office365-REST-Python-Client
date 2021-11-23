from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.taxonomy.taxonomy_item import TaxonomyItem, TaxonomyItemCollection
from office365.sharepoint.taxonomy.term_set import TermSet


class TermGroup(TaxonomyItem):
    """Represents the top-level container in a TermStore object."""

    @property
    def term_sets(self):
        return self.properties.get("termSets",
                                   TaxonomyItemCollection(self.context, TermSet,
                                                          ResourcePath("termSets", self.resource_path)))

