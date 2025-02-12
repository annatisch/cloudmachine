from typing import TYPE_CHECKING, Any, Callable, Dict, List, Literal, Type, TypedDict, Union, Unpack, Optional, overload
from typing_extensions import TypeVar

from ..._bicep.expressions import Output, Expression, ResourceSymbol, Parameter
from ..resourcegroup import ResourceGroup
from .._utils import _convert_managed_identities
from ..._resource import _ClientResource, FieldsType, FieldType, ResourceReference, ExtensionResources

if TYPE_CHECKING:
    from .._utils import ManagedIdentity, RoleAssignment
    from .types import CognitiveServicesAccountResource


class CognitiveServicesKwargs(TypedDict, total=False):
    """"""
    kind: Union[Parameter[str], Literal['AIServices', 'AnomalyDetector', 'CognitiveServices', 'ComputerVision', 'ContentModerator', 'ContentSafety', 'ConversationalLanguageUnderstanding', 'CustomVision.Prediction', 'CustomVision.Training', 'Face', 'FormRecognizer', 'HealthInsights', 'ImmersiveReader', 'Internal.AllInOne', 'LanguageAuthoring', 'LUIS', 'LUIS.Authoring', 'MetricsAdvisor', 'OpenAI', 'Personalizer', 'QnAMaker.v2', 'SpeechServices', 'TextAnalytics', 'TextTranslation']]
    """Kind of the Cognitive Services account. Use 'Get-AzCognitiveServicesAccountSku' to determine a valid combinations of 'kind' and 'SKU' for your Azure region."""
    custom_subdomain_name: Union[str, Parameter[str]]
    """Subdomain name used for token-based authentication. Required if 'networkAcls' or 'privateEndpoints' are set."""
    allowed_fqdn_list: Union[List[Union[str, Parameter[str]]], Parameter[List[str]]]
    """List of allowed FQDN."""
    api_properties: Union['ApiProperties', Parameter['ApiProperties']]
    """The API properties for special APIs."""
    disable_local_auth: Union[bool, Parameter[bool]]
    """Allow only Azure AD authentication. Should be enabled for security reasons."""
    dynamic_throttling_enabled: Union[bool, Parameter[bool]]
    """The flag to enable dynamic throttling."""
    location: Union[str, Parameter[str]]
    """Location for all Resources."""
    managed_identities: 'ManagedIdentity'
    """The managed identity definition for this resource."""
    migration_token: Union[str, Parameter[str]]
    """Resource migration token."""
    network_acls: Union['NetworkRuleSet', Parameter['NetworkRuleSet']]
    """A collection of rules governing the accessibility from specific network locations."""
    public_network_access: Union[Literal['Disabled', 'Enabled'], Parameter[str]]
    """Whether or not public network access is allowed for this resource. For security reasons it should be disabled. If not specified, it will be disabled by default if private endpoints are set and networkAcls are not set."""
    restore: Union[bool, Parameter[bool]]
    """Restore a soft-deleted cognitive service at deployment time. Will fail if no such soft-deleted resource exists."""
    restrict_outbound_network_access: Union[bool, Parameter[bool]]
    """Restrict outbound network access."""
    role_assignments: Union[Parameter[List[Union[str, 'RoleAssignment']]], List[Union[Parameter[Union[str, 'RoleAssignment']], 'RoleAssignment', Literal['Cognitive Services Contributor', 'Cognitive Services Custom Vision Contributor', 'Cognitive Services Custom Vision Deployment', 'Cognitive Services Custom Vision Labeler', 'Cognitive Services Custom Vision Reader', 'Cognitive Services Custom Vision Trainer', 'Cognitive Services Data Reader (Preview)', 'Cognitive Services Face Recognizer', 'Cognitive Services Immersive Reader User', 'Cognitive Services Language Owner', 'Cognitive Services Language Reader', 'Cognitive Services Language Writer', 'Cognitive Services LUIS Owner', 'Cognitive Services LUIS Reader', 'Cognitive Services LUIS Writer', 'Cognitive Services Metrics Advisor Administrator', 'Cognitive Services Metrics Advisor User', 'Cognitive Services OpenAI Contributor', 'Cognitive Services OpenAI User', 'Cognitive Services QnA Maker Editor', 'Cognitive Services QnA Maker Reader', 'Cognitive Services Speech Contributor', 'Cognitive Services Speech User', 'Cognitive Services User', 'Contributor', 'Owner', 'Reader', 'Role Based Access Control Administrator', 'User Access Administrator']]]]
    """Array of role assignments to create."""
    user_role: Union['RoleAssignment', Parameter[Union[str, 'RoleAssignment']], Literal['Cognitive Services Contributor', 'Cognitive Services Custom Vision Contributor', 'Cognitive Services Custom Vision Deployment', 'Cognitive Services Custom Vision Labeler', 'Cognitive Services Custom Vision Reader', 'Cognitive Services Custom Vision Trainer', 'Cognitive Services Data Reader (Preview)', 'Cognitive Services Face Recognizer', 'Cognitive Services Immersive Reader User', 'Cognitive Services Language Owner', 'Cognitive Services Language Reader', 'Cognitive Services Language Writer', 'Cognitive Services LUIS Owner', 'Cognitive Services LUIS Reader', 'Cognitive Services LUIS Writer', 'Cognitive Services Metrics Advisor Administrator', 'Cognitive Services Metrics Advisor User', 'Cognitive Services OpenAI Contributor', 'Cognitive Services OpenAI User', 'Cognitive Services QnA Maker Editor', 'Cognitive Services QnA Maker Reader', 'Cognitive Services Speech Contributor', 'Cognitive Services Speech User', 'Cognitive Services User', 'Contributor', 'Owner', 'Reader', 'Role Based Access Control Administrator', 'User Access Administrator']]
    """Role assignment to create for user principal ID"""
    sku: Union[Literal['C2', 'C3', 'C4', 'F0', 'F1', 'S', 'S0', 'S1', 'S10', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9'], Parameter[str]]
    """SKU of the Cognitive Services account. Use 'Get-AzCognitiveServicesAccountSku' to determine a valid combinations of 'kind' and 'SKU' for your Azure region."""
    tags: Union[Dict[str, Union[str, Parameter[str]]], Parameter[Dict]]
    """Tags of the resource."""
    # storage: List[object]
    # """The storage accounts for this resource."""


_DEFAULT_COGNITIVE_SERVICES: 'CognitiveServicesKwargs' = {}
CognitiveServicesAccountAccountResourceType = TypeVar('CognitiveServicesAccountAccountResourceType', default='CognitiveServicesAccountResource')


class CognitiveServicesAccount(_ClientResource[CognitiveServicesAccountAccountResourceType]):
    DEFAULTS: 'CognitiveServicesAccountResource' = _DEFAULT_COGNITIVE_SERVICES
    resource: Literal["Microsoft.CognitiveServices/accounts"]
    properties: CognitiveServicesAccountAccountResourceType

    def __init__(
            self,
            properties: Optional['CognitiveServicesAccountResource'] = None,
            /,
            name: Optional[str] = None,
            kind: Optional[str] = None,
            **kwargs: Unpack[CognitiveServicesKwargs]
    ) -> None:
        existing = kwargs.pop('existing', False)
        extensions: ExtensionResources = {}
        if 'role_assignments' in kwargs:
            extensions['role_assignments'] = kwargs.pop('role_assignments')
        if 'user_role' in kwargs:
            extensions['user_role'] = kwargs.pop('user_role')
        if not existing:
            properties = properties or {}
            if 'properties' not in properties:
                properties['properties'] = {}
            if name:
                properties['name'] = name
            if kind:
                properties['kind'] = kind
            if 'kind' in kwargs:
                properties['kind'] = kwargs.pop('kind')
            if 'custom_subdomain_name' in kwargs:
                properties['properties']['customSubDomainName'] = kwargs.pop('custom_subdomain_name')
            if 'allowed_fqdn_list' in kwargs:
                properties['properties']['allowedFqdnList'] = kwargs.pop('allowed_fqdn_list')
            if 'api_properties' in kwargs:
                properties['properties']['apiProperties'] = kwargs.pop('api_properties')
            if 'disable_local_auth' in kwargs:
                properties['properties']['disableLocalAuth'] = kwargs.pop('disable_local_auth')
            if 'dynamic_throttling_enabled' in kwargs:
                properties['properties']['dynamicThrottlingEnabled'] = kwargs.pop('dynamic_throttling_enabled')
            if 'location' in kwargs:
                properties['location'] = kwargs.pop('location')
            if 'managed_identities' in kwargs:
                properties['identity'] = _convert_managed_identities(kwargs.pop('managed_identities'))
            if 'migration_token' in kwargs:
                properties['properties']['migrationToken'] = kwargs.pop('migration_token')
            if 'network_acls' in kwargs:
                properties['properties']['networkAcls'] = kwargs.pop('network_acls')
            if 'public_network_access' in kwargs:
                properties['properties']['publicNetworkAccess'] = kwargs.pop('public_network_access')
            if 'restore' in kwargs:
                properties['properties']['restore'] = kwargs.pop('restore')
            if 'restrict_outbound_network_access' in kwargs:
                properties['properties']['restrictOutboundNetworkAccess'] = kwargs.pop('restrict_outbound_network_access')
            if 'sku' in kwargs:
                properties['sku'] = {}
                properties['sku']['name'] = kwargs.pop('sku')
            if 'tags' in kwargs:
                properties['tags'] = kwargs.pop('tags')
            # for kwarg_name, param_name in _KWARG_CONVERSION.items():
            #     if kwarg_name in kwargs:
            #         account_params[param_name] = kwargs.pop(kwarg_name)
        super().__init__(
            properties,
            extensions=extensions,
            service_prefix=["ai"],
            existing=existing,
            **kwargs
        )
        self._supports_managed_identity = True

    @classmethod
    def reference(
            cls,
            *,
            name: str,
            resource_group: Optional[Union[str, ResourceGroup]] = None,
    ) -> 'CognitiveServicesAccount[ResourceReference]':
        from .types import RESOURCE, VERSION
        resource = f"{RESOURCE}@{VERSION}"
        return super().reference(
            resource=resource,
            name=name,
            resource_group=resource_group,
        )

    @property
    def resource(self) -> str:
        if self._resource:
            return self._resource
        from .types import RESOURCE
        self._resource = RESOURCE
        return self._resource

    @property
    def version(self) -> str:
        if self._version:
            return self._version
        from .types import VERSION
        self._version = VERSION
        return self._version

    def _find_last_resource_match(
            self,
            fields: FieldsType,
            *,
            resource: Optional[str] = None,
            resource_group: Optional[ResourceSymbol] = None,
            name: Optional[Union[str, Expression]] = None,
    ) -> Optional[FieldType]:
        resource = resource or self.resource
        for field in (f for f in reversed(list(fields.values())) if f.resource == resource):
            if resource == self.resource and field.properties['kind'] != self.properties['kind']:
            # field_kind = field.properties.get('kind')
            # if field_kind and kind != field_kind:
                continue
            if name and resource_group:
                if field.properties.get('name') == name and field.resource_group == resource_group:
                    return field
            elif resource_group:
                if field.resource_group == resource_group:
                    return field
            elif name:
                if field.properties.get('name') == name:
                    return field
            else:
                return field
        return None

    def _outputs(
            self,
            *,
            symbol: ResourceSymbol,
            attrname: Optional[str],
            **kwargs
    ) -> List[Output]:
        outputs = super()._outputs(symbol=symbol, attrname=attrname, **kwargs)
        outputs.append(Output(f"AZURE_AI_ENDPOINT{self._suffix}", "properties.endpoint", symbol))
        return outputs


class AIServicesKwargs(TypedDict, total=False):
    """"""
    custom_subdomain_name: Union[str, Parameter[str]]
    """Subdomain name used for token-based authentication. Required if 'networkAcls' or 'privateEndpoints' are set."""
    allowed_fqdn_list: Union[List[Union[str, Parameter[str]]], Parameter[List[str]]]
    """List of allowed FQDN."""
    disable_local_auth: Union[bool, Parameter[bool]]
    """Allow only Azure AD authentication. Should be enabled for security reasons."""
    dynamic_throttling_enabled: Union[bool, Parameter[bool]]
    """The flag to enable dynamic throttling."""
    location: Union[str, Parameter[str]]
    """Location for all Resources."""
    managed_identities: 'ManagedIdentity'
    """The managed identity definition for this resource."""
    migration_token: Union[str, Parameter[str]]
    """Resource migration token."""
    network_acls: Union['NetworkRuleSet', Parameter['NetworkRuleSet']]
    """A collection of rules governing the accessibility from specific network locations."""
    public_network_access: Union[Literal['Disabled', 'Enabled'], Parameter[str]]
    """Whether or not public network access is allowed for this resource. For security reasons it should be disabled. If not specified, it will be disabled by default if private endpoints are set and networkAcls are not set."""
    restore: Union[bool, Parameter[bool]]
    """Restore a soft-deleted cognitive service at deployment time. Will fail if no such soft-deleted resource exists."""
    restrict_outbound_network_access: Union[bool, Parameter[bool]]
    """Restrict outbound network access."""
    role_assignments: Union[Parameter[List[Union[str, 'RoleAssignment']]], List[Union[Parameter[Union[str, 'RoleAssignment']], 'RoleAssignment', Literal['Cognitive Services Contributor', 'Cognitive Services Custom Vision Contributor', 'Cognitive Services Custom Vision Deployment', 'Cognitive Services Custom Vision Labeler', 'Cognitive Services Custom Vision Reader', 'Cognitive Services Custom Vision Trainer', 'Cognitive Services Data Reader (Preview)', 'Cognitive Services Face Recognizer', 'Cognitive Services Immersive Reader User', 'Cognitive Services Language Owner', 'Cognitive Services Language Reader', 'Cognitive Services Language Writer', 'Cognitive Services LUIS Owner', 'Cognitive Services LUIS Reader', 'Cognitive Services LUIS Writer', 'Cognitive Services Metrics Advisor Administrator', 'Cognitive Services Metrics Advisor User', 'Cognitive Services OpenAI Contributor', 'Cognitive Services OpenAI User', 'Cognitive Services QnA Maker Editor', 'Cognitive Services QnA Maker Reader', 'Cognitive Services Speech Contributor', 'Cognitive Services Speech User', 'Cognitive Services User', 'Contributor', 'Owner', 'Reader', 'Role Based Access Control Administrator', 'User Access Administrator']]]]
    """Array of role assignments to create."""
    user_role: Union['RoleAssignment', Parameter[Union[str, 'RoleAssignment']], Literal['Cognitive Services Contributor', 'Cognitive Services Custom Vision Contributor', 'Cognitive Services Custom Vision Deployment', 'Cognitive Services Custom Vision Labeler', 'Cognitive Services Custom Vision Reader', 'Cognitive Services Custom Vision Trainer', 'Cognitive Services Data Reader (Preview)', 'Cognitive Services Face Recognizer', 'Cognitive Services Immersive Reader User', 'Cognitive Services Language Owner', 'Cognitive Services Language Reader', 'Cognitive Services Language Writer', 'Cognitive Services LUIS Owner', 'Cognitive Services LUIS Reader', 'Cognitive Services LUIS Writer', 'Cognitive Services Metrics Advisor Administrator', 'Cognitive Services Metrics Advisor User', 'Cognitive Services OpenAI Contributor', 'Cognitive Services OpenAI User', 'Cognitive Services QnA Maker Editor', 'Cognitive Services QnA Maker Reader', 'Cognitive Services Speech Contributor', 'Cognitive Services Speech User', 'Cognitive Services User', 'Contributor', 'Owner', 'Reader', 'Role Based Access Control Administrator', 'User Access Administrator']]
    """Role assignment to create for user principal ID"""
    sku: Union[Literal['C2', 'C3', 'C4', 'F0', 'F1', 'S', 'S0', 'S1', 'S10', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9'], Parameter[str]]
    """SKU of the Cognitive Services account. Use 'Get-AzCognitiveServicesAccountSku' to determine a valid combinations of 'kind' and 'SKU' for your Azure region."""
    tags: Union[Dict[str, Union[str, Parameter[str]]], Parameter[Dict]]
    """Tags of the resource."""
    # storage: List[object]
    # """The storage accounts for this resource."""


_DEFAULT_AI_SERVICES: 'CognitiveServicesAccountResource' = {'kind': 'AIServices'}


class AIServices(CognitiveServicesAccount[CognitiveServicesAccountAccountResourceType]):
    DEFAULTS: 'CognitiveServicesAccountResource' = _DEFAULT_AI_SERVICES

    def __init__(
            self,
            properties: Optional['CognitiveServicesAccountResource'] = None,
            /,
            name: Optional[str] = None,
            **kwargs: Unpack[AIServicesKwargs]
    ) -> None:
        super().__init__(
            properties,
            name=name,
            kind='AIServices',
            **kwargs
        )

    def _build_endpoint(self) -> str:
        return f"https://{self.name()}.openai.azure.com/"

    def _add_defaults(self, field: FieldType, parameters: Dict[str, Parameter]):
        super()._add_defaults(field, parameters)
        if 'kind' not in field.properties:
            field.properties['kind'] = 'AIServices'
        if 'publicNetworkAccess' not in field.properties['properties']:
            field.properties['properties']['publicNetworkAccess'] = 'Enabled'
        if 'disableLocalAuth' not in field.properties['properties']:
            field.properties['properties']['disableLocalAuth'] = True
        if 'sku' not in field.properties:
            field.properties['sku'] = {}
        if 'name' not in field.properties['sku']:
            field.properties['sku']['name'] = 'S0'
        # 'roleAssignments': [
        #     'Cognitive Services OpenAI Contributor',
        #     'Cognitive Services OpenAI User'
        # ]