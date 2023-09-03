from office365.sharepoint.base_entity import BaseEntity


class PageCopyResponse(BaseEntity):

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Publishing.PageCopyWithAssets.PageCopyResponse"
