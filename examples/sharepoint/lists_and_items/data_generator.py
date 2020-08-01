import os

from faker import Faker
from settings import settings

from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.lists.list_creation_information import ListCreationInformation
from office365.sharepoint.lists.list_template_type import ListTemplateType


def ensure_list(web, list_properties):
    lists = web.lists.filter("Title eq '{0}'".format(list_properties.Title))
    ctx.load(lists)
    ctx.execute_query()
    if len(lists) == 1:
        return lists[0]
    target_list = web.lists.add(list_properties)
    ctx.execute_query()
    return target_list


def generate_documents(context):
    lib = ensure_list(context.web,
                      ListCreationInformation("Documents_Archive",
                                              None,
                                              ListTemplateType.DocumentLibrary))

    include_files = False

    fake = Faker()
    total_amount = 200
    for idx in range(0, total_amount):
        # 1. Create a folder
        folder_name = fake.date()
        target_folder = lib.rootFolder.add(folder_name)
        context.execute_query()
        print("({0} of {1}) Folder '{2}' has been created".format(idx, total_amount, target_folder.serverRelativeUrl))

        if include_files:
            # 2. Upload a file into a folder
            path = "../../../tests/data/SharePoint User Guide.docx"
            with open(path, 'rb') as content_file:
                file_content = content_file.read()
            name = os.path.basename(path)
            target_file = target_folder.upload_file(name, file_content)
            context.execute_query()
            print("File '{0}' has been uploaded".format(target_file.serverRelativeUrl))


def generate_contacts(context):
    contacts_list = ensure_list(context.web,
                                ListCreationInformation("Contacts_Large",
                                                        None,
                                                        ListTemplateType.Contacts)
                                )

    fake = Faker()
    total_amount = 200
    for idx in range(0, total_amount):
        contact_properties = {
            'Title': fake.name(),
            'FullName': fake.name(),
            'Email': fake.email(),
            'Company': fake.company(),
            'WorkPhone': fake.phone_number(),
            'WorkAddress': fake.street_address(),
            'WorkCity': fake.city(),
            'WorkZip': fake.postcode(),
            'WorkCountry': fake.country(),
            'WebPage': {'Url': fake.url()}
        }
        contact_item = contacts_list.add_item(contact_properties)
        context.execute_query()
        print("({0} of {1}) Contact '{2}' has been created".format(idx, total_amount, contact_item.properties["Title"]))


if __name__ == '__main__':
    ctx = ClientContext.connect_with_credentials("https://mediadev8.sharepoint.com/sites/team",
                                                 UserCredential(settings['user_credentials']['username'],
                                                                settings['user_credentials']['password']))
    # generate_contacts(ctx)
    generate_documents(ctx)
