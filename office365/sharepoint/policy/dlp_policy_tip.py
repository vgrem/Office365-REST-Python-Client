from office365.runtime.types.collections import StringCollection
from office365.sharepoint.base_entity import BaseEntity


class DlpPolicyTip(BaseEntity):
    """Provides information about the Data Loss Protection policy on an item so it can be shown to the user."""

    @property
    def applied_actions_text(self):
        """Specifies the text which states what restrictive actions have been applied to this item."""
        return self.properties.get("AppliedActionsText", None)

    @property
    def compliance_url(self):
        """Specifies the URL that provides additional help on the policy tip dialog."""
        return self.properties.get("ComplianceUrl", None)

    @property
    def general_text(self):
        """General text that appears on the top of the policy tip dialog."""
        return self.properties.get("GeneralText", None)

    @property
    def last_processed_time(self):
        """The last time this item was processed for policy matches."""
        return self.properties.get("LastProcessedTime", None)

    @property
    def matched_condition_descriptions(self):
        """An array that contains a description of each policy condition that has been matched."""
        return self.properties.get("MatchedConditionDescriptions", StringCollection())

    @property
    def override_options(self):
        """The allowable options that someone can take to override policy matches."""
        return self.properties.get("OverrideOptions", None)

    @property
    def two_letter_iso_language_name(self):
        """The two-letter language code of the generated policy tip detail."""
        return self.properties.get("TwoLetterISOLanguageName", None)

