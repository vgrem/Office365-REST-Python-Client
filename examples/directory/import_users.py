from faker import Faker
from office365.directory.userProfile import UserProfile
from office365.graph_client import GraphClient
from tests import test_tenant, create_unique_name
from tests.graph_case import acquire_token_by_username_password


def generate_user_profile():
    fake = Faker()

    user_json = {
        'givenName': fake.name(),
        'companyName': fake.company(),
        'businessPhones': [fake.phone_number()],
        'officeLocation': fake.street_address(),
        'city': fake.city(),
        'country': fake.country(),
        'principalName': "{0}@{1}".format(fake.user_name(), test_tenant),
        'password': create_unique_name("P@ssw0rd"),
        'accountEnabled': True
    }
    return UserProfile(**user_json)


client = GraphClient(acquire_token_by_username_password)

for idx in range(0, 5):
    user_profile = generate_user_profile()
    user = client.users.add(user_profile).execute_query()
    print("{0} user has been created".format(user.properties['userPrincipalName']))
