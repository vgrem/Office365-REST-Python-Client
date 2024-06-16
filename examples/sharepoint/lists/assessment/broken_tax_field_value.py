"""
Demonstrates how to perform list/library assessment if taxonomy field value association is broken
to term set or not.

To prevent this exception to occur:
'-2146232832, Microsoft.SharePoint.SPFieldValidationException', 'The given guid does not exist in the term store'
"""
from office365.runtime.client_request_exception import ClientRequestException
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.taxonomy.field import TaxonomyField
from tests import test_client_credentials, test_team_site_url

ctx = ClientContext(test_team_site_url).with_credentials(test_client_credentials)
lib = ctx.web.default_document_library()
fields = lib.fields.get().execute_query()
for field in fields:
    if not isinstance(field, TaxonomyField):
        continue
    try:
        items = lib.items.select([field.internal_name]).top(1).get().execute_query()
        print(field.internal_name)
    except ClientRequestException:
        print(field.is_term_set_valid)
        print("Error: {0}".format(field.internal_name))
