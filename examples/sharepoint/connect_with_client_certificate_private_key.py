import os

from examples import sample_tenant_name, sample_client_id, sample_thumbprint, sample_site_url
from office365.sharepoint.client_context import ClientContext


cert_path = '{0}/selfsigncert.pem'.format(os.path.dirname(__file__))
with open(cert_path, 'r') as f:
    private_key = open(cert_path).read()

cert_credentials = {
    'tenant': sample_tenant_name,
    'client_id': sample_client_id,
    'thumbprint': sample_thumbprint,
    'private_key': private_key
}
ctx = ClientContext(sample_site_url).with_client_certificate(**cert_credentials)
current_web = ctx.web.get().execute_query()
print("{0}".format(current_web.url))
