from office365.runtime.client_value import ClientValue


class SignInStatus(ClientValue):
    """Provides the sign-in status (Success or Failure) of the sign-in."""
    def __init__(self, additional_details=None, error_code=None, failure_reason=None):
        super(SignInStatus, self).__init__()
        self.additionalDetails = additional_details
        self.errorCode = error_code
        self.failureReason = failure_reason
