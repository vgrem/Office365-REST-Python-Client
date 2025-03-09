from office365.entity import Entity


class FeatureRolloutPolicy(Entity):
    """
    Represents a feature rollout policy associated with a directory object. Creating a feature rollout policy
    helps tenant administrators to pilot features of Microsoft Entra ID with a specific group before enabling
    features for entire organization. This minimizes the impact and helps administrators to test and rollout
    authentication related features gradually.

    The following are limitations of feature rollout:

     - Each feature supports a maximum of 10 groups.
     - The appliesTo field only supports groups.
     - Dynamic groups and nested groups are not supported.
    """
