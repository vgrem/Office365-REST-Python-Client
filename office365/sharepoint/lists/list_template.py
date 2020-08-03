from office365.sharepoint.base_entity import BaseEntity


class ListTemplate(BaseEntity):

    def __init__(self, context):
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
        super().__init__(context)

    @property
    def internalName(self):
        """Gets a value that specifies the identifier for the list template.
        :rtype: str or None
        """
        return self.properties.get('InternalName', None)
