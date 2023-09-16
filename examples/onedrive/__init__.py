def upload_excel_sample(graph_client):
    """
    :type graph_client: office365.graph_client.GraphClient
    """
    local_path = "../../data/Financial Sample.xlsx"
    return graph_client.me.drive.root.resumable_upload(local_path).execute_query()
