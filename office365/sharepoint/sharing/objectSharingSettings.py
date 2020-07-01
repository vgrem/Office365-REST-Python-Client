from office365.runtime.resource_path import ResourcePath
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.sharing.objectSharingInformation import ObjectSharingInformation


class ObjectSharingSettings(BaseEntity):

    @property
    def web_url(self):
        """

        :return: str
        """
        return self.properties.get("WebUrl", None)

    @property
    def object_sharing_information(self):
        return self.properties.get("ObjectSharingInformation",
                                   ObjectSharingInformation(self.context,
                                                            ResourcePath("ObjectSharingInformation",
                                                                         self.resource_path)))
