import os

from faker import Faker

from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_user_credentials


def run(context, amount):
    """
    :type context: ClientContext
    :type amount: int
    """
    lib = context.web.lists.get_by_title("Documents_Archive")
    include_files = False

    fake = Faker()
    for idx in range(0, amount):
        # 1. Create a folder
        folder_name = fake.date()
        target_folder = lib.root_folder.add(folder_name)
        context.execute_query()
        print(
            "({0} of {1}) Folder '{2}' has been created".format(
                idx, amount, target_folder.serverRelativeUrl
            )
        )

        if include_files:
            # 2. Upload a file into a folder
            path = "../../../tests/data/SharePoint User Guide.docx"
            with open(path, "rb") as content_file:
                file_content = content_file.read()
            name = os.path.basename(path)
            target_file = target_folder.upload_file(name, file_content).execute_query()
            print("File '{0}' has been uploaded".format(target_file.serverRelativeUrl))


if __name__ == "__main__":
    ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)
    run(ctx, 100)
