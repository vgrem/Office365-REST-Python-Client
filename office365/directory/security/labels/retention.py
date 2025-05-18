from office365.entity import Entity


class RetentionLabel(Entity):
    """
    Represents how organizations, for compliance and governance purposes, can manage their data at an item
    level (email or document), including whether and for how long to retain or delete the item.

     Organizations can use retention labels for different types of content that require different retention settings.
     For example, they can apply a retention label to tax forms and supporting documents to retain them for
     the period required by law.

     Organizations can configure retention labels with the retention periods and actions based on factors such
     as the date last modified or created. They can also start different retention periods by specifying an event
     that can trigger retention when the event occurs.

     For more information on how retention labels work, when to use them, and how Microsoft Purview supports
     retention labels to let you configure retention and deletion settings, see Learn about retention policies and
     retention labels.
    """
