from office365.sharepoint.lists.creation_information import ListCreationInformation
from office365.sharepoint.lists.template_type import ListTemplateType


def create_list(web, title, list_type=ListTemplateType.GenericList):
    """
    :type web: office365.sharepoint.webs.web.Web
    :type title: str
    :type list_type: int
    """
    list_properties = ListCreationInformation(title=title, base_template=list_type)
    return web.lists.add(list_properties)

