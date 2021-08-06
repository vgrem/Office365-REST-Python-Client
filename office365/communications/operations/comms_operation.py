from office365.entity import Entity


class CommsOperation(Entity):
    """
    Represents the status of certain long-running operations.

    This resource can be returned as the response to an action, or as the content of a commsNotification.

    When it is returned as a response to an action, the status indicates whether there will be subsequent notifications.
    If, for example, an operation with status of completed or failed is returned, there will not be any subsequent
    operation via the notification channel.

    If a null operation, or an operation with a status of notStarted or running is returned, subsequent updates will
    come via the notification channel.
    """
    pass
