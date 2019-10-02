import settings
from faker import Faker

from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext


def generate_tasks(context):
    tasks_list = ctx.web.lists.get_by_title("Tasks")
    for idx in range(0, 10):
        title = "Task{0}".format(idx)
        task_properties = {'__metadata': {'type': 'SP.Data.TasksListItem'}, 'Title': title}
        task_item = tasks_list.add_item(task_properties)
        context.execute_query()
        print("Task '{0}' has been created".format(task_item.properties["Title"]))


def generate_contacts(context):
    contacts_list = ctx.web.lists.get_by_title("Contacts")
    fake = Faker()
    for idx in range(0, 1):
        name = fake.name()
        contact_properties = {'__metadata': {'type': 'SP.Data.ContactsListItem'}, 'Title': name}
        contact_item = contacts_list.add_item(contact_properties)
        context.execute_query()
        print("Contact '{0}' has been created".format(contact_item.properties["Title"]))


if __name__ == '__main__':
    ctx_auth = AuthenticationContext(url=settings['url'])
    if ctx_auth.acquire_token_for_user(username=settings['username'], password=settings['password']):
        ctx = ClientContext(settings['url'], ctx_auth)
        generate_tasks(ctx)
        # generate_contacts(ctx)
    else:
        print(ctx_auth.get_last_error())
