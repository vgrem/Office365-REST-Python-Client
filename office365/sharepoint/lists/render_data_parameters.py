from office365.runtime.client_value import ClientValue


class RenderListDataParameters(ClientValue):
    """Specifies the parameters to be used to render list data as a JSON string"""

    def __init__(
        self,
        add_all_fields=None,
        add_all_view_fields=None,
        add_regional_settings=None,
        add_required_fields=None,
        allow_multiple_value_filter_for_taxonomy_fields=None,
        audience_target=None,
        dates_in_utc=None,
        expand_groups=None,
        expand_user_field=None,
        filter_out_channel_folders_in_default_doc_lib=None,
    ):
        """
        :param bool add_all_fields:
        :param bool add_all_view_fields:
        :param bool add_regional_settings:
        :param bool add_required_fields: This parameter indicates if we return required fields.
        :param bool allow_multiple_value_filter_for_taxonomy_fields: This parameter indicates whether multi value
            filtering is allowed for taxonomy fields.
        :param bool audience_target:
        :param bool dates_in_utc: Specifies if the DateTime field is returned in UTC or local time.
        :param bool expand_groups: Specifies whether to expand the grouping or not.
        :param bool expand_user_field:
        :param bool filter_out_channel_folders_in_default_doc_lib:
        """
        self.AddAllFields = add_all_fields
        self.AddAllViewFields = add_all_view_fields
        self.AddRegionalSettings = add_regional_settings
        self.AddRequiredFields = add_required_fields
        self.AllowMultipleValueFilterForTaxonomyFields = (
            allow_multiple_value_filter_for_taxonomy_fields
        )
        self.AudienceTarget = audience_target
        self.DatesInUtc = dates_in_utc
        self.ExpandGroups = expand_groups
        self.ExpandUserField = expand_user_field
        self.FilterOutChannelFoldersInDefaultDocLib = (
            filter_out_channel_folders_in_default_doc_lib
        )

    @property
    def entity_type_name(self):
        return "SP.RenderListDataParameters"
