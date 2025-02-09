from typing import TYPE_CHECKING, Any, Dict, List, Literal, Self, TypedDict, Union, Unpack, Optional, overload

from azure.cloudmachine.resources.resourcegroup._resource import ResourceGroup

from ..._bicep.expressions import Expression, Output, Parameter, ResourceSymbol
from ..._resource import Resource, FieldsType, FieldType

if TYPE_CHECKING:
    from . import (
        MachineLearningServicesWorkspaceParams,
        FeatureStoreSetting,
        ComputeParams,
        ConnectionParams,
        CustomerManagedKey,
        ManagedIdentity,
        ManagedNetworkSetting,
        DiagnosticSetting,
        RoleAssignment,
        PrivateEndpoint,
        ServerlessComputeSetting,
        WorkspaceHubConfig
    )


_DEFAULT_WORKSPACE: 'MachineLearningServicesWorkspaceParams' = {
    'sku': 'Basic',
    'kind': 'Default'
}

_SUPPORTED_SYSTEM_TOPICS: Dict[str, str] = {
    "br/public:avm/res/storage/storage-account": "Microsoft.Storage.StorageAccounts"
}

class MachineLearningServicesWorkspaceKwargs(TypedDict, total=False):
    """"""
    sku: Literal['Basic', 'Free', 'Premium', 'Standard']
    """Specifies the SKU, also referred as 'edition' of the Azure Machine Learning workspace."""
    application_insights: str
    """The resource ID of the associated Application Insights. Required if 'kind' is 'Default' or 'FeatureStore'."""
    keyvault: str
    """The resource ID of the associated Key Vault. Required if 'kind' is 'Default', 'FeatureStore' or 'Hub'."""
    storage_account: str
    """The resource ID of the associated Storage Account. Required if 'kind' is 'Default', 'FeatureStore' or 'Hub'."""
    feature_store_settings: 'FeatureStoreSetting'
    """Settings for feature store type workspaces. Required if 'kind' is set to 'FeatureStore'."""
    hub: str
    """The resource ID of the hub to associate with the workspace. Required if 'kind' is set to 'Project'."""
    primary_user_assigned_identity: str
    """The user assigned identity resource ID that represents the workspace identity. Required if 'userAssignedIdentities' is not empty and may not be used if 'systemAssignedIdentity' is enabled."""
    container_registry: str
    """The resource ID of the associated Container Registry."""
    computes: List['ComputeParams']
    """Computes to create respectively attach to the workspace."""
    connections: List['ConnectionParams']
    """Connections to create in the workspace."""
    customer_managed_key: 'CustomerManagedKey'
    """The customer managed key definition."""
    description: str
    """The description of this workspace."""
    diagnostic_settings: List['DiagnosticSetting']
    """The diagnostic settings of the service."""
    discovery_url: str
    """URL for the discovery service to identify regional endpoints for machine learning experimentation services."""
    enable_telemetry: bool
    """Enable/Disable usage telemetry for module."""
    hbi_workspace: bool
    """The flag to signal HBI data in the workspace and reduce diagnostic data collected by the service."""
    image_build_compute: str
    """The compute name for image build."""
    kind: Literal['Default', 'FeatureStore', 'Hub', 'Project']
    """The type of Azure Machine Learning workspace to create."""
    location: str
    """Location for all resources."""
    lock: 'Lock'
    """The lock settings of the service."""
    managed_identities: 'ManagedIdentity'
    """The managed identity definition for this resource. At least one identity type is required."""
    managed_network_settings: 'ManagedNetworkSetting'
    """Managed Network settings for a machine learning workspace."""
    private_endpoints: List['PrivateEndpoint']
    """Configuration details for private endpoints. For security reasons, it is recommended to use private endpoints whenever possible."""
    public_network_access: Literal['Disabled', 'Enabled']
    """Whether or not public network access is allowed for this resource. For security reasons it should be disabled."""
    role_assignments: List['RoleAssignment']
    """Array of role assignments to create."""
    serverless_compute_settings: 'ServerlessComputeSetting'
    """Settings for serverless compute created in the workspace."""
    service_managed_resources_settings: Dict[str, object]
    """The service managed resource settings."""
    shared_private_link_resources: List[object]
    """The list of shared private link resources in this workspace. Note: This property is not idempotent."""
    system_datastores_auth_mode: Literal['accessKey', 'identity']
    """The authentication mode used by the workspace when connecting to the default storage account."""
    tags: Dict[str, object]
    """Resource tags."""
    workspacehub_config: 'WorkspaceHubConfig'
    """Configuration for workspace hub settings."""


