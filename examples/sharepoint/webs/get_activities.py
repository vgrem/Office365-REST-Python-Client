"""
Gets web activities
"""
from office365.sharepoint.activities.entity import SPActivityEntity
from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_site_url

client = ClientContext(test_site_url).with_credentials(test_client_credentials)
activities = client.web.activities.get().execute_query()
for activity in activities:
    print(activity.action.facet_type)
