from office365.delta_path import DeltaPath
from office365.entity_collection import EntityCollection


class DeltaCollection(EntityCollection):

    def change_type(self, type_name):
        """
        Specifies a custom query option to filter the delta response based on the type of change.

        :param str type_name: Supported values are created, updated or deleted.
        """
        self.query_options.custom["changeType"] = type_name
        return self

    @property
    def delta(self):
        """
        Get newly created, updated, or deleted entities (changes)
        """
        return self.properties.get('delta',
                                   DeltaCollection(self.context, self._item_type, DeltaPath(self.resource_path)))
