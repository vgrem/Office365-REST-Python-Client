from __future__ import annotations

from typing import TYPE_CHECKING

from office365.runtime.client_result import ClientResult
from office365.runtime.queries.function import FunctionQuery
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity

if TYPE_CHECKING:
    from office365.sharepoint.client_context import ClientContext


class Automations(Entity):
    @staticmethod
    def add_flow_owner(
        context: ClientContext, flow_id: str, principal_object_id: str, environment_id: str
    ) -> ClientResult[bytes]:
        """AddFlowOwner operation.

        Args:
            flow_id (str):
                flowId parameter
            principal_object_id (str):
                principalObjectId parameter
            environment_id (str):
                environmentId parameter
        """
        from office365.sharepoint.automations.automations import Automations

        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            Automations(context),
            "AddFlowOwner",
            None,
            {"flowId": flow_id, "principalObjectId": principal_object_id, "environmentId": environment_id},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def authorize_connection(
        context: ClientContext, connector_name: str, connection_id: str, consent_payload: str, environment_id: str
    ) -> ClientResult[bytes]:
        """AuthorizeConnection operation.

        Args:
            connector_name (str):
                connectorName parameter
            connection_id (str):
                connectionId parameter
            consent_payload (str):
                consentPayload parameter
            environment_id (str):
                environmentId parameter
        """
        from office365.sharepoint.automations.automations import Automations

        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            Automations(context),
            "AuthorizeConnection",
            None,
            {
                "connectorName": connector_name,
                "connectionId": connection_id,
                "consentPayload": consent_payload,
                "environmentId": environment_id,
            },
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def confirm_connection_consent_code(
        context: ClientContext, connector_name: str, connection_id: str, consent_code_payload: str, environment_id: str
    ) -> ClientResult[bytes]:
        """ConfirmConnectionConsentCode operation.

        Args:
            connector_name (str):
                connectorName parameter
            connection_id (str):
                connectionId parameter
            consent_code_payload (str):
                consentCodePayload parameter
            environment_id (str):
                environmentId parameter
        """
        from office365.sharepoint.automations.automations import Automations

        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            Automations(context),
            "ConfirmConnectionConsentCode",
            None,
            {
                "connectorName": connector_name,
                "connectionId": connection_id,
                "consentCodePayload": consent_code_payload,
                "environmentId": environment_id,
            },
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def create_connection(
        context: ClientContext, connector_name: str, new_connection_id: str, connection_payload: str, environment_id: str
    ) -> ClientResult[bytes]:
        """CreateConnection operation.

        Args:
            connector_name (str):
                connectorName parameter
            new_connection_id (str):
                newConnectionId parameter
            connection_payload (str):
                connectionPayload parameter
            environment_id (str):
                environmentId parameter
        """
        from office365.sharepoint.automations.automations import Automations

        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            Automations(context),
            "CreateConnection",
            None,
            {
                "connectorName": connector_name,
                "newConnectionId": new_connection_id,
                "connectionPayload": connection_payload,
                "environmentId": environment_id,
            },
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def create_first_party_connection(
        context: ClientContext, connector_name: str, connection_id: str, environment_id: str
    ) -> ClientResult[bytes]:
        """CreateFirstPartyConnection operation.

        Args:
            connector_name (str):
                connectorName parameter
            connection_id (str):
                connectionId parameter
            environment_id (str):
                environmentId parameter
        """
        from office365.sharepoint.automations.automations import Automations

        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            Automations(context),
            "CreateFirstPartyConnection",
            None,
            {"connectorName": connector_name, "connectionId": connection_id, "environmentId": environment_id},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def create_flow(context: ClientContext, flow_payload: str, environment_id: str) -> ClientResult[bytes]:
        """CreateFlow operation.

        Args:
            flow_payload (str):
                flowPayload parameter
            environment_id (str):
                environmentId parameter
        """
        from office365.sharepoint.automations.automations import Automations

        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            Automations(context),
            "CreateFlow",
            None,
            {"flowPayload": flow_payload, "environmentId": environment_id},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def create_or_update_connection(
        context: ClientContext, connector_name: str, connection_id: str, connection_payload: str, environment_id: str
    ) -> ClientResult[bytes]:
        """CreateOrUpdateConnection operation.

        Args:
            connector_name (str):
                connectorName parameter
            connection_id (str):
                connectionId parameter
            connection_payload (str):
                connectionPayload parameter
            environment_id (str):
                environmentId parameter
        """
        from office365.sharepoint.automations.automations import Automations

        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            Automations(context),
            "CreateOrUpdateConnection",
            None,
            {
                "connectorName": connector_name,
                "connectionId": connection_id,
                "connectionPayload": connection_payload,
                "environmentId": environment_id,
            },
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def delete_connection(
        context: ClientContext, connector_name: str, connection_id: str, environment_id: str
    ) -> ClientResult[bytes]:
        """DeleteConnection operation.

        Args:
            connector_name (str):
                connectorName parameter
            connection_id (str):
                connectionId parameter
            environment_id (str):
                environmentId parameter
        """
        from office365.sharepoint.automations.automations import Automations

        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            Automations(context),
            "DeleteConnection",
            None,
            {"connectorName": connector_name, "connectionId": connection_id, "environmentId": environment_id},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def delete_flow(context: ClientContext, flow_id: str, environment_id: str) -> ClientResult[bytes]:
        """DeleteFlow operation.

        Args:
            flow_id (str):
                flowId parameter
            environment_id (str):
                environmentId parameter
        """
        from office365.sharepoint.automations.automations import Automations

        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            Automations(context),
            "DeleteFlow",
            None,
            {"flowId": flow_id, "environmentId": environment_id},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_connection_consent_link(
        context: ClientContext, connector_name: str, connection_id: str, consent_link_payload: str, environment_id: str
    ) -> ClientResult[bytes]:
        """GetConnectionConsentLink operation.

        Args:
            connector_name (str):
                connectorName parameter
            connection_id (str):
                connectionId parameter
            consent_link_payload (str):
                consentLinkPayload parameter
            environment_id (str):
                environmentId parameter
        """
        from office365.sharepoint.automations.automations import Automations

        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            Automations(context),
            "GetConnectionConsentLink",
            None,
            {
                "connectorName": connector_name,
                "connectionId": connection_id,
                "consentLinkPayload": consent_link_payload,
                "environmentId": environment_id,
            },
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_connectors(context: ClientContext, environment_id: str) -> ClientResult[bytes]:
        """GetConnectors operation.

        Args:
            environment_id (str):
                environmentId parameter
        """
        from office365.sharepoint.automations.automations import Automations

        return_type = ClientResult(context, bytes())
        qry = FunctionQuery(
            Automations(context), "GetConnectors", [environment_id], return_type, return_raw_content=True
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_dynamic_properties(
        context: ClientContext, api_name: str, connection_name: str, request_payload: str, environment_id: str
    ) -> ClientResult[bytes]:
        """GetDynamicProperties operation.

        Args:
            api_name (str):
                apiName parameter
            connection_name (str):
                connectionName parameter
            request_payload (str):
                requestPayload parameter
            environment_id (str):
                environmentId parameter
        """
        from office365.sharepoint.automations.automations import Automations

        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            Automations(context),
            "GetDynamicProperties",
            None,
            {
                "apiName": api_name,
                "connectionName": connection_name,
                "requestPayload": request_payload,
                "environmentId": environment_id,
            },
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def get_environment(context: ClientContext, environment_id: str) -> ClientResult[bytes]:
        """GetEnvironment operation.

        Args:
            environment_id (str):
                environmentId parameter
        """
        from office365.sharepoint.automations.automations import Automations

        return_type = ClientResult(context, bytes())
        qry = FunctionQuery(
            Automations(context), "GetEnvironment", [environment_id], return_type, return_raw_content=True
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def list_dynamic_enum_values(
        context: ClientContext, api_name: str, connection_name: str, request_payload: str, environment_id: str
    ) -> ClientResult[bytes]:
        """ListDynamicEnumValues operation.

        Args:
            api_name (str):
                apiName parameter
            connection_name (str):
                connectionName parameter
            request_payload (str):
                requestPayload parameter
            environment_id (str):
                environmentId parameter
        """
        from office365.sharepoint.automations.automations import Automations

        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            Automations(context),
            "ListDynamicEnumValues",
            None,
            {
                "apiName": api_name,
                "connectionName": connection_name,
                "requestPayload": request_payload,
                "environmentId": environment_id,
            },
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def list_dynamic_schema_properties(
        context: ClientContext, api_name: str, connection_name: str, request_payload: str, environment_id: str
    ) -> ClientResult[bytes]:
        """ListDynamicSchemaProperties operation.

        Args:
            api_name (str):
                apiName parameter
            connection_name (str):
                connectionName parameter
            request_payload (str):
                requestPayload parameter
            environment_id (str):
                environmentId parameter
        """
        from office365.sharepoint.automations.automations import Automations

        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            Automations(context),
            "ListDynamicSchemaProperties",
            None,
            {
                "apiName": api_name,
                "connectionName": connection_name,
                "requestPayload": request_payload,
                "environmentId": environment_id,
            },
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def prepare_flow_operations(context: ClientContext, environment_id: str) -> ClientResult[bytes]:
        """PrepareFlowOperations operation.

        Args:
            environment_id (str):
                environmentId parameter
        """
        from office365.sharepoint.automations.automations import Automations

        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            Automations(context),
            "PrepareFlowOperations",
            None,
            {"environmentId": environment_id},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def remove_flow_owner(
        context: ClientContext, flow_id: str, principal_object_id: str, environment_id: str
    ) -> ClientResult[bytes]:
        """RemoveFlowOwner operation.

        Args:
            flow_id (str):
                flowId parameter
            principal_object_id (str):
                principalObjectId parameter
            environment_id (str):
                environmentId parameter
        """
        from office365.sharepoint.automations.automations import Automations

        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            Automations(context),
            "RemoveFlowOwner",
            None,
            {"flowId": flow_id, "principalObjectId": principal_object_id, "environmentId": environment_id},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def run_recurrence_flow(
        context: ClientContext, flow_id: str, trigger_name: str, environment_id: str
    ) -> ClientResult[bytes]:
        """RunRecurrenceFlow operation.

        Args:
            flow_id (str):
                flowId parameter
            trigger_name (str):
                triggerName parameter
            environment_id (str):
                environmentId parameter
        """
        from office365.sharepoint.automations.automations import Automations

        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            Automations(context),
            "RunRecurrenceFlow",
            None,
            {"flowId": flow_id, "triggerName": trigger_name, "environmentId": environment_id},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def start_flow(context: ClientContext, flow_id: str, environment_id: str) -> ClientResult[bytes]:
        """StartFlow operation.

        Args:
            flow_id (str):
                flowId parameter
            environment_id (str):
                environmentId parameter
        """
        from office365.sharepoint.automations.automations import Automations

        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            Automations(context),
            "StartFlow",
            None,
            {"flowId": flow_id, "environmentId": environment_id},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def stop_flow(context: ClientContext, flow_id: str, environment_id: str) -> ClientResult[bytes]:
        """StopFlow operation.

        Args:
            flow_id (str):
                flowId parameter
            environment_id (str):
                environmentId parameter
        """
        from office365.sharepoint.automations.automations import Automations

        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            Automations(context),
            "StopFlow",
            None,
            {"flowId": flow_id, "environmentId": environment_id},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def test_connection(
        context: ClientContext, connector_name: str, connection_id: str, environment_id: str
    ) -> ClientResult[bytes]:
        """TestConnection operation.

        Args:
            connector_name (str):
                connectorName parameter
            connection_id (str):
                connectionId parameter
            environment_id (str):
                environmentId parameter
        """
        from office365.sharepoint.automations.automations import Automations

        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            Automations(context),
            "TestConnection",
            None,
            {"connectorName": connector_name, "connectionId": connection_id, "environmentId": environment_id},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def update_first_party_connection(
        context: ClientContext, connector_name: str, connection_id: str, environment_id: str
    ) -> ClientResult[bytes]:
        """UpdateFirstPartyConnection operation.

        Args:
            connector_name (str):
                connectorName parameter
            connection_id (str):
                connectionId parameter
            environment_id (str):
                environmentId parameter
        """
        from office365.sharepoint.automations.automations import Automations

        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            Automations(context),
            "UpdateFirstPartyConnection",
            None,
            {"connectorName": connector_name, "connectionId": connection_id, "environmentId": environment_id},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @staticmethod
    def update_flow(context: ClientContext, flow_id: str, flow_payload: str, environment_id: str) -> ClientResult[bytes]:
        """UpdateFlow operation.

        Args:
            flow_id (str):
                flowId parameter
            flow_payload (str):
                flowPayload parameter
            environment_id (str):
                environmentId parameter
        """
        from office365.sharepoint.automations.automations import Automations

        return_type = ClientResult(context, bytes())
        qry = ServiceOperationQuery(
            Automations(context),
            "UpdateFlow",
            None,
            {"flowId": flow_id, "flowPayload": flow_payload, "environmentId": environment_id},
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type
