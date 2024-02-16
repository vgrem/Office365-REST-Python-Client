from faker import Faker

from office365.sharepoint.client_context import ClientContext
from tests import test_team_site_url, test_user_credentials


def print_progress(items_count):
    print("{0} list items has been created".format(items_count))


def load_data_source(amount=1000):
    fake = Faker()
    contacts = []
    for idx in range(0, amount):
        contact = {
            "Title": fake.name(),
            "FullName": fake.name(),
            "Email": fake.email(),
            "Company": fake.company(),
            "WorkPhone": fake.phone_number(),
            "WorkAddress": fake.street_address(),
            "WorkCity": fake.city(),
            "WorkZip": fake.postcode(),
            "WorkCountry": fake.country()
            # "WebPage": {"Url": fake.url()},
        }
        contacts.append(contact)

    return contacts


def run(context):
    # type: (ClientContext) -> None
    contacts_data = load_data_source()
    contacts_list = context.web.lists.get_by_title("Contacts_Large")
    for idx, contact in enumerate(contacts_data):
        # contact_item = contacts_list.add_item(contact).execute_query()
        contacts_list.add_item(contact)
        # print(
        #    "({0} of {1}) Contact '{2}' has been created".format(
        #        idx, len(contacts_data), contact_item.properties["Title"]
        #    )
        # )
    ctx.execute_batch(items_per_batch=2, success_callback=print_progress)


if __name__ == "__main__":
    ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)
    run(ctx)
