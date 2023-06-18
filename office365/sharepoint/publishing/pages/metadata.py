from office365.runtime.types.collections import StringCollection
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.publishing.pages.version_info import SitePageVersionInfo
from office365.sharepoint.publishing.user_info import UserInfo


class SitePageMetadata(BaseEntity):
    """Represents the core properties of a Site Page."""

    @property
    def absolute_url(self):
        """Gets the absolute Url of the Site Page.

        :rtype: str or None
        """
        return self.properties.get('AbsoluteUrl', None)

    @property
    def author_byline(self):
        return self.properties.get("AuthorByline", StringCollection())

    @property
    def created_by(self):
        """Specifies the user who created the page."""
        return self.properties.get("CreatedBy", UserInfo())

    @property
    def last_modified_by(self):
        """Gets the user who last modified the current Site Page."""
        return self.properties.get("LastModifiedBy", UserInfo())

    @property
    def comments_disabled(self):
        """
        Indicates if comments are disabled for the current Site Page.

        :rtype: bool or None
        """
        return self.properties.get("CommentsDisabled", None)

    @property
    def banner_image_url(self):
        """Gets the banner image Url.

        :rtype: str or None
        """
        return self.properties.get('BannerImageUrl', None)

    @banner_image_url.setter
    def banner_image_url(self, value):
        """Sets the banner image Url.

        :type value: str
        """
        self.set_property('BannerImageUrl', value)

    @property
    def content_type_id(self):
        """Gets the content type ID of the current Site Page.

        :rtype: str or None
        """
        return self.properties.get('ContentTypeId', None)

    @content_type_id.setter
    def content_type_id(self, value):
        """Sets the content type ID of the current Site Page.

        :type value: str
        """
        self.set_property('ContentTypeId', value)

    @property
    def description(self):
        """Gets the description for the current Site Page.

        :rtype: str or None
        """
        return self.properties.get('Description', None)

    @property
    def does_user_have_edit_permission(self):
        """Indicates if the current user has edit permission to the Site Page.

        :rtype: bool or None
        """
        return self.properties.get('DoesUserHaveEditPermission', None)

    @property
    def file_name(self):
        """Gets the file name of the current Site Page.

        :rtype: str or None
        """
        return self.properties.get('FileName', None)

    @property
    def first_published(self):
        """Datetime of when the site page was initially published.
        The server MUST return Datetime.MinValue (00:00:00:0000000 UTC) when the site page has never been published.

        :rtype: str or None
        """
        return self.properties.get('FirstPublished', None)

    @property
    def is_page_checked_out_to_current_user(self):
        """Indicates if the Site Page is checked out to the current user.

        :rtype: bool or None
        """
        return self.properties.get('IsPageCheckedOutToCurrentUser', None)

    @property
    def version_info(self):
        """Gets the version information for the most recently checked in version of the Site Page."""
        return self.properties.get('VersionInfo', SitePageVersionInfo())

    @property
    def parent_collection(self):
        """
        :rtype: office365.sharepoint.publishing.pages.metadata_collection.SitePageMetadataCollection
        """
        return self._parent_collection

    @property
    def topic_header(self):
        """
        :rtype: str or None
        """
        return self.properties.get('TopicHeader', None)

    @property
    def entity_type_name(self):
        return "SP.Publishing.SitePageMetadata"

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "AuthorByline": self.author_byline,
                "CreatedBy": self.created_by,
                "LastModifiedBy": self.last_modified_by,
                "VersionInfo": self.version_info
            }
            default_value = property_mapping.get(name, None)
        return super(SitePageMetadata, self).get_property(name, default_value)

    def set_property(self, name, value, persist_changes=True):
        if self._resource_path is None:
            if name == "Id":
                self._resource_path = self.parent_collection.get_by_id(value).resource_path
        return super(SitePageMetadata, self).set_property(name, value, persist_changes)
