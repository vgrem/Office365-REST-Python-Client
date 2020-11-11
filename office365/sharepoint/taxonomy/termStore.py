from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.taxonomy.termGroupCollection import TermGroupCollection


class TermStore(BaseEntity):
    """Represents a hierarchical or flat set of Term objects known as a 'TermSet'."""

    @property
    def id(self):
        """
        :rtype: str
        """
        return self.properties.get("id", None)

    @property
    def name(self):
        """
        :rtype: str
        """
        return self.properties.get("name", None)

    @property
    def defaultLanguageTag(self):
        """
        :rtype: str
        """
        return self.properties.get("defaultLanguageTag", None)

    @property
    def languageTags(self):
        """
        :rtype: list[str]
         """
        return self.properties.get("languageTags", [])

    @property
    def termGroups(self):
        return self.properties.get("termGroups",
                                   TermGroupCollection(self.context, ResourcePath("termGroups", self.resource_path)))
