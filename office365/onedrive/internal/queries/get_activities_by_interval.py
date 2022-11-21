from office365.entity_collection import EntityCollection
from office365.onedrive.analytics.item_activity_stat import ItemActivityStat
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.service_operation import ServiceOperationQuery


def build_get_activities_by_interval_query(binding_type, start_dt=None, end_dt=None, interval=None):
    """
    :param office365.entity.Entity binding_type: Binding type
    :param datetime.datetime start_dt: The start time over which to aggregate activities.
    :param datetime.datetime end_dt: The end time over which to aggregate activities.
    :param str interval: The aggregation interval.
    """
    params = {
        "startDateTime": start_dt.strftime('%m-%d-%Y') if start_dt else None,
        "endDateTime": end_dt.strftime('%m-%d-%Y') if end_dt else None,
        "interval": interval
    }
    return_type = EntityCollection(binding_type.context, ItemActivityStat, binding_type.resource_path)
    qry = ServiceOperationQuery(binding_type, "getActivitiesByInterval", params, None, None, return_type)

    def _construct_request(request):
        request.method = HttpMethod.Get
    binding_type.context.before_execute(_construct_request)
    return qry
