from office365.graph_client import GraphClient
from office365.onedrive.driveitems.driveItem import DriveItem
from office365.onedrive.workbooks.workbook import Workbook
from office365.runtime.client_request_exception import ClientRequestException


def upload_excel_sample(graph_client):
    # type: (GraphClient) -> DriveItem
    local_path = "../../data/Financial Sample.xlsx"
    return graph_client.me.drive.root.upload_file(local_path).execute_query()


def ensure_workbook_sample(graph_client):
    # type: (GraphClient) -> Workbook
    try:
        return (
            graph_client.me.drive.root.get_by_path("Financial Sample.xlsx")
            .workbook.get()
            .execute_query()
        )
    except ClientRequestException as e:
        if e.response.status_code == 404:
            local_path = "../../data/Financial Sample.xlsx"
            target_file = graph_client.me.drive.root.upload_file(
                local_path
            ).execute_query()
            print("File {0} has been uploaded".format(target_file.web_url))
            return target_file.workbook
        else:
            raise ValueError(e.response.text)
