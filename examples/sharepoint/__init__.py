def upload_sample(context, path):
    """
    :type context: office365.sharepoint.client_context.ClientContext
    :type path: str
    """
    folder = context.web.default_document_library().root_folder
    with open(path, 'rb') as f:
        file = folder.files.upload(f).execute_query()
    return file
