from office365.runtime.client_value import ClientValue
from office365.runtime.types.collections import StringCollection


class MessageRulePredicates(ClientValue):
    """Represents the set of conditions and exceptions that are available for a rule."""

    def __init__(self, body_contains=None, body_or_subject_contains=None, categories=None):
        """
        :param list[str] body_contains: Represents the strings that should appear in the body of an incoming message
            in order for the condition or exception to apply.
        :param list[str] body_or_subject_contains: Represents the strings that should appear in the body or subject
             of an incoming message in order for the condition or exception to apply.
        :param list[str] categories: Represents the categories that an incoming message should be labeled with in
             order for the condition or exception to apply.
        """
        self.bodyContains = StringCollection(body_contains)
        self.bodyOrSubjectContains = StringCollection(body_or_subject_contains)
        self.categories = StringCollection(categories)
