import os

from office365.sharepoint.client_context import ClientContext

app_settings = {
    'url': 'https://mediadev8.sharepoint.com/sites/team',
    'client_id': '51d03106-4726-442c-86db-70b32fa7547f',
    'thumbprint': "6B36FBFC86FB1C019EB6496494B9195E6D179DDB",
    'certificate_path': '{0}/selfsigncert.pem'.format(os.path.dirname(__file__))
}

ctx = ClientContext.connect_with_certificate(app_settings['url'],
                                             app_settings['client_id'],
                                             app_settings['thumbprint'],
                                             app_settings['certificate_path'])

current_web = ctx.web
ctx.load(current_web)
ctx.execute_query()
print("{0}".format(current_web.url))
