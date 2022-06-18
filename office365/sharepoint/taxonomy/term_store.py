from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.collections import StringCollection
from office365.sharepoint.taxonomy.item import TaxonomyItem, TaxonomyItemCollection
from office365.sharepoint.taxonomy.term import Term
from office365.sharepoint.taxonomy.term_group import TermGroup


class TermStore(TaxonomyItem):
    """Represents a hierarchical or flat set of Term objects known as a 'TermSet'."""

    def search_term(self, label, set_id, parent_term_id=None, language_tag=None):
        """

        :param str label:
        :param str set_id:
        :param str or None parent_term_id:
        :param str or None language_tag:
        """
        return_type = TaxonomyItemCollection(self.context, Term, self.resource_path)
        params = {"label": label, "setId": set_id, "parentTermId": parent_term_id, "languageTag": language_tag}
        qry = ServiceOperationQuery(self, "searchTerm", params, None, None, return_type)
        self.context.add_query(qry)

        def _construct_request(request):
            """
            :type request: office365.runtime.http.request_options.RequestOptions
            """
            pass

        self.context.before_execute(_construct_request)
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
        return self.properties.get("languageTags", StringCollection())

    @property
    def term_groups(self):
        return self.properties.get("termGroups",
                                   TaxonomyItemCollection(self.context, TermGroup,
                                                          ResourcePath("termGroups", self.resource_path)))

    def get_property(self, name, default_value=None):
        if name == "termGroups":
            default_value = self.term_groups
        elif name == "languageTags":
            default_value = self.language_tags
        return super(TermStore, self).get_property(name, default_value)
