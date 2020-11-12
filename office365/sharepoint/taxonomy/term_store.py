from office365.runtime.client_object import ClientObject
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.taxonomy.termGroupCollection import TermGroupCollection
from office365.sharepoint.taxonomy.term_collection import TermCollection


class TermStore(ClientObject):
    """Represents a hierarchical or flat set of Term objects known as a 'TermSet'."""

    def search_term(self, label, setId, parentTermId=None, languageTag=None):
        """

        :param str label:
        :param str setId:
        :param str or None parentTermId:
        :param str or None languageTag:
        :return:
        """
        return_type = TermCollection(self.context)
        # params = {"label": label, "setId": setId, "parentTermId": parentTermId, "languageTag": languageTag}
        params = {"label": label, "setId": setId}
        qry = ServiceOperationQuery(self, "searchTerm", params, None, None, return_type)
        self.context.add_query(qry)
        return return_type

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
    def default_language_tag(self):
        """
        :rtype: str
        """
        return self.properties.get("defaultLanguageTag", None)

    @property
    def language_tags(self):
        """
        :rtype: list[str]
         """
        return self.properties.get("languageTags", [])

    @property
    def term_groups(self):
        return self.properties.get("termGroups",
                                   TermGroupCollection(self.context, ResourcePath("termGroups", self.resource_path)))

