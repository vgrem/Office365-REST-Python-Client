from office365.directory.policies.base import PolicyBase


class AuthorizationPolicy(PolicyBase):
    """Represents a policy that can control Azure Active Directory authorization settings.
    It's a singleton that inherits from base policy type, and always exists for the tenant."""
