import os

secure_vars = os.environ['Office365_Python_Sdk_SecureVars'].split(';')
company = os.environ.get('COMPANY', 'mediadev8')

settings = {
    'url': 'https://{company}.sharepoint.com/'.format(company=company),
    'tenant': '{company}.onmicrosoft.com'.format(company=company),
    'redirect_url': 'https://github.com/vgrem/Office365-REST-Python-Client/',
    'user_credentials': {
        'username': secure_vars[0],
        'password': secure_vars[1]
    },
    'client_credentials': {
        'client_id': secure_vars[2],
        'client_secret': secure_vars[3],
    }
}
