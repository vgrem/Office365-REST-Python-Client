from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient

# Upload large attachment to Outlook message

client = GraphClient(acquire_token_by_username_password)

# local_path = "../../tests/data/Sample.txt"
local_path = "../../../tests/data/big_buck_bunny.mp4"


def print_progress(range_pos):
    print("{0} bytes uploaded".format(range_pos))


def run_example_1():
    draft_message = client.me.messages.add(
        subject="Meet for lunch?",
        body="The new cafeteria is open.",
        to_recipients=["fannyd@contoso.onmicrosoft.com"]
    ).execute_query()
    print(draft_message.id)

    draft_message.upload_attachment(local_path, print_progress).send().execute_query()


def run_example_2():
    message = client.me.messages.add(
        subject="Meet for lunch?",
        body="The new cafeteria is open.",
        to_recipients=["fannyd@contoso.onmicrosoft.com", "vvgrem@gmail.com"]
    ).upload_attachment(local_path, print_progress).execute_query()
    print(message.id)


#run_example_1()
run_example_2()


