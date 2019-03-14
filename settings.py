import os

user_credentials = os.environ['Office365_Python_Sdk_Credentials'].split(';')
client_credentials = os.environ['Office365_Python_Sdk_ClientCredentials'].split(';')

settings = {
    'url': 'https://mediadev88.sharepoint.com/',
    'tenant': 'mediadev88.onmicrosoft.com',
    'redirect_url': 'https://github.com/vgrem/Office365-REST-Python-Client/',
    'user_credentials': {
        'username': user_credentials[0],
        'password': user_credentials[1]
    },
    'client_credentials': {
        'client_id': 'd4b2d51e-2d8e-4f08-8bce-961a7a435130',
        'client_secret': client_credentials[1],
    }
}
