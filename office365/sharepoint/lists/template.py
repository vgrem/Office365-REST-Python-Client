from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.base_entity import BaseEntity


class ListTemplate(BaseEntity):
    """
    Represents a list definition or a list template, which defines the fields and views for a list.
    List definitions are contained in files within
    \\Program Files\\Common Files\\Microsoft Shared\\Web Server Extensions\\12\\TEMPLATE\\FEATURES,
    but list templates are created through the user interface or through the object model when a list is
    saved as a template.
    Use the Web.ListTemplates property (section 3.2.5.143.1.2.13) to return a ListTemplateCollection
    (section 3.2.5.92) for a site collection. Use an indexer to return a single list definition or
    list template from the collection.
    """

    def get_global_schema_xml(self):
        """Retrieves the global schema.xml file."""
        return_type = ClientResult(self.context)
        qry = ServiceOperationQuery(self, "GetGlobalSchemaXml", None, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    @property
    def internal_name(self):
        """Gets a value that specifies the identifier for the list template.

        :rtype: str or None
        """
        return self.properties.get('InternalName', None)

    def set_property(self, name, value, persist_changes=True):
        super(ListTemplate, self).set_property(name, value, persist_changes)
        if self._resource_path is None:
            if name == "Name":
                self._resource_path = ServiceOperationPath(
                    "GetByName", [value], self._parent_collection.resource_path)
        return self
