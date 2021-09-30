from office365.runtime.auth.token_response import TokenResponse
from office365.sharepoint.client_context import ClientContext
from tests import test_site_url, settings

"""
Important: for Application authenticated against Azure AD blade, calling SharePoint v1 API endpoint when
using Client Credentials flow (app-only access) will return 401 error, meaning this flow is NOT supported (blocked)
unless:

- AAD app is explicitly granted access via ACS as explained here: https://docs.microsoft.com/en-us/sharepoint/dev/solution-guidance/security-apponly-azureacs
- Client Certificate flow is utilized instead as explained here https://docs.microsoft.com/en-us/sharepoint/dev/solution-guidance/security-apponly-azuread




Refer, for instance, this thread for a more details:
https://docs.microsoft.com/en-us/answers/questions/131535/azure-app-cannot-access-sharepoint-online-sites-us.html

"""


def acquire_token():
    authority_url = 'https://login.microsoftonline.com/{0}'.format(settings.get('default', 'tenant'))
    import msal
    app = msal.ConfidentialClientApplication(
        authority=authority_url,
        client_id=settings.get('client_credentials', 'client_id'),
        client_credential=settings.get('client_credentials', 'client_secret')
    )
    token_json = app.acquire_token_for_client(scopes=["https://mediadev8.sharepoint.com/.default"])
    return TokenResponse.from_json(token_json)


ctx = ClientContext(test_site_url).with_access_token(acquire_token)
target_web = ctx.web.get().execute_query()
print(target_web.url)
