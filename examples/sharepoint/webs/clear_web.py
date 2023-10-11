from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_site_url


def print_progress(num_deleted):
    print("{0} deleted.".format(num_deleted))


ctx = ClientContext(test_site_url).with_credentials(test_client_credentials)
result = (
    ctx.web.lists.get()
    .select(["IsSystemList", "Title", "Id"])
    .filter("IsSystemList eq false")
    .execute_query()
)
print("{0} lists found".format(len(result)))
for lst in result:
    lst.delete_object()
ctx.web.context.execute_batch(success_callback=print_progress)