_KWARG_CONVERSION: Dict[str, str] = {
        'sku': 'sku',
        'application_insights': 'associatedApplicationInsightsResourceId',
        'keyvault': 'associatedKeyVaultResourceId',
        'storage_account': 'associatedStorageAccountResourceId',
        'feature_store_settings': 'featureStoreSettings',
        'hub': 'hubResourceId',
        'primary_user_assigned_identity': 'primaryUserAssignedIdentity',
        'container_registry': 'associatedContainerRegistryResourceId',
        'customer_managed_key': 'customerManagedKey',
        'description': 'description',
        'diagnostic_settings': 'diagnosticSettings',
        'discovery_url': 'discoveryUrl',
        'enable_telemetry': 'enableTelemetry',
        'hbi_workspace': 'hbiWorkspace',
        'image_build_compute': 'imageBuildCompute',
        'kind': 'kind',
        'location': 'location',
        'lock': 'lock',
        'managed_identities': 'managedIdentities',
        'managed_network_settings': 'managedNetworkSettings',
        'private_endpoints': 'privateEndpoints',
        'public_network_access': 'publicNetworkAccess',
        'role_assignments': 'roleAssignments',
        'serverless_compute_settings': 'serverlessComputeSettings',
        'service_managed_resources_settings': 'serviceManagedResourcesSettings',
        'shared_private_link_resources': 'sharedPrivateLinkResources',
        'system_datastores_auth_mode': 'systemDatastoresAuthMode',
        'tags': 'tags',
        'workspacehub_config': 'workspaceHubConfig',
}


