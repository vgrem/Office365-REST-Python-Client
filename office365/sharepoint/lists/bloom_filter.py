from __future__ import annotations

from typing import Optional

from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.types.collections import StringCollection
from office365.sharepoint.entity import Entity


class ListBloomFilter(Entity):
    """Specifies a Bloom filter (probabilistic structure for checking the existence of list items)."""

    @property
    def bloom_filter_size(self) -> Optional[int]:
        """The length of the Bloom Filter"""
        return self.properties.get("BloomFilterSize", None)

    @property
    def index_map(self):
        """Specifies a list of bloom indexes for item."""
        return self.properties.get("IndexMap", ClientValueCollection(int))

    @property
    def false_positive_rate(self) -> Optional[float]:
        """Gets the FalsePositiveRate property"""
        return self.properties.get("FalsePositiveRate", None)

    @property
    def hashed_value_set(self) -> StringCollection:
        """Gets the HashedValueSet property"""
        return self.properties.get("HashedValueSet", StringCollection())

    @property
    def item_processed_count(self) -> Optional[int]:
        """Gets the ItemProcessedCount property"""
        return self.properties.get("ItemProcessedCount", None)

    @property
    def k(self) -> Optional[int]:
        """Gets the K property"""
        return self.properties.get("K", None)

    @property
    def last_list_item_id_processed(self) -> Optional[int]:
        """Gets the LastListItemIdProcessed property"""
        return self.properties.get("LastListItemIdProcessed", None)

    @property
    def max_item_count(self) -> Optional[int]:
        """Gets the MaxItemCount property"""
        return self.properties.get("MaxItemCount", None)
