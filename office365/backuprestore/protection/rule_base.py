from office365.entity import Entity


class ProtectionRuleBase(Entity):
    """Represents a protection rule specified by the client as part of a protection plan applied to
    Microsoft 365 data in an organization. Currently, only inclusion rules, which are rules that indicate
    that a protection policy should match the specified criteria, can be defined.

    Currently, protection Rules are static in nature, meaning policy changes are applied only when the
    rule is executed, with no automatic/dynamic updates."""
