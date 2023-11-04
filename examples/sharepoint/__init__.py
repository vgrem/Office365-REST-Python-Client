from office365.sharepoint.fields.creation_information import FieldCreationInformation
from office365.sharepoint.fields.type import FieldType
from office365.sharepoint.lists.creation_information import ListCreationInformation
from office365.sharepoint.lists.list import List
from office365.sharepoint.lists.template_type import ListTemplateType
from office365.sharepoint.webs.web import Web
from tests import create_unique_name


def upload_sample_file(context, path):
    """
    :type context: office365.sharepoint.client_context.ClientContext
    :type path: str
    """
    folder = context.web.default_document_library().root_folder
    with open(path, "rb") as f:
        file = folder.files.upload(f).execute_query()
    return file


def create_sample_tasks_list(web):
    # type: (Web) -> List
    list_title = "Company Tasks"

    list_title = create_unique_name("Tasks N")
    list_create_info = ListCreationInformation(
        list_title, None, ListTemplateType.TasksWithTimelineAndHierarchy
    )

    return_type = web.lists.add(list_create_info).execute_query()
    field_info = FieldCreationInformation("Manager", FieldType.User)
    return_type.fields.add(field_info).execute_query()
    return return_type


def configure():
    pass
