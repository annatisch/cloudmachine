from typing import TYPE_CHECKING, Any, Callable, Dict, List, Literal, Self, Type, TypeVar, TypedDict, Union, Unpack, Optional, overload

from azure.cloudmachine._bicep.expressions import Output, ResourceSymbol
from azure.cloudmachine.resources.resourcegroup._resource import ResourceGroup

from ..._resource import _ClientResource, Resource

if TYPE_CHECKING:
    from . import (
        SearchServiceParams,
        ManagedIdentity,
        RoleAssignment,
        PrivateEndpoint,
        DiagnosticSetting,
        AuthOption,
        NetworkRuleSet,
        SecretsExportConfiguration,
        SharedPrivateLinkResource,
        Lock
    )


class SearchServiceKwargs(TypedDict, total=False):
    auth_options: 'AuthOption'
    """Defines the options for how the data plane API of a Search service authenticates requests. Must remain an empty object {} if 'disableLocalAuth' is set to true."""
    cmk_enforcement: Literal['Disabled', 'Enabled', 'Unspecified']
    """Describes a policy that determines how resources within the search service are to be encrypted with Customer Managed Keys."""
    diagnostic_settings: List['DiagnosticSetting']
    """The diagnostic settings of the service."""
    disable_local_auth: bool
    """When set to true, calls to the search service will not be permitted to utilize API keys for authentication. This cannot be set to true if 'authOptions' are defined."""
    enable_telemetry: bool
    """Enable/Disable usage telemetry for module."""
    hosting_mode: Literal['default', 'highDensity']
    """Applicable only for the standard3 SKU. You can set this property to enable up to 3 high density partitions that allow up to 1000 indexes, which is much higher than the maximum indexes allowed for any other SKU. For the standard3 SKU, the value is either 'default' or 'highDensity'. For all other SKUs, this value must be 'default'."""
    location: str
    """Location for all Resources."""
    lock: 'Lock'
    """The lock settings for all Resources in the solution."""
    managed_identities: 'ManagedIdentity'
    """The managed identity definition for this resource."""
    network_rule_set: 'NetworkRuleSet'
    """Network specific rules that determine how the Azure Cognitive Search service may be reached."""
    partition_count: int
    """The number of partitions in the search service; if specified, it can be 1, 2, 3, 4, 6, or 12. Values greater than 1 are only valid for standard SKUs. For 'standard3' services with hostingMode set to 'highDensity', the allowed values are between 1 and 3."""
    private_endpoints: List['PrivateEndpoint']
    """Configuration details for private endpoints. For security reasons, it is recommended to use private endpoints whenever possible."""
    public_network_access: Literal['Disabled', 'Enabled']
    """This value can be set to 'Enabled' to avoid breaking changes on existing customer resources and templates. If set to 'Disabled', traffic over public interface is not allowed, and private endpoint connections would be the exclusive access method."""
    replica_count: int
    """The number of replicas in the search service. If specified, it must be a value between 1 and 12 inclusive for standard SKUs or between 1 and 3 inclusive for basic SKU."""
    role_assignments: List['RoleAssignment']
    """Array of role assignments to create."""
    secrets_export_configuration: 'SecretsExportConfiguration'
    """Key vault reference and secret settings for the module's secrets export."""
    semantic_search: Literal['disabled', 'free', 'standard']
    """Sets options that control the availability of semantic search. This configuration is only possible for certain search SKUs in certain locations."""
    shared_private_link_resources: List['SharedPrivateLinkResource']
    """The sharedPrivateLinkResources to create as part of the search Service."""
    sku: Literal['basic', 'free', 'standard', 'standard2', 'standard3', 'storage_optimized_l1', 'storage_optimized_l2']
    """Defines the SKU of an Azure Cognitive Search Service, which determines price tier and capacity limits."""
    tags: Dict[str, object]
    """Tags to help categorize the resource in the Azure portal."""



_DEFAULT_SEARCH_SERVICE: 'SearchServiceParams' = {
    "sku": "basic",
    "semanticSearch": "free",
    "replicaCount": 1,
    "hostingMode": "default",
    "roleAssignments": ["Search Service Contributor"]
}

_KWARG_CONVERSION: Dict[str, str] = {
    'auth_options': 'authOptions',
    'cmk_enforcement': 'cmkEnforcement',
    'diagnostic_settings': 'diagnosticSettings',
    'disable_local_auth': 'disableLocalAuth',
    'enable_telemetry': 'enableTelemetry',
    'hosting_mode': 'hostingMode',
    'location': 'location',
    'lock': 'lock',
    'managed_identities': 'managedIdentities',
    'network_rule_set': 'networkRuleSet',
    'partition_count': 'partitionCount',
    'private_endpoints': 'privateEndpoints',
    'public_network_access': 'publicNetworkAccess',
    'replica_count': 'replicaCount',
    'role_assignments': 'roleAssignments',
    'secrets_export_configuration': 'secretsExportConfiguration',
    'semantic_search': 'semanticSearch',
    'shared_private_link_resources': 'sharedPrivateLinkResources',
    'sku': 'sku',
    'tags': 'tags',

}
ClientType = TypeVar("ClientType")
 

class SearchService(_ClientResource):
    identifier: Literal["search"] = "search"
    module: Literal["br/public:avm/res/search/search-service"] = "br/public:avm/res/search/search-service"
    DEFAULTS: 'SearchServiceParams' = _DEFAULT_SEARCH_SERVICE
    resource: Literal["Microsoft.Search/searchServices"]
    properties: 'SearchServiceParams'

    def __init__(
            self,
            properties: Optional['SearchServiceParams'] = None,
            /,
            search_name: Optional[str] = None,
            **kwargs: Unpack[SearchServiceKwargs]
    ) -> None:
        search_params: 'SearchServiceParams' = properties or {}
        if search_name:
            search_params['name'] = search_name
        for kwarg_name, param_name in _KWARG_CONVERSION.items():
            if kwarg_name in kwargs:
                search_params[param_name] = kwargs.pop(kwarg_name)
        super().__init__(
            properties=search_params,
            service_prefix=["search"],
            **kwargs
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

    def _build_endpoint(self) -> str:
        return f"https://{self.name()}.search.windows.net/"

    def _outputs(
            self,
             *,
             symbol: ResourceSymbol,
             attrname: Optional[str],
             resource_group: ResourceSymbol,
             **kwargs
    ) -> Dict[str, Output]:
        outputs = super()._outputs(symbol=symbol, attrname=attrname, resource_group=resource_group)
        suffix = self._get_suffix()
        if self._existing:
            outputs[f"AZURE_SEARCH_ENDPOINT{suffix}"] = Output(
                "outputs.name",
                symbol
            ).format(prefix="https://", suffix=".search.windows.net/")
        else:
            outputs[f"AZURE_SEARCH_ENDPOINT{suffix}"] = Output(
                "name",
                symbol
            ).format(prefix="https://", suffix=".search.windows.net/")
        return outputs
