from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.taxonomy.item import TaxonomyItem
from office365.sharepoint.taxonomy.terms.label import Label


class Term(TaxonomyItem):
    """Represents a Term or a Keyword in a managed metadata hierarchy."""

    @property
    def labels(self):
        """Gets a collection of Label objects for the current Term object."""
        return self.properties.get("labels", ClientValueCollection(Label))
