from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.client_result import ClientResult
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext


class DigitalLegacy(Entity):
    @staticmethod
    def accept_nomination(context: ClientContext, benefactor_hex_cid: str) -> ClientResult[bytes]:
        """AcceptNomination operation.

        Args:
            benefactor_hex_cid (str):
                benefactorHexCid parameter
        """
        from office365.sharepoint.esign.digitallegacy import DigitalLegacy

        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            DigitalLegacy(context),
            "AcceptNomination",
            None,
            {"benefactorHexCid": benefactor_hex_cid},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def beneficiary_redeem_access_request(context: ClientContext, benefactor_hex_cid: str) -> ClientResult[bool]:
        """BeneficiaryRedeemAccessRequest operation.

        Args:
            benefactor_hex_cid (str):
                benefactorHexCid parameter
        """
        from office365.sharepoint.esign.digitallegacy import DigitalLegacy

        return_type = ClientResult(context, bool())
        qry = ServiceOperationQuery(
            DigitalLegacy(context),
            "BeneficiaryRedeemAccessRequest",
            None,
            {"benefactorHexCid": benefactor_hex_cid},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def check_converge_status(context: ClientContext) -> ClientResult[bool]:
        """CheckConvergeStatus operation."""
        from office365.sharepoint.esign.digitallegacy import DigitalLegacy

        return_type = ClientResult(context, bool())
        qry = FunctionQuery(DigitalLegacy(context), "CheckConvergeStatus", [], return_type)
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_access_code(context: ClientContext, beneficiary_hex_cid: str) -> ClientResult[bytes]:
        """GetAccessCode operation.

        Args:
            beneficiary_hex_cid (str):
                beneficiaryHexCid parameter
        """
        from office365.sharepoint.esign.digitallegacy import DigitalLegacy

        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            DigitalLegacy(context),
            "GetAccessCode",
            None,
            {"beneficiaryHexCid": beneficiary_hex_cid},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_converge_status(context: ClientContext, email_address: str) -> ClientResult[bool]:
        """GetConvergeStatus operation.

        Args:
            email_address (str):
                emailAddress parameter
        """
        from office365.sharepoint.esign.digitallegacy import DigitalLegacy

        return_type = ClientResult(context, bool())
        qry = FunctionQuery(DigitalLegacy(context), "GetConvergeStatus", [email_address], return_type)
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_settings_as_stream(context: ClientContext) -> ClientResult[bytes]:
        """GetSettingsAsStream operation."""
        from office365.sharepoint.esign.digitallegacy import DigitalLegacy

        return_type = ClientResult(context, bytes())
        qry = FunctionQuery(DigitalLegacy(context), "GetSettingsAsStream", [], return_type, return_raw_content=True)
        context.add_query(qry)
        return return_type

    @staticmethod
    def nominate_beneficiary(context: ClientContext, beneficiary_email: str) -> ClientResult[bytes]:
        """NominateBeneficiary operation.

        Args:
            beneficiary_email (str):
                beneficiaryEmail parameter
        """
        from office365.sharepoint.esign.digitallegacy import DigitalLegacy

        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            DigitalLegacy(context),
            "NominateBeneficiary",
            None,
            {"beneficiaryEmail": beneficiary_email},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def redeem_access_request(
        context: ClientContext, beneficiary_hex_cid: str, benefactor_hex_cid: str, access_code: str
    ) -> ClientResult[bool]:
        """RedeemAccessRequest operation.

        Args:
            beneficiary_hex_cid (str):
                beneficiaryHexCid parameter
            benefactor_hex_cid (str):
                benefactorHexCid parameter
            access_code (str):
                accessCode parameter
        """
        from office365.sharepoint.esign.digitallegacy import DigitalLegacy

        return_type = ClientResult(context, bool())
        qry = ServiceOperationQuery(
            DigitalLegacy(context),
            "RedeemAccessRequest",
            None,
            {
                "beneficiaryHexCid": beneficiary_hex_cid,
                "benefactorHexCid": benefactor_hex_cid,
                "accessCode": access_code,
            },
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def reject_access_request(context: ClientContext, beneficiary_hex_cid: str) -> ClientResult[bytes]:
        """RejectAccessRequest operation.

        Args:
            beneficiary_hex_cid (str):
                beneficiaryHexCid parameter
        """
        from office365.sharepoint.esign.digitallegacy import DigitalLegacy

        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            DigitalLegacy(context),
            "RejectAccessRequest",
            None,
            {"beneficiaryHexCid": beneficiary_hex_cid},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def reject_nomination(context: ClientContext, benefactor_hex_cid: str) -> ClientResult[bytes]:
        """RejectNomination operation.

        Args:
            benefactor_hex_cid (str):
                benefactorHexCid parameter
        """
        from office365.sharepoint.esign.digitallegacy import DigitalLegacy

        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            DigitalLegacy(context),
            "RejectNomination",
            None,
            {"benefactorHexCid": benefactor_hex_cid},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def remove_benefactor(context: ClientContext, benefactor_hex_cid: str) -> ClientResult[bytes]:
        """RemoveBenefactor operation.

        Args:
            benefactor_hex_cid (str):
                benefactorHexCid parameter
        """
        from office365.sharepoint.esign.digitallegacy import DigitalLegacy

        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            DigitalLegacy(context),
            "RemoveBenefactor",
            None,
            {"benefactorHexCid": benefactor_hex_cid},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def remove_beneficiary(context: ClientContext, beneficiary_hex_cid: str) -> ClientResult[bytes]:
        """RemoveBeneficiary operation.

        Args:
            beneficiary_hex_cid (str):
                beneficiaryHexCid parameter
        """
        from office365.sharepoint.esign.digitallegacy import DigitalLegacy

        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            DigitalLegacy(context),
            "RemoveBeneficiary",
            None,
            {"beneficiaryHexCid": beneficiary_hex_cid},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def request_access(context: ClientContext, benefactor_hex_cid: str, access_code_string: str) -> ClientResult[bytes]:
        """RequestAccess operation.

        Args:
            benefactor_hex_cid (str):
                benefactorHexCid parameter
            access_code_string (str):
                accessCodeString parameter
        """
        from office365.sharepoint.esign.digitallegacy import DigitalLegacy

        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            DigitalLegacy(context),
            "RequestAccess",
            None,
            {"benefactorHexCid": benefactor_hex_cid, "accessCodeString": access_code_string},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def set_benefactor_on_nomination(
        context: ClientContext, benefactor_name: str, benefactor_email: str, benefactor_cid: str
    ) -> ClientResult[bool]:
        """SetBenefactorOnNomination operation.

        Args:
            benefactor_name (str):
                benefactorName parameter
            benefactor_email (str):
                benefactorEmail parameter
            benefactor_cid (str):
                benefactorCid parameter
        """
        from office365.sharepoint.esign.digitallegacy import DigitalLegacy

        return_type = ClientResult(context, bool())
        qry = ServiceOperationQuery(
            DigitalLegacy(context),
            "SetBenefactorOnNomination",
            None,
            {"benefactorName": benefactor_name, "benefactorEmail": benefactor_email, "benefactorCid": benefactor_cid},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def update_beneficiary_on_access_request(
        context: ClientContext, beneficiary_hex_cid: str, access_code: str
    ) -> ClientResult[bool]:
        """UpdateBeneficiaryOnAccessRequest operation.

        Args:
            beneficiary_hex_cid (str):
                beneficiaryHexCid parameter
            access_code (str):
                accessCode parameter
        """
        from office365.sharepoint.esign.digitallegacy import DigitalLegacy

        return_type = ClientResult(context, bool())
        qry = ServiceOperationQuery(
            DigitalLegacy(context),
            "UpdateBeneficiaryOnAccessRequest",
            None,
            {"beneficiaryHexCid": beneficiary_hex_cid, "accessCode": access_code},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def update_digital_legacy_setting(
        context: ClientContext, object_type: int, user_hex_cid: str, next_state: int
    ) -> ClientResult[bool]:
        """UpdateDigitalLegacySetting operation.

        Args:
            object_type (int):
                objectType parameter
            user_hex_cid (str):
                userHexCid parameter
            next_state (int):
                nextState parameter
        """
        from office365.sharepoint.esign.digitallegacy import DigitalLegacy

        return_type = ClientResult(context, bool())
        qry = ServiceOperationQuery(
            DigitalLegacy(context),
            "UpdateDigitalLegacySetting",
            None,
            {"objectType": object_type, "userHexCid": user_hex_cid, "nextState": next_state},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type
