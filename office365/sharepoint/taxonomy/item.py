from office365.runtime.client_object import ClientObject
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.taxonomy.item_collection import TaxonomyItemCollection


class TaxonomyItem(ClientObject):
    """The TaxonomyItem class is a base class that represents an item in the TermStore (section 3.1.5.23).
    A TaxonomyItem has a name and a unique identifier. It also contains date and time of when the item is created and
    when the item is last modified."""

    def search_term(self, label, set_id=None, parent_term_id=None, language_tag=None):
        """

        :param str label:
        :param str set_id:
        :param str or None parent_term_id:
        :param str or None language_tag:
        """
        return_type = TaxonomyItemCollection(self.context, TaxonomyItem, self.resource_path)
        params = {"label": label, "setId": set_id, "parentTermId": parent_term_id, "languageTag": language_tag}
        qry = ServiceOperationQuery(self, "searchTerm", None, params, None, return_type)
        self.context.add_query(qry)

        def _construct_request(request):
            """
            :type request: office365.runtime.http.request_options.RequestOptions
            """
            pass

        self.context.before_execute(_construct_request)
        return return_type

    def set_property(self, name, value, persist_changes=True):
        super(TaxonomyItem, self).set_property(name, value, persist_changes)
        if self._resource_path is None:
            if name == "id":
                self._resource_path = ResourcePath(value, self.parent_collection.resource_path)
        return self


