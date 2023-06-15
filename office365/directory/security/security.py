from office365.directory.security.alerts.alert import Alert
from office365.directory.security.attacksimulations.root import AttackSimulationRoot
from office365.directory.security.cases_root import CasesRoot
from office365.directory.security.triggers.root import TriggersRoot
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath


class Security(Entity):
    """The security resource is the entry point for the Security object model. It returns a singleton security resource.
     It doesn't contain any usable properties."""

    @property
    def alerts(self):
        return self.properties.get('alerts',
                                   EntityCollection(self.context, Alert, ResourcePath("alerts", self.resource_path)))

    @property
    def alerts_v2(self):
        """
        A collection of alerts in Microsoft 365 Defender.
        """
        return self.properties.get('alerts_v2',
                                   EntityCollection(self.context, Alert, ResourcePath("alerts_v2", self.resource_path)))

    @property
    def cases(self):
        """"""
        return self.properties.get('cases',
                                   CasesRoot(self.context, ResourcePath("cases", self.resource_path)))

    @property
    def attack_simulation(self):
        """"""
        return self.properties.get('attackSimulation',
                                   AttackSimulationRoot(self.context,
                                                        ResourcePath("attackSimulation", self.resource_path)))

    @property
    def triggers(self):
        return self.properties.get('triggers',
                                   TriggersRoot(self.context, ResourcePath("triggers", self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "alerts_v2": self.alerts_v2,
                "attackSimulation": self.attack_simulation
            }
            default_value = property_mapping.get(name, None)
        return super(Security, self).get_property(name, default_value)
