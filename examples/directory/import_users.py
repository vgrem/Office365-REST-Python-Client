from faker import Faker
from settings import settings
from tests import random_seed

from office365.graph.directory.userProfile import UserProfile
from office365.graph.graph_client import GraphClient


def acquire_token(auth_ctx):
    """

    :type auth_ctx: adal.AuthenticationContext
    """
    token = auth_ctx.acquire_token_with_username_password(
        'https://graph.microsoft.com',
        settings['user_credentials']['username'],
        settings['user_credentials']['password'],
        settings['client_credentials']['client_id'])
    return token


def generate_user_profile():
    fake = Faker()

    user_json = {
        'givenName': fake.name(),
        'companyName': fake.company(),
        'businessPhones': [fake.phone_number()],
        'officeLocation': fake.street_address(),
        'city': fake.city(),
        'country': fake.country(),
        'principalName': "{0}@{1}".format(fake.user_name(), settings['tenant']),
        'password': "P@ssw0rd{0}".format(random_seed),
        'accountEnabled': True
    }
    return UserProfile(**user_json)


client = GraphClient(settings['tenant'], acquire_token)

for idx in range(0, 5):
    user_profile = generate_user_profile()
    user = client.users.add(user_profile)
    client.execute_query()
    print("{0} user has been created".format(user.properties['userPrincipalName']))
