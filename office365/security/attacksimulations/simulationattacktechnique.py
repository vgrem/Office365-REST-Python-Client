from enum import Enum


class SimulationAttackTechnique(Enum):
    unknown = "0"
    credentialHarvesting = "1"
    attachmentMalware = "2"
    driveByUrl = "3"
    linkInAttachment = "4"
    linkToMalwareFile = "5"
    unknownFutureValue = "6"

    @property
    def entity_type_name(self):
        return "microsoft.graph.SimulationAttackTechnique"
