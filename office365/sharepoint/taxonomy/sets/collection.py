from office365.sharepoint.taxonomy.item_collection import TaxonomyItemCollection
from office365.sharepoint.taxonomy.sets.set import TermSet


class TermSetCollection(TaxonomyItemCollection):

    def __init__(self, context, resource_path=None):
        super(TermSetCollection, self).__init__(context, TermSet, resource_path)

    def __getitem__(self, index):
        """
        :type index: int
        :rtype: TermSet
        """
        return self._data[index]
