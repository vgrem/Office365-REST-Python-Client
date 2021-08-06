from office365.entity import Entity


class GroupLifecyclePolicy(Entity):
    """
    Represents a lifecycle policy for a Microsoft 365 group. A group lifecycle policy allows administrators
    to set an expiration period for groups. For example, after 180 days, a group expires.
    When a group reaches its expiration, owners of the group are required to renew their group within a time interval
    defined by the administrator. Once renewed, the group expiration is extended by the number of days defined
    in the policy. For example, the group's new expiration is 180 days after renewal.
    If the group is not renewed, it expires and is deleted.
    The group can be restored within a period of 30 days from deletion.
    """
    pass
