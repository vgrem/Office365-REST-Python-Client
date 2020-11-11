from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.taxonomy.termStore import TermStore


class TaxonomyService(BaseEntity):
    """Wraps all of the associated TermStore objects for an Site object."""

    def __init__(self, context):
        super().__init__(context, ResourcePath("v2.1"))

    @property
    def term_store(self):
        return self.properties.get("termStore",
                                   TermStore(self.context, ResourcePath("termStore", self.resource_path)))
