from faker import Faker

from office365.directory.users.profile import UserProfile
from office365.graph_client import GraphClient
from tests import (
    create_unique_name,
    test_client_id,
    test_password,
    test_tenant,
    test_username,
)


def generate_user_profile():
    fake = Faker()

    user_json = {
        "given_name": fake.name(),
        "company_name": fake.company(),
        "business_phones": [fake.phone_number()],
        "office_location": fake.street_address(),
        "city": fake.city(),
        "country": fake.country(),
        "principal_name": "{0}@{1}".format(fake.user_name(), test_tenant),
        "password": create_unique_name("P@ssw0rd"),
        "account_enabled": True,
    }
    return UserProfile(**user_json)


client = GraphClient(tenant=test_tenant).with_username_and_password(
    test_client_id, test_username, test_password
)

for idx in range(0, 1):
    user_profile = generate_user_profile()
    user = client.users.add(user_profile).execute_query()
    print("'{0}' user has been created".format(user.user_principal_name))
