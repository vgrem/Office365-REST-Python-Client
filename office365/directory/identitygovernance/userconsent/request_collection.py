from office365.directory.identitygovernance.userconsent.request import (
    UserConsentRequest,
)
from office365.entity_collection import EntityCollection


class UserConsentRequestCollection(EntityCollection[UserConsentRequest]):
    """AppConsentRequest's collection"""

    def __init__(self, context, resource_path=None):
        super(UserConsentRequestCollection, self).__init__(
            context, UserConsentRequest, resource_path
        )
