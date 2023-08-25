from office365.sharepoint.fields.creation_information import FieldCreationInformation
from office365.sharepoint.fields.type import FieldType
from office365.sharepoint.lists.creation_information import ListCreationInformation
from office365.sharepoint.lists.template_type import ListTemplateType
from tests import create_unique_name


def upload_sample_files(drive):
    """
    :type drive: office365.onedrive.drives.drive.Drive
    """
    local_paths = ["../../data/Financial Sample.xlsx"]
    for local_path in local_paths:
        file = drive.root.resumable_upload(local_path).get().execute_query()
        print(f"File {file.web_url} has been uploaded")


def create_sample_tasks_list(web):
    """
    :type web: office365.sharepoint.webs.web.Web
    """
    list_title = create_unique_name("Tasks N")
    list_create_info = ListCreationInformation(list_title,
                                               None,
                                               ListTemplateType.TasksWithTimelineAndHierarchy)

    return_type = web.lists.add(list_create_info).execute_query()
    field_info = FieldCreationInformation("Manager", FieldType.User)
    return_type.fields.add(field_info).execute_query()
    return return_type
