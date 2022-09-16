from office365.runtime.client_value import ClientValue


class SPClientSideComponentIdentifier(ClientValue):
    """This identifier uniquely identifies a component."""

    def __init__(self, _id=None, version=None):
        self.id = _id
        self.version = version

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.ClientSideComponent.SPClientSideComponentIdentifier"

