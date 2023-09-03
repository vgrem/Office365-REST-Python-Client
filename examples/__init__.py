def upload_sample_files(drive):
    """
    :type drive: office365.onedrive.drives.drive.Drive
    """
    local_paths = ["../../data/Financial Sample.xlsx"]
    for local_path in local_paths:
        file = drive.root.resumable_upload(local_path).get().execute_query()
        print(f"File {file.web_url} has been uploaded")


