import os

secure_vars = os.environ['office365_python_sdk_securevars'].split(';')
tenant = os.environ.get('office365_python_sdk_tenant', 'mediadev8')

settings = {
    'url': f'https://{tenant}.sharepoint.com/',
    'tenant': f'{tenant}.onmicrosoft.com',
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


