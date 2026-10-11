from __future__ import annotations

from typing import TYPE_CHECKING

from office365.entity import Entity
from office365.entity_collection import EntityCollection
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.odata_property import odata
from office365.security.attacksimulations.automation import (
    SimulationAutomation,
)
from office365.security.attacksimulations.landing_page import LandingPage
from office365.security.attacksimulations.operations.operation import (
    AttackSimulationOperation,
)
from office365.security.attacksimulations.simulation import Simulation

if TYPE_CHECKING:
    from office365.security.attacksimulations.login_page import LoginPage
    from office365.security.attacksimulations.payload import Payload
    from office365.security.end_user_notification import EndUserNotification
    from office365.security.training import Training


class AttackSimulationRoot(Entity):
    """Represents an abstract type that provides the ability to launch a realistic phishing attack that organizations
    can learn from."""

    @odata(name="landingPages")
    @property
    def landing_pages(self) -> EntityCollection[LandingPage]:
        """Represents an attack simulation training landing page."""
        return self.properties.get(
            "landingPages",
            EntityCollection(
                self.context,
                LandingPage,
                ResourcePath("landingPages", self.resource_path),
            ),
        )

    @property
    def operations(self) -> EntityCollection[AttackSimulationOperation]:
        """Represents an attack simulation training operation."""
        return self.properties.get(
            "operations",
            EntityCollection(
                self.context,
                AttackSimulationOperation,
                ResourcePath("operations", self.resource_path),
            ),
        )

    @property
    def simulations(self) -> EntityCollection[Simulation]:
        """Represents an attack simulation training campaign in a tenant."""
        return self.properties.get(
            "simulations",
            EntityCollection(
                self.context,
                Simulation,
                ResourcePath("simulations", self.resource_path),
            ),
        )

    @odata(name="simulationAutomations")
    @property
    def simulation_automations(self) -> EntityCollection[SimulationAutomation]:
        """Represents simulation automation created to run on a tenant."""
        return self.properties.get(
            "simulationAutomations",
            EntityCollection(
                self.context,
                SimulationAutomation,
                ResourcePath("simulationAutomations", self.resource_path),
            ),
        )

    @property
    def end_user_notifications(self) -> EntityCollection[EndUserNotification]:
        """Gets the endUserNotifications property"""
        from office365.security.end_user_notification import (
            EndUserNotification,
        )

        return self.properties.get(
            "endUserNotifications",
            EntityCollection[EndUserNotification](
                self.context, EndUserNotification, ResourcePath("endUserNotifications", self.resource_path)
            ),
        )

    @property
    def login_pages(self) -> EntityCollection[LoginPage]:
        """Gets the loginPages property"""
        from office365.security.attacksimulations.login_page import LoginPage

        return self.properties.get(
            "loginPages",
            EntityCollection[LoginPage](self.context, LoginPage, ResourcePath("loginPages", self.resource_path)),
        )

    @property
    def payloads(self) -> EntityCollection[Payload]:
        """Gets the payloads property"""
        from office365.security.attacksimulations.payload import Payload

        return self.properties.get(
            "payloads", EntityCollection[Payload](self.context, Payload, ResourcePath("payloads", self.resource_path))
        )

    @property
    def trainings(self) -> EntityCollection[Training]:
        """Gets the trainings property"""
        from office365.security.training import Training

        return self.properties.get(
            "trainings",
            EntityCollection[Training](self.context, Training, ResourcePath("trainings", self.resource_path)),
        )

    @property
    def entity_type_name(self) -> str:
        return "microsoft.graph.AttackSimulationRoot"
