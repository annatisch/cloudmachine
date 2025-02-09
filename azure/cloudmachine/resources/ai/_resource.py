from typing import TYPE_CHECKING, Any, Callable, Dict, List, Literal, Self, Type, TypeVar, TypedDict, Union, Unpack, Optional, overload

from ..._bicep.expressions import Output, Expression, ResourceSymbol
from ...resources.resourcegroup._resource import ResourceGroup
from ..._resource import _ClientResource, Resource, FieldsType, FieldType

if TYPE_CHECKING:
    from . import (
        CognitiveServicesAccountParams,
        Lock,
        RoleAssignment,
        PrivateEndpoint,
        DiagnosticSetting,
        Deployment,
        ManagedIdentity,
        CustomerManagedKey,
        SecretsExportConfiguration
    )


class CognitiveServicesKwargs(TypedDict, total=False):
    """"""
    kind: Literal['AIServices', 'AnomalyDetector', 'CognitiveServices', 'ComputerVision', 'ContentModerator', 'ContentSafety', 'ConversationalLanguageUnderstanding', 'CustomVision.Prediction', 'CustomVision.Training', 'Face', 'FormRecognizer', 'HealthInsights', 'ImmersiveReader', 'Internal.AllInOne', 'LanguageAuthoring', 'LUIS', 'LUIS.Authoring', 'MetricsAdvisor', 'OpenAI', 'Personalizer', 'QnAMaker.v2', 'SpeechServices', 'TextAnalytics', 'TextTranslation']
    """Kind of the Cognitive Services account. Use 'Get-AzCognitiveServicesAccountSku' to determine a valid combinations of 'kind' and 'SKU' for your Azure region."""
    custom_subdomain_name: str
    """Subdomain name used for token-based authentication. Required if 'networkAcls' or 'privateEndpoints' are set."""
    allowed_fqdn_list: List[object]
    """List of allowed FQDN."""
    api_properties: Dict[str, object]
    """The API properties for special APIs."""
    customer_managed_key: 'CustomerManagedKey'
    """The customer managed key definition."""
    deployments: List['Deployment']
    """Array of deployments about cognitive service accounts to create."""
    diagnostic_settings: List['DiagnosticSetting']
    """The diagnostic settings of the service."""
    disable_local_auth: bool
    """Allow only Azure AD authentication. Should be enabled for security reasons."""
    dynamic_throttling_enabled: bool
    """The flag to enable dynamic throttling."""
    enable_telemetry: bool
    """Enable/Disable usage telemetry for module."""
    location: str
    """Location for all Resources."""
    lock: 'Lock'
    """The lock settings of the service."""
    managed_identities: 'ManagedIdentity'
    """The managed identity definition for this resource."""
    migration_token: str
    """Resource migration token."""
    network_acls: Dict[str, object]
    """A collection of rules governing the accessibility from specific network locations."""
    private_endpoints: List['PrivateEndpoint']
    """Configuration details for private endpoints. For security reasons, it is recommended to use private endpoints whenever possible."""
    public_network_access: Literal['Disabled', 'Enabled']
    """Whether or not public network access is allowed for this resource. For security reasons it should be disabled. If not specified, it will be disabled by default if private endpoints are set and networkAcls are not set."""
    restore: bool
    """Restore a soft-deleted cognitive service at deployment time. Will fail if no such soft-deleted resource exists."""
    restrict_outbound_network_access: bool
    """Restrict outbound network access."""
    role_assignments: List['RoleAssignment']
    """Array of role assignments to create."""
    secrets_export_configuration: 'SecretsExportConfiguration'
    """Key vault reference and secret settings for the module's secrets export."""
    sku: Literal['C2', 'C3', 'C4', 'F0', 'F1', 'S', 'S0', 'S1', 'S10', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9']
    """SKU of the Cognitive Services account. Use 'Get-AzCognitiveServicesAccountSku' to determine a valid combinations of 'kind' and 'SKU' for your Azure region."""
    tags: Dict[str, object]
    """Tags of the resource."""
    storage: List[object]
    """The storage accounts for this resource."""


_DEFAULT_COGNITIVE_SERVICES: 'CognitiveServicesKwargs' = {
}

_KWARG_CONVERSION: Dict[str, str] = {
    'kind': 'kind',
    'custom_subdomain_name': 'customSubDomainName',
    'allowed_fqdn_list': 'allowedFqdnList',
    'api_properties': 'apiProperties',
    'customer_managed_key': 'customerManagedKey',
    'deployments': 'deployments',
    'diagnostic_settings': 'diagnosticSettings',
    'disable_local_auth': 'disableLocalAuth',
    'dynamic_throttling_enabled': 'dynamicThrottlingEnabled',
    'enable_telemetry': 'enableTelemetry',
    'managed_identities': 'managedIdentities',
    'migration_token': 'migrationToken',
    'location': 'location',
    'lock': 'lock',
    'network_acls': 'networkAcls',
    'private_endpoints': 'privateEndpoints',
    'public_network_access': 'publicNetworkAccess',
    'role_assignments': 'roleAssignments',
    'restore': 'restore',
    'restrict_outbound_network_access': 'restrictOutboundNetworkAccess',
    'secrets_export_configuration': 'secretsExportConfiguration',
    'sku': 'sku',
    'storage': 'userOwnedStorage',
    'tags': 'tags',
}
ClientType = TypeVar("ClientType")
 

class CognitiveServicesAccount(_ClientResource):
    identifier: Literal["cognitiveservice"] = "cognitiveservice"
    module: Literal["br/public:avm/res/cognitive-services/account"] = "br/public:avm/res/cognitive-services/account"
    DEFAULTS: 'CognitiveServicesAccountParams' = _DEFAULT_COGNITIVE_SERVICES
    resource: Literal["Microsoft.CognitiveServices/accounts"]
    properties: 'CognitiveServicesAccountParams'

    def __init__(
            self,
            properties: Optional['CognitiveServicesAccountParams'] = None,
            account_name: Optional[str] = None,
            **kwargs: Unpack[CognitiveServicesKwargs]
    ) -> None:
        account_params: 'CognitiveServicesAccountParams' = properties or {}
        if account_name:
            account_params['name'] = account_name
        for kwarg_name, param_name in _KWARG_CONVERSION.items():
            if kwarg_name in kwargs:
                account_params[param_name] = kwargs.pop(kwarg_name)
        super().__init__(
            properties=account_params,
            service_prefix=["ai"],
            **kwargs
        )

    @overload
    @classmethod
    def reference(cls, resource_id: str, /) -> Self:
        ...
    @overload
    @classmethod
    def reference(
        cls,
        *,
        name: str,
        resource_group: Optional[Union[str, ResourceGroup]] = None,
        subscription: Optional[str] = None,
    ) -> Self:
        ...
    @classmethod
    def reference(
            cls,
            resource_id: Optional[str] = None,
            *,
            name: Optional[str] = None,
            resource_group: Optional[Union[str, ResourceGroup]] = None,
            subscription: Optional[str] = None,
    ) -> Self:
        if resource_id:
            return super().reference(resource_id)
        from . import MODULE_RESOURCE, MODULE_VERSION
        resource = f"{MODULE_RESOURCE}@{MODULE_VERSION}"
        return super().reference(
            resource=resource,
            name=name,
            resource_group=resource_group,
            subscription=subscription
        )

    @property
    def resource(self) -> str:
        from . import MODULE_RESOURCE
        return MODULE_RESOURCE

    @property
    def version(self) -> str:
        from . import MODULE_VERSION
        return MODULE_VERSION

    @property
    def tag(self) -> str:
        from . import MODULE_TAG
        return MODULE_TAG

    def _find_resource_match(
            self,
            fields: FieldsType,
            rg: ResourceSymbol,
            name: Optional[Union[str, Expression]] = None,
    ) -> Optional[FieldType]:
        kind = self.properties.get('kind')
        for field in [f for f in reversed(list(fields.values())) if f.resource == self.module]:
            field_kind = field.params['kind']
            if kind and field_kind and kind != field_kind:
                continue
            if name:
                if field.params['name'] == name and field.resource_group == rg:
                    return field
            else:
                if field.resource_group == rg:
                    return field
        return None

    def _outputs(
            self,
            *,
            symbol: ResourceSymbol,
            attrname: Optional[str],
            resource_group: ResourceSymbol,
            **kwargs
    ) -> Dict[str, Output]:
        outputs = super()._outputs(symbol=symbol, attrname=attrname, resource_group=resource_group, **kwargs)
        outputs[f"AZURE_AI_ENDPOINT{self._get_suffix()}"] = Output(
            "properties.endpoint" if self._existing else "outputs.endpoint",
            symbol
        )
        return outputs

_DEFAULT_AI_SERVICES: 'CognitiveServicesAccountParams' = {
    'kind': 'AIServices',
    'sku': 'S0',
    'publicNetworkAccess': 'Enabled',
    'disableLocalAuth': True,
    'roleAssignments': [
        'Cognitive Services OpenAI Contributor',
        'Cognitive Services OpenAI User'
    ]
}


class AIServices(CognitiveServicesAccount):
    identifier: Literal["ai"] = "ai"
    DEFAULTS: 'CognitiveServicesAccountParams' = _DEFAULT_AI_SERVICES

    def _build_endpoint(self) -> str:
        return f"https://{self.name()}.openai.azure.com/"
