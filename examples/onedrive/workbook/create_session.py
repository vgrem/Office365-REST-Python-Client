from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException


def ensure_workbook_sample(graph_client):
    """
    :type graph_client: GraphClient
    """
    try:
        return graph_client.me.drive.root.get_by_path("Financial Sample.xlsx").workbook.get().execute_query()
    except ClientRequestException as e:
        if e.response.status_code == 404:
            local_path = "../../data/Financial Sample.xlsx"
            target_file = graph_client.me.drive.root.resumable_upload(local_path).execute_query()
            print(f"File {target_file.web_url} has been uploaded")
            return target_file.workbook
        else:
            raise ValueError(e.response.text)


client = GraphClient(acquire_token_by_username_password)
workbook = ensure_workbook_sample(client)

result = workbook.create_session().execute_query()
result_new = workbook.refresh_session(result.value.id).execute_query()
workbook.close_session(result.value.id).execute_query()
