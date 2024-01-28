from office365.directory.security.attacksimulations.automation import (
    SimulationAutomation,
)
from office365.directory.security.attacksimulations.simulation import Simulation
from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath


class AttackSimulationRoot(Entity):
    """Represents an abstract type that provides the ability to launch a realistic phishing attack that organizations
    can learn from."""

    @property
    def simulations(self):
        # type: () -> EntityCollection[Simulation]
        """Represents an attack simulation training campaign in a tenant."""
        return self.properties.get(
            "simulations",
            EntityCollection(
                self.context,
                Simulation,
                ResourcePath("simulations", self.resource_path),
            ),
        )

    @property
    def simulation_automations(self):
        # type: () -> EntityCollection[SimulationAutomation]
        """Represents simulation automation created to run on a tenant."""
        return self.properties.get(
            "simulationAutomations",
            EntityCollection(
                self.context,
                SimulationAutomation,
                ResourcePath("simulationAutomations", self.resource_path),
            ),
        )

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "simulationAutomations": self.simulation_automations,
            }
            default_value = property_mapping.get(name, None)
        return super(AttackSimulationRoot, self).get_property(name, default_value)
