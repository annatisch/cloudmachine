from typing import TYPE_CHECKING, Any, Dict, List, Literal, Unpack, Optional

from ...._bicep.expressions import ModuleSymbol, Output, Parameter
from ...._resource import Resource, FieldsType

if TYPE_CHECKING:
    from . import SystemTopicParams, SystemTopicKwargs


_DEFAULT_SYSTEM_TOPIC: 'SystemTopicParams' = {

}

_SUPPORTED_SYSTEM_TOPICS: Dict[str, str] = {
    # Azure API Center
    # Azure API Management
    # Azure App Configuration
    # Azure App Service
    "br/public:avm/res/storage/storage-account": "Microsoft.Storage.StorageAccounts"
    # Azure Cache for Redis
    # Azure Communication Services
    # Azure Container Registry
    # Azure Data Box
    # Azure Data Manager for Agriculture
    # Azure Event Grid
    # Azure Event Hubs
    # Azure Health Data Services
    # Azure IoT Hub
    # Azure Key Vault
    # Azure Kubernetes Service
    # Azure Machine Learning
    # Azure Maintenance Configuration
    # Azure Maps
    # Azure Media Services
    # Azure Policy
    # Azure Resource Notifications
    # Azure resource groups
    # Azure Service Bus
    # Azure SignalR
    # Azure Storage Actions
    # Azure subscriptions
}


class EventSystemTopic(Resource):
    identifier: Literal["events:systemtopic"] = "events:systemtopic"
    module: Literal["br/public:avm/res/event-grid/system-topic"] = "br/public:avm/res/event-grid/system-topic"
    defaults: 'SystemTopicParams' = _DEFAULT_SYSTEM_TOPIC
    resource: Literal["Microsoft.EventGrid/systemTopics"] = "Microsoft.EventGrid/systemTopics"
    properties: 'SystemTopicParams'

    def __init__(
            self,
            properties: Optional['SystemTopicParams'] = None,
            systemtopic_name: Optional[str] = None,
            **kwargs: Unpack['SystemTopicKwargs']
    ) -> None:
        systemtopic_params: 'SystemTopicParams' = properties or {}
        if systemtopic_name:
            systemtopic_params['name'] = systemtopic_name
        if 'source' in kwargs:
            systemtopic_params['source'] = kwargs['source']
        if 'topic_type' in kwargs:
            systemtopic_params['topicType'] = kwargs['topic_type']
        if 'diagnostic_settings' in kwargs:
            systemtopic_params['diagnosticSettings'] = kwargs.pop('diagnostic_settings')
        if 'location' in kwargs:
            systemtopic_params['location'] = kwargs.pop('location')
        if 'lock' in kwargs:
            systemtopic_params['lock'] = kwargs.pop('lock')
        if 'managed_identities' in kwargs:
            systemtopic_params['managedIdentities'] = kwargs.pop('managed_identities')
        if 'role_assignments' in kwargs:
            systemtopic_params['roleAssignments'] = kwargs.pop('role_assignments')
        if 'tags' in kwargs:
            systemtopic_params['tags'] = kwargs.pop('tags')
        super().__init__(
            properties=systemtopic_params,
            service_prefix=["eventgrid_systemtopic"],
            **kwargs
        )
        self._supports_managed_identity = True

    @property
    def resource(self) -> str:
        from . import MODULE_RESOURCE
        return MODULE_RESOURCE

    @property
    def version(self) -> str:
        from . import MODULE_VERSION
        return MODULE_VERSION

    def _merge_params(
            self,
            params: 'SystemTopicParams',
            *,
            symbol: ModuleSymbol,
            fields: FieldsType,
            attrname: Optional[str] = None,
            **kwargs
    ) -> Dict[str, Output]:
        outputs = super()._merge_params(params, symbol=symbol, attrname=attrname, **kwargs)
        source = params.pop('source', None)
        if isinstance(source, str) and not source.startswith("/subscriptions/"):
            try:
                field = fields[source]
                source = field[2].id
                if 'topicType' not in params:
                    params['topicType'] = _SUPPORTED_SYSTEM_TOPICS[field[0]]
            except KeyError as e:
                raise ValueError("Cannot assign System Topic to resource with attribute name: '{source}'")
        elif not source:
            for resource in reversed(list(fields.values())):
                if resource[0] in _SUPPORTED_SYSTEM_TOPICS:
                    source = resource[2].id
                    if 'topicType' not in params:
                        params['topicType'] = _SUPPORTED_SYSTEM_TOPICS[resource[0]]
                    break
            if not source:
                raise ValueError("No resources found in component the can be sources for the system topic.")
        params['source'] = source
        return outputs

    def _update_managed_identities(
            self,
            params: Dict[str, Any],
            updated_params: Optional[Dict[str, Any]] = None,
            *,
            identity: Optional[ModuleSymbol] = None
    ) -> None:
        if updated_params:
            managed_identities = params.pop("managedIdentities", {})
            user_assigned_identities = managed_identities.pop("userAssignedResourcesIds", [])
            user_assigned_identities.extend(updated_params.get('userAssignedResourcesIds', []))
            managed_identities.update(updated_params)
            managed_identities["userAssignedResourcesIds"] = user_assigned_identities
            params['managedIdentities'] = managed_identities
        if identity and self._supports_managed_identity:
            if 'managedIdentities' not in params:
                params['managedIdentities'] = {
                    'userAssignedResourcesIds': [identity.id]
                }
            else:
                identities = params['managedIdentities'].get('userAssignedResourcesIds', [])
                existing = [i for i in identities if (hasattr(i, 'symbol') and i.symbol == identity) or i == identity]
                if not existing:
                    identities.append(identity.id)
                    params['managedIdentities']['userAssignedResourcesIds'] = identities
