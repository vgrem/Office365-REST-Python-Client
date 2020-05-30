from settings import settings
from faker import Faker
from office365.runtime.auth.UserCredential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.list_creation_information import ListCreationInformation
from office365.sharepoint.list_template_type import ListTemplateType


def ensure_list(web, list_properties):
    ctx = web.context
    lists = web.lists.filter("Title eq '{0}'".format(list_properties.Title))
    ctx.load(lists)
    ctx.execute_query()
    if len(lists) == 1:
        return lists[0]
    target_list = web.lists.add(list_properties)
    ctx.execute_query()
    return target_list


def generate_contacts(context):
    contacts_list = ensure_list(context.web,
                                ListCreationInformation("Contacts_Large",
                                                        None,
                                                        ListTemplateType.Contacts)
                                )

    fake = Faker()
    for idx in range(0, 301):
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
        print("Contact '{0}' has been created".format(contact_item.properties["Title"]))


if __name__ == '__main__':
    ctx = ClientContext.connect_with_credentials("https://mediadev8.sharepoint.com/sites/team",
                                                 UserCredential(settings['user_credentials']['username'],
                                                                settings['user_credentials']['password']))
    generate_contacts(ctx)
