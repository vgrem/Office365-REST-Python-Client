from office365.runtime.client_value import ClientValue


class AlertCreationInformation(ClientValue):

    def __init__(self, alert_frequency, template_name, alert_type):
        super().__init__()
        self.AlertFrequency = alert_frequency
        self.AlertTemplateName = template_name
        self.AlertType = alert_type
