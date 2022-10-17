from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.base_entity import BaseEntity


class ListBloomFilter(BaseEntity):
    """Specifies a Bloom filter (probabilistic structure for checking the existence of list items)."""

    @property
    def bloom_filter_size(self):
        """
        The length of the Bloom Filter

        :rtype: int or None
        """
        return self.properties.get("BloomFilterSize", None)

    @property
    def index_map(self):
        """
        Specifies a list of bloom indexes for item.
        """
        return self.properties.get("IndexMap", ClientValueCollection(int))
