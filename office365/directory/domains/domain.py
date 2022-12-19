from office365.entity import Entity


class Domain(Entity):
    """
    Represents a domain associated with the tenant.

    Use domain operations to associate domains to a tenant, verify domain ownership, and configure supported services.
    Domain operations enable registrars to automate domain association for services such as Microsoft 365.
    For example, as part of domain sign up, a registrar can enable a vanity domain for email, websites,
    authentication, etc.
    """
