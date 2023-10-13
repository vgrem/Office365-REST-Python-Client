from office365.onedrive.drives.drive import Drive


def upload_sample_files(drive):
    # type: (Drive) -> None
    local_paths = ["../../data/Financial Sample.xlsx"]
    for local_path in local_paths:
        file = drive.root.resumable_upload(local_path).get().execute_query()
        print("File {0} has been uploaded", file.web_url)
