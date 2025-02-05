from typing import TYPE_CHECKING, Any, Callable, Dict, List, Literal, Self, Type, TypeVar, TypedDict, Union, Unpack, Optional, overload

from azure.cloudmachine._bicep.expressions import Output, ResourceGroupSymbol, ResourceSymbol
from azure.cloudmachine.resources.resourcegroup._resource import ResourceGroup

from ..._resource import _ClientResource, Resource

if TYPE_CHECKING:
    from . import KeyVaultParams, RoleAssignment, PrivateEndpoint, Secret, AccessPolicy, DiagnosticSetting, Lock, Key


class KeyVaultKwargs(TypedDict, total=False):
    """"""
    access_policies: List['AccessPolicy']
    """All access policies to create."""
    create_mode: str
    """The vault's create mode to indicate whether the vault need to be recovered or not. - recover or default."""
    diagnostic_settings: List['DiagnosticSetting']
    """The diagnostic settings of the service."""
    enable_purge_protection: bool
    """Provide 'true' to enable Key Vault's purge protection feature."""
    enable_rbac_authorization: bool
    """Property that controls how data actions are authorized. When true, the key vault will use Role Based Access Control (RBAC) for authorization of data actions, and the access policies specified in vault properties will be ignored. When false, the key vault will use the access policies specified in vault properties, and any policy stored on Azure Resource Manager will be ignored. Note that management actions are always authorized with RBAC."""
    enable_soft_delete: bool
    """Switch to enable/disable Key Vault's soft delete feature."""
    enable_telemetry: bool
    """Enable/Disable usage telemetry for module."""
    enable_vault_for_deployment: bool
    """Specifies if the vault is enabled for deployment by script or compute."""
    enable_vault_for_disk_encryption: bool
    """Specifies if the azure platform has access to the vault for enabling disk encryption scenarios."""
    enable_vault_for_template_deployment: bool
    """Specifies if the vault is enabled for a template deployment."""
    keys: List['Key']
    """All keys to create."""
    location: str
    """Location for all resources."""
    lock: 'Lock'
    """The lock settings of the service."""
    network_acls: Dict[str, object]
    """Rules governing the accessibility of the resource from specific network locations."""
    private_endpoints: List['PrivateEndpoint']
    """Configuration details for private endpoints. For security reasons, it is recommended to use private endpoints whenever possible."""
    public_network_access: Literal['', 'Disabled', 'Enabled']
    """Whether or not public network access is allowed for this resource. For security reasons it should be disabled. If not specified, it will be disabled by default if private endpoints are set and networkAcls are not set."""
    role_assignments: List['RoleAssignment']
    """Array of role assignments to create."""
    secrets: List['Secret']
    """All secrets to create."""
    sku: Literal['premium', 'standard']
    """Specifies the SKU for the vault."""
    soft_delete_retention: int
    """softDelete data retention days. It accepts >=7 and <=90."""
    tags: Dict[str, object]
    """Resource tags."""


_DEFAULT_KEY_VAULT: 'KeyVaultParams' = {
    "sku": "standard",
}

_KWARG_CONVERSION: Dict[str, str] = {
    'access_policies': 'accessPolicies',
    'create_mode': 'createMode',
    'diagnostic_settings': 'diagnosticSettings',
    'enable_purge_protection': 'enablePurgeProtection',
    'enable_rbac_authorization': 'enableRbacAuthorization',
    'enable_soft_delete': 'enableSoftDelete',
    'enable_telemetry': 'enableTelemetry',
    'enable_vault_for_deployment': 'enableVaultForDeployment',
    'enable_vault_for_disk_encryption': 'enableVaultForDiskEncryption',
    'enable_vault_for_template_deployment': 'enableVaultForTemplateDeployment',
    'keys': 'keys',
    'location': 'location',
    'lock': 'lock',
    'network_acls': 'networkAcls',
    'private_endpoints': 'privateEndpoints',
    'public_network_access': 'publicNetworkAccess',
    'role_assignments': 'roleAssignments',
    'secrets': 'secrets',
    'sku': 'sku',
    'soft_delete_retention': 'softDeleteRetentionInDays',
    'tags': 'tags',
}
ClientType = TypeVar("ClientType")
 

class KeyVault(_ClientResource):
    identifier: Literal["keyvault"] = "keyvault"
    module: Literal["br/public:avm/res/key-vault/vault"] = "br/public:avm/res/key-vault/vault"
    DEFAULTS: 'KeyVaultParams' = _DEFAULT_KEY_VAULT
    resource: Literal["Microsoft.KeyVault/vaults"]
    properties: 'KeyVaultParams'

    def __init__(
            self,
            properties: Optional['KeyVaultParams'] = None,
            /,
            keyvault_name: Optional[str] = None,
            *,
            role_assignments: List[str] = ['Key Vault Administrator'],
            **kwargs: Unpack[KeyVaultKwargs]
    ) -> None:
        keyvault_params: 'KeyVaultParams' = properties or {}
        if keyvault_name:
            keyvault_params['name'] = keyvault_name
        for kwarg_name, param_name in _KWARG_CONVERSION.items():
            if kwarg_name in kwargs:
                keyvault_params[param_name] = kwargs.pop(kwarg_name)
        keyvault_params['roleAssignments'] = role_assignments
        super().__init__(
            properties=keyvault_params,
            service_prefix=["keyvault", "key_vault"],
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
    def reference(cls, resource_id: str, /) -> Self:
        ...
    @overload
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
        raise NotImplementedError()

    def _outputs(
            self,
             *,
             symbol: ResourceSymbol,
             attrname: Optional[str],
             resource_group: ResourceGroupSymbol,
             **kwargs
    ) -> Dict[str, Output]:
        outputs = super()._outputs(symbol=symbol, attrname=attrname, resource_group=resource_group)
        suffix = self._get_suffix()
        if self._existing:
            outputs[f"AZURE_KEYVAULT_ENDPOINT{suffix}"] = Output("properties.uri", symbol)
        else:
            outputs[f"AZURE_KEYVAULT_ENDPOINT{suffix}"] = Output("outputs.uri", symbol)
        return outputs
