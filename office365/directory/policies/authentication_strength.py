from office365.directory.authentication.strength_usage import (
    AuthenticationStrengthUsage,
)
from office365.entity import Entity
from office365.runtime.client_result import ClientResult
from office365.runtime.queries.function import FunctionQuery


class AuthenticationStrengthPolicy(Entity):
    """
    A collection of settings that define specific combinations of authentication methods and metadata.
    The authentication strength policy, when applied to a given scenario using Azure AD Conditional Access,
    defines which authentication methods must be used to authenticate in that scenario. An authentication strength
    may be built-in or custom (defined by the tenant) and may or may not fulfill the requirements to grant an MFA claim.
    """

    def usage(self):
        """
        Allows the caller to see which Conditional Access policies reference a specified authentication strength policy.
        The policies are returned in two collections, one containing Conditional Access policies that require an
        MFA claim and the other containing Conditional Access policies that do not require such a claim.
        Policies in the former category are restricted in what kinds of changes may be made to them to prevent
        undermining the MFA requirement of those policies.
        """
        return_type = ClientResult(self.context, AuthenticationStrengthUsage())
        qry = FunctionQuery(self, "usage", None, return_type)
        self.context.add_query(qry)
        return return_type
