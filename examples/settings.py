import os

user_credentials = os.environ['Office365_Python_Sdk_Credentials'].split(';')

settings = {
    'url': 'https://mediadev88.sharepoint.com/',
    'user_credentials': {
        'username': user_credentials[0],
        'password': user_credentials[1]
    },
    'client_credentials': {
        'client_id': '',
        'client_secret': '',
        'redirect_url': 'https://github.com/vgrem/Office365-REST-Python-Client/'
    }
}
