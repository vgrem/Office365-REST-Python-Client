"""
Creates a modern page on a SharePoint site

https://support.microsoft.com/en-gb/office/create-and-use-modern-pages-on-a-sharepoint-site-b3d46deb-27a6-4b1e-87b8-df851e503dec
"""

from office365.sharepoint.client_context import ClientContext
from tests import (
    create_unique_name,
    test_team_site_url,
    test_user_credentials,
)

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)
page_title = create_unique_name("Site Page ")
print("Creating and publishing a site page: {0} ...".format(page_title))
new_page = ctx.site_pages.create_and_publish_page(page_title).execute_query()
# draft_page = ctx.site_pages.create_page(page_title).execute_query()
print("A site page has been created at url: {0} ...".format(new_page.absolute_url))
