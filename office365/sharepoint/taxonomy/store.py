from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.collections import StringCollection
from office365.sharepoint.taxonomy.item import TaxonomyItem
from office365.sharepoint.taxonomy.item_collection import TaxonomyItemCollection
from office365.sharepoint.taxonomy.group import TermGroup


class TermStore(TaxonomyItem):
    """Represents a hierarchical or flat set of Term objects known as a 'TermSet'."""

    @property
    def id(self):
        """
        Gets the unique identifier.

        :rtype: str
        """
        return self.properties.get("id", None)

    @property
    def name(self):
        """
        Gets the name

        :rtype: str
        """
        return self.properties.get("name", None)

    @property
    def default_language_tag(self):
        """
        Gets or sets the LCID of the default working language.

        :rtype: str
        """
        return self.properties.get("defaultLanguageTag", None)

    @property
    def language_tags(self):
        """
        Gets an integer collection of LCIDs.
        """
        return self.properties.get("languageTags", StringCollection())

    @property
    def term_groups(self):
        """Gets a collection of the child Group objects"""
        return self.properties.get("termGroups",
                                   TaxonomyItemCollection(self.context, TermGroup,
                                                          ResourcePath("termGroups", self.resource_path)))

    def get_property(self, name, default_value=None):
        if name == "termGroups":
            default_value = self.term_groups
        elif name == "languageTags":
            default_value = self.language_tags
        return super(TermStore, self).get_property(name, default_value)
