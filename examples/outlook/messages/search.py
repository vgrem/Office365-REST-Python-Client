import json

from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient
from office365.outlook.mail.folder import MailFolder


def search_by_subject(client, query_text):
    return client.search.query_messages(query_text).execute_query()


def search_in_mail_folder(client, text=None):
    inbox = client.me.mail_folders["Inbox"]  # type: MailFolder
    # query_text = "parentFolderId:{0}".format(inbox.id)
    # return client.search.query_messages(query_text).execute_query()
    return inbox.messages.filter("subject eq '{0}'".format(text)).get().execute_query()


graph_client = GraphClient(acquire_token_by_username_password)
# result = search_by_subject(graph_client, "Let's go for lunch")
result = search_in_mail_folder(graph_client, "Major update from Message center")
print(json.dumps(result.to_json(), indent=4))
