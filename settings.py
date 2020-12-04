import os

secure_vars = os.environ['office365_python_sdk_securevars'].split(';')
tenant_name = secure_vars[0].split("@")[1]  # extract tenant prefix from email address
tenant_prefix = tenant_name.split(".")[0]

settings = {
    'url': 'https://{0}.sharepoint.com/'.format(tenant_prefix),
    'team_site_url': "https://{0}.sharepoint.com/sites/team/".format(tenant_prefix),
    'admin_site_url': "https://{0}-admin.sharepoint.com/".format(tenant_prefix),
    'tenant': tenant_name,
    'redirect_url': 'https://github.com/vgrem/Office365-REST-Python-Client/',
    'user_credentials': {
        'username': secure_vars[0],
        'password': secure_vars[1]
    },
    'client_credentials': {
        'client_id': secure_vars[2],
        'client_secret': secure_vars[3],
    },
    "first_account_name": "jdoe2@{0}.onmicrosoft.com".format(tenant_prefix),
    "test_alt_account_name": "mdoe@{0}.onmicrosoft.com".format(tenant_prefix)
}
