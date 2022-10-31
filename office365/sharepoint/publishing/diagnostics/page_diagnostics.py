from office365.runtime.client_value import ClientValue


class PageDiagnostics(ClientValue):

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Publishing.Diagnostics.PageDiagnostics"
