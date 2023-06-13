"""
Add a certificate to an app using Microsoft Graph

https://learn.microsoft.com/en-us/graph/applications-how-to-add-certificate?tabs=http
"""
import base64

from office365.directory.key_credential import KeyCredential
from office365.graph_client import GraphClient
from tests import test_client_credentials
from tests.graph_case import acquire_token_by_username_password


def read_certificate(path):
    """
    Get the certificate key
    """
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend
    from cryptography.x509 import NameOID

    with open(path, 'rb') as f:
        pem_data = f.read()
    cert = x509.load_pem_x509_certificate(pem_data, default_backend())

    return KeyCredential(
        usage="Verify",
        key_type="AsymmetricX509Cert",
        start_datetime=cert.not_valid_before.isoformat(),
        end_datetime=cert.not_valid_after.isoformat(),
        key=base64.b64encode(pem_data).decode("utf-8"),
        display_name="O={0}".format(cert.subject.get_attributes_for_oid(NameOID.ORGANIZATION_NAME)[0].value)
    )


cert_path = '../../selfsigncert.pem'
key_cred = read_certificate(cert_path)

client = GraphClient(acquire_token_by_username_password)
app = client.applications.get_by_app_id(test_client_credentials.clientId).get().execute_query()
app.key_credentials.add(key_cred)
app.update().execute_query()
