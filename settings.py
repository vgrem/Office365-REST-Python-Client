import os

secure_vars = os.environ['office365_python_sdk_securevars'].split(';')
tenant_prefix = secure_vars[0].split("@")[1].split(".")[0]  # extract tenant prefix from email address

settings = {
    'url': 'https://{tenant}.sharepoint.com/'.format(tenant=tenant_prefix),
    'team_site_url': "https://{tenant}.sharepoint.com/sites/team/".format(tenant=tenant_prefix),
    'admin_site_url': "https://{0}-admin.sharepoint.com/".format(tenant_prefix),
    'tenant': '{tenant}.onmicrosoft.com'.format(tenant=tenant_prefix),
    'redirect_url': 'https://github.com/vgrem/Office365-REST-Python-Client/',
    'user_credentials': {
        'username': secure_vars[0],
        'password': secure_vars[1]
    },
    'client_credentials': {
        'client_id': secure_vars[2],
        'client_secret': secure_vars[3],
    },
    "test_accounts": ["mdoe@{0}.onmicrosoft.com".format(tenant_prefix),
                      "jdoe@{0}.onmicrosoft.com".format(tenant_prefix)]
}
