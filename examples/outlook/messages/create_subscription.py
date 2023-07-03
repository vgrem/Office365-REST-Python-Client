"""
Demonstrates how to  send a change notification when the user receives a new mail.

https://learn.microsoft.com/en-us/graph/api/subscription-post-subscriptions?view=graph-rest-1.0&tabs=http
"""
import datetime

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)

expires = datetime.datetime.now() + datetime.timedelta(hours=120)
notification_url = "https://webhook.azurewebsites.net/api/send/myNotifyClient"
subscription = client.subscriptions.add("created",
                                        notification_url,
                                        client.me.mail_folders["Inbox"].messages.resource_path,
                                        expires).execute_query()
print(subscription)
