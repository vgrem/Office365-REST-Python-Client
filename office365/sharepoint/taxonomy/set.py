from office365.runtime.client_value import ClientValue
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.taxonomy.item import TaxonomyItem
from office365.sharepoint.taxonomy.item_collection import TaxonomyItemCollection
from office365.sharepoint.taxonomy.term import Term


class TermSet(TaxonomyItem):

    @property
    def terms(self):
        return self.properties.get("terms",
                                   TaxonomyItemCollection(self.context, Term,
                                                          ResourcePath("terms", self.resource_path)))


class TermSetInfo(ClientValue):
    pass
