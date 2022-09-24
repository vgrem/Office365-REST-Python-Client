import json

from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient


# The example is adapted from https://docs.microsoft.com/en-us/graph/api/user-sendmail?view=graph-rest-1.0

def search_by_subject(client, text):
    query_text = "subject:'Let's go for lunch'"
    return client.search.query_messages(query_text).execute_query()


def search_in_mail_folder(client, text=None):
    inbox = client.me.mail_folders["Inbox"].get().execute_query()
    query_text = "parentFolderId:{0}".format(inbox.id)
    return client.search.query_messages(query_text).execute_query()


graph_client = GraphClient(acquire_token_by_username_password)
#result = search_by_subject(graph_client, "Let's go for lunch")
result = search_in_mail_folder(graph_client)
print(json.dumps(result.value.to_json(), indent=4))