class MLWorkspace(Resource):
    identifier: Literal["ml:workspace"] = "ml:workspace"
    module: Literal["br/public:avm/res/machine-learning-services/workspace"] = "br/public:avm/res/machine-learning-services/workspace"
    DEFAULTS: 'MachineLearningServicesWorkspaceParams' = _DEFAULT_WORKSPACE
    resource: Literal["Microsoft.MachineLearningServices/workspaces"] = "Microsoft.MachineLearningServices/workspaces"
    properties: 'MachineLearningServicesWorkspaceParams'

    def __init__(
            self,
            properties: Optional['MachineLearningServicesWorkspaceParams'] = None,
            workspace_name: Optional[str] = None,
            **kwargs: Unpack['MachineLearningServicesWorkspaceKwargs']
    ) -> None:
        workspace_params: 'MachineLearningServicesWorkspaceParams' = properties or {}
        if workspace_name:
            workspace_params['name'] = workspace_name
        for kwarg_name, param_name in _KWARG_CONVERSION.items():
            if kwarg_name in kwargs:
                workspace_params[param_name] = kwargs.pop(kwarg_name)
        super().__init__(
            properties=workspace_params,
            service_prefix=["ml_workspace"],
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

    def _merge_params(
            self,
            params: 'MachineLearningServicesWorkspaceParams',
            *,
            symbol: ResourceSymbol,
            attrname: Optional[str] = None,
            identity: Optional[ResourceSymbol],
            **kwargs
    ) -> Dict[str, Any]:
        output_config = super()._merge_params(params, symbol=symbol, attrname=attrname, **kwargs)
        if not params.get('primaryUserAssignedIdentity'):
            params['primaryUserAssignedIdentity'] = identity.id
        return output_config


_DEFAULT_AI_HUB: 'MachineLearningServicesWorkspaceParams' = {
    'publicNetworkAccess': 'Enabled',
    'sku': 'Basic',
}

class AIHub(MLWorkspace):
    identifier: Literal["ai:hub"] = "ai:hub"
    DEFAULTS: 'MachineLearningServicesWorkspaceParams' = _DEFAULT_AI_HUB
    resource: Literal["Microsoft.MachineLearningServices/workspaces"] = "Microsoft.MachineLearningServices/workspaces"
    properties: 'MachineLearningServicesWorkspaceParams'

    def __init__(
            self,
            properties: 'MachineLearningServicesWorkspaceParams' = None,
            hub_name: Optional[str] = None,
            **kwargs: Unpack[MachineLearningServicesWorkspaceKwargs] #TODO: Use kwargs subset
    ):
        super().__init__(
            properties=properties,
            workspace_name=hub_name,
            kind="Hub",
            **kwargs
        )

    def _merge_params(
            self,
            params: 'MachineLearningServicesWorkspaceParams',
            *,
            symbol: ResourceSymbol,
            fields: FieldsType,
            attrname: Optional[str] = None,
            identity: Optional[ResourceSymbol],
            resource_group: ResourceSymbol,
            **kwargs
    ) -> Dict[str, Any]:
        output_config = super()._merge_params(
            params,
            symbol=symbol,
            attrname=attrname,
            fields=fields,
            identity=identity,
            resource_group=resource_group,
            **kwargs
        )
        if not params.get('associatedStorageAccountResourceId'):
            storage_resource = [
                "br/public:avm/res/storage/storage-account",
                "Microsoft.Storage/storageAccounts"
            ]
            storage = self._find_field(storage_resource, fields)
            if not storage:
                raise ValueError("Cannot create AI Hub without associated Storage account.")
            params['associatedStorageAccountResourceId'] = storage.symbol.id
            if storage.params.get('managedIdentities'):
                params['systemDatastoresAuthMode'] = 'identity'
        if not params.get('associatedKeyVaultResourceId'):
            keyvault_resource = [
                "br/public:avm/res/key-vault/vault",
                "Microsoft.KeyVault/vaults"
            ]
            vault = self._find_field(keyvault_resource, fields)
            if not vault:
                raise ValueError("Cannot create an AI Hub without associated KeyVault account.")
            params['associatedKeyVaultResourceId'] = vault.symbol.id
        if not params.get('workspaceHubConfig'):
            params['workspaceHubConfig'] = {
                'defaultWorkspaceResourceGroup': resource_group.id
            }
        return output_config


_DEFAULT_AI_PROJECT: 'MachineLearningServicesWorkspaceParams' = {
    'sku': 'Basic'
}


class AIProject(MLWorkspace):
    identifier: Literal["ai:project"] = "ai:project"
    DEFAULTS: 'MachineLearningServicesWorkspaceParams' = _DEFAULT_AI_PROJECT

    def __init__(
            self,
            properties: 'MachineLearningServicesWorkspaceParams' = None,
            project_name: Optional[str] = None,
            **kwargs: Unpack[MachineLearningServicesWorkspaceKwargs]
    ):
        super().__init__(
            properties=properties,
            workspace_name=project_name,
            kind="Project",
            **kwargs
        )

    def _merge_params(
            self,
            params: 'MachineLearningServicesWorkspaceParams',
            *,
            symbol: ResourceSymbol,
            fields: FieldsType,
            attrname: Optional[str] = None,
            identity: Optional[ResourceSymbol],
            **kwargs
    ) -> Dict[str, Any]:
        output_config = super()._merge_params(
            params,
            symbol=symbol,
            attrname=attrname,
            fields=fields,
            identity=identity,
            **kwargs
        )
        if not params.get('hubResourceId'):
            hub_resource = [
                "br/public:avm/res/machine-learning-services/workspace",
                "Microsoft.MachineLearningServices/workspaces"
            ]
            index = 0
            hub = self._find_field(hub_resource, fields)
            while hub:
                if hub[1]['kind'] == 'Hub':
                    break
                index += 1
                hub = self._find_field(hub_resource, fields, index=index)
            if not hub:
                raise ValueError("Cannot create Project Workspace without a Hub Workspace.")
            params['hubResourceId'] = hub[2].id
        params['systemDatastoresAuthMode'] = 'identity'
        return output_config
