from office365.directory.security.attacksimulations.report_overview import SimulationReportOverview
from office365.runtime.client_value import ClientValue


class SimulationReport(ClientValue):
    """
    Represents a report of an attack simulation and training campaign, including an overview and users who
    participated in the campaign.
    """

    def __init__(self, overview=SimulationReportOverview()):
        """
        :param SimulationReportOverview overview: Overview of an attack simulation and training campaign.
        """
        self.overview = overview
