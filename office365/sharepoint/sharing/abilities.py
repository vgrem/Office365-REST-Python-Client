from office365.runtime.client_value import ClientValue


class SharingAbilities(ClientValue):
    """
    Represents the matrix of possible sharing abilities for direct sharing and tokenized sharing links along
    with the state of each capability for the current user.
    """

    @property
    def entity_type_name(self):
        return "SP.Sharing.SharingAbilities"
