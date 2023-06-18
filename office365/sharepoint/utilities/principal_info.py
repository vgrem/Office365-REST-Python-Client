from office365.runtime.client_value import ClientValue


class PrincipalInfo(ClientValue):
    """Provides access to information about a principal."""

    def __init__(self, principal_id=None, display_name=None, email=None, login_name=None,
                 department=None, job_title=None):
        """
        :param str principal_id: Specifies an identifier for the principal. It MUST be -1 if the principal
            does not belong to the current site.
        :param str display_name: Specifies the display name of the principal.
        :param str email: Specifies the e-mail address of the principal.
        :param str department: Specifies the department name of the principal.
        :param str job_title: Specifies the job title of the principal.
        :param str login_name: Specifies the login name of the principal.
        """
        self.PrincipalId = principal_id
        self.DisplayName = display_name
        self.Email = email
        self.LoginName = login_name
        self.Department = department
        self.JobTitle = job_title

    @property
    def entity_type_name(self):
        return "SP.Utilities.PrincipalInfo"
