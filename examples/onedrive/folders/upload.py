"""
Demonstrates how to upload files from a local folder into OneDrive drive

"""

import os
from os.path import isfile, join

from office365.graph_client import GraphClient
from office365.runtime.client_request_exception import ClientRequestException
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
remote_drive = client.me.drive
local_path = "../../data"

for name in os.listdir(local_path):
    path = join(local_path, name)
    if isfile(path):
        try:
            with open(path, "rb") as local_file:
                uploaded_file = remote_drive.root.upload_file(
                    local_file
                ).execute_query()
            print("File '{0}' uploaded into '{1}'".format(path, uploaded_file.web_url))
        except ClientRequestException as e:
            print(
                "An error occured while uploading a file {0}: {1}".format(
                    path, e.message
                )
            )
