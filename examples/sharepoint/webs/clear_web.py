from office365.sharepoint.client_context import ClientContext
from tests import test_client_credentials, test_site_url


def print_progress(num_deleted):
    print("{0} deleted.".format(num_deleted))


def delete_custom_lists(web):
    """
    :type web: office365.sharepoint.webs.web.Web
    """
    result = (
        web.lists.get()
        .select(["IsSystemList", "Title", "Id"])
        .filter("IsSystemList eq false")
        .execute_query()
    )
    print("{0} lists found".format(len(result)))
    for lst in result:  # type: List
        lst.delete_object()
    web.context.execute_batch(success_callback=print_progress)


ctx = ClientContext(test_site_url).with_credentials(test_client_credentials)
delete_custom_lists(ctx.web)
