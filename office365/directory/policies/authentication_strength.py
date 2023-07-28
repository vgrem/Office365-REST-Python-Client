from office365.entity import Entity


class AuthenticationStrengthPolicy(Entity):
    """
    A collection of settings that define specific combinations of authentication methods and metadata.
    The authentication strength policy, when applied to a given scenario using Azure AD Conditional Access,
    defines which authentication methods must be used to authenticate in that scenario. An authentication strength
    may be built-in or custom (defined by the tenant) and may or may not fulfill the requirements to grant an MFA claim.
    """
