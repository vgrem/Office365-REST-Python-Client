from office365.runtime.client_object import ClientObject


class PhysicalAddress(ClientObject):
    """The physical address of a contact."""

    def __init__(self, context):
        super().__init__(context)
