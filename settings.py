import os

secure_vars = os.environ['Office365_Python_Sdk_SecureVars'].split(';')

settings = {
    'url': 'https://mediadev8.sharepoint.com/',
    'tenant': 'mediadev8.onmicrosoft.com',
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
