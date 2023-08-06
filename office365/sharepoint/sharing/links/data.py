from office365.runtime.client_value import ClientValue


class SharingLinkData(ClientValue):
    """
    This class stores basic overview information about the link URL, including limited data
    about the object the link URL refers to and any additional sharing link data if the link URL
    is a tokenized sharing link.
    """

    def __init__(self, blocks_download=None, description=None, embeddable=None, expiration=None,
                 has_external_guest_invitees=None, is_anonymous=None, is_create_only_link=None,
                 is_forms_link=None):
        """
        :param bool blocks_download:
        :param str description:
        :param bool embeddable:
        :param str expiration: The UTC date/time string with complete representation for calendar date and time of
           day which represents the time and date of expiry for the tokenized sharing link
           (i.e. is not accessible anymore)
        :param bool has_external_guest_invitees: Boolean indicating whether the link URL is a tokenized sharing link
            that has any external guest invitees (external users explicitly invited by email address).
        :param bool is_anonymous: Boolean indicating if the link is anonymously accessible.
        :param bool is_create_only_link:
        :param bool is_forms_link: Indicates if the link URL is a tokenized sharing link that supports forms sharing.
            This is limited to only tokenized sharing links generated with the Excel Survey feature.
        """
        self.BlocksDownload = blocks_download
        self.Description = description
        self.Embeddable = embeddable
        self.Expiration = expiration
        self.HasExternalGuestInvitees = has_external_guest_invitees
        self.IsAnonymous = is_anonymous
        self.IsCreateOnlyLink = is_create_only_link
        self.IsFormsLink = is_forms_link
