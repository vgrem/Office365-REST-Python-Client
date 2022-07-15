from office365.runtime.client_object_collection import ClientObjectCollection


class TaxonomyItemCollection(ClientObjectCollection):

    def get_by_name(self, name):
        """
        Returns the taxonomy item with the specified name.

        :param str name: A string that contains the name of the taxonomy item.
        :rtype: office365.sharepoint.taxonomy.item.TaxonomyItem
        """
        return_type = self._item_type(self.context)
        self.add_child(return_type)

        def _after_get_by_name(col):
            if len(col) != 1:
                message = "Taxonomy Item not found or ambiguous match found for name: {0}".format(name)
                raise ValueError(message)
            return_type.set_property("id", col[0].get_property("id"))

        self.filter("name eq '{0}'".format(name))
        self.context.load(self, after_loaded=_after_get_by_name)
        return return_type

