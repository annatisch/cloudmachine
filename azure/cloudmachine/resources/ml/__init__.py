from typing import TYPE_CHECKING, TypedDict, Literal, List, Dict, Union
from typing_extensions import Required


if TYPE_CHECKING:
    from .compute import ComputeParams
    from .connection import ConnectionParams

MODULE = "br/public:avm/res/machine-learning-services/workspace"
MODULE_RESOURCE = "Microsoft.MachineLearningServices/workspaces"
MODULE_VERSION = "2024-04-01-preview"
MODULE_TAG = "0.10.0"


class ComputeRuntime(TypedDict, total=False):
    """Compute runtime config for feature store type workspace."""
    sparkRuntimeVersion: str
    """The spark runtime version."""


class FeatureStoreSetting(TypedDict, total=False):
    """Settings for feature store type workspaces. Required if 'kind' is set to 'FeatureStore'."""
    computeRuntime: 'ComputeRuntime'
    """Compute runtime config for feature store type workspace."""
    offlineStoreConnectionName: str
    """The offline store connection name."""
    onlineStoreConnectionName: str
    """The online store connection name."""


class CustomerManagedKey(TypedDict, total=False):
    """The customer managed key definition."""
    keyName: Required[str]
    """The name of the customer managed key to use for encryption."""
    keyVaultResourceId: Required[str]
    """The resource ID of a key vault to reference a customer managed key for encryption from."""
    keyVersion: str
    """The version of the customer managed key to reference for encryption. If not provided, the deployment will use the latest version available at deployment time."""
    userAssignedIdentityResourceId: str
    """User assigned identity to use when fetching the customer managed key. Required if no system assigned identity is available for use."""


class LogCategoriesAndGroup(TypedDict, total=False):
    """The name of logs that will be streamed. "allLogs" includes all possible logs for the resource. Set to """
    category: str
    """Name of a Diagnostic Log category for a resource type this setting is applied to. Set the specific logs to collect here."""
    categoryGroup: str
    """Name of a Diagnostic Log category group for a resource type this setting is applied to. Set to """
    enabled: bool
    """Enable or disable the category explicitly. Default is """


class MetricCategory(TypedDict, total=False):
    """The name of metrics that will be streamed. "allMetrics" includes all possible metrics for the resource. Set to """
    category: Required[str]
    """Name of a Diagnostic Metric category for a resource type this setting is applied to. Set to """
    enabled: bool
    """Enable or disable the category explicitly. Default is """


class DiagnosticSetting(TypedDict, total=False):
    """The diagnostic settings of the service."""
    eventHubAuthorizationRuleResourceId: str
    """Resource ID of the diagnostic event hub authorization rule for the Event Hubs namespace in which the event hub should be created or streamed to."""
    eventHubName: str
    """Name of the diagnostic event hub within the namespace to which logs are streamed. Without this, an event hub is created for each log category. For security reasons, it is recommended to set diagnostic settings to send data to either storage account, log analytics workspace or event hub."""
    logAnalyticsDestinationType: Literal['AzureDiagnostics', 'Dedicated']
    """A string indicating whether the export to Log Analytics should use the default destination type, i.e. AzureDiagnostics, or use a destination type."""
    logCategoriesAndGroups: List['LogCategoriesAndGroup']
    """The name of logs that will be streamed. "allLogs" includes all possible logs for the resource. Set to """
    marketplacePartnerResourceId: str
    """The full ARM resource ID of the Marketplace resource to which you would like to send Diagnostic Logs."""
    metricCategories: List['MetricCategory']
    """The name of metrics that will be streamed. "allMetrics" includes all possible metrics for the resource. Set to """
    name: str
    """The name of the diagnostic setting."""
    storageAccountResourceId: str
    """Resource ID of the diagnostic storage account. For security reasons, it is recommended to set diagnostic settings to send data to either storage account, log analytics workspace or event hub."""
    workspaceResourceId: str
    """Resource ID of the diagnostic log analytics workspace. For security reasons, it is recommended to set diagnostic settings to send data to either storage account, log analytics workspace or event hub."""


class Lock(TypedDict, total=False):
    """The lock settings of the service."""
    kind: Literal['CanNotDelete', 'None', 'ReadOnly']
    """Specify the type of lock."""
    name: str
    """Specify the name of lock."""


class ManagedIdentity(TypedDict, total=False):
    """The managed identity definition for this resource. At least one identity type is required."""
    systemAssigned: bool
    """Enables system assigned managed identity on the resource."""
    userAssignedResourceIds: List[object]
    """The resource ID(s) to assign to the resource. Required if a user assigned identity is used for encryption."""


class ManagedNetworkSetting(TypedDict, total=False):
    """Managed Network settings for a machine learning workspace."""
    isolationMode: Required[Literal['AllowInternetOutbound', 'AllowOnlyApprovedOutbound', 'Disabled']]
    """Isolation mode for the managed network of a machine learning workspace."""
    outboundRules: Dict[str, object]
    """Outbound rules for the managed network of a machine learning workspace."""


class CustomDnsConfig(TypedDict, total=False):
    """Custom DNS configurations."""
    ipAddresses: Required[List[object]]
    """A list of private IP addresses of the private endpoint."""
    fqdn: str
    """FQDN that resolves to private endpoint IP address."""


class IpConfigurationProperties(TypedDict, total=False):
    """Properties of private endpoint IP configurations."""
    groupId: Required[str]
    """The ID of a group obtained from the remote resource that this private endpoint should connect to."""
    memberName: Required[str]
    """The member name of a group obtained from the remote resource that this private endpoint should connect to."""
    privateIPAddress: Required[str]
    """A private IP address obtained from the private endpoint's subnet."""


class IpConfiguration(TypedDict, total=False):
    """A list of IP configurations of the Private Endpoint. This will be used to map to the first-party Service endpoints."""
    name: Required[str]
    """The name of the resource that is unique within a resource group."""
    properties: Required['IpConfigurationProperties']
    """Properties of private endpoint IP configurations."""


class Lock(TypedDict, total=False):
    """Specify the type of lock."""
    kind: Literal['CanNotDelete', 'None', 'ReadOnly']
    """Specify the type of lock."""
    name: str
    """Specify the name of lock."""


class PrivateDnsZoneGroupConfig(TypedDict, total=False):
    """The private DNS Zone Groups to associate the Private Endpoint. A DNS Zone Group can support up to 5 DNS zones."""
    privateDnsZoneResourceId: Required[str]
    """The resource id of the private DNS zone."""
    name: str
    """The name of the private DNS Zone Group config."""


class PrivateDnsZoneGroup(TypedDict, total=False):
    """The private DNS Zone Group to configure for the Private Endpoint."""
    privateDnsZoneGroupConfigs: Required[List['PrivateDnsZoneGroupConfig']]
    """The private DNS Zone Groups to associate the Private Endpoint. A DNS Zone Group can support up to 5 DNS zones."""
    name: str
    """The name of the Private DNS Zone Group."""


class RoleAssignment(TypedDict, total=False):
    """Array of role assignments to create."""
    principalId: Required[str]
    """The principal ID of the principal (user/group/identity) to assign the role to."""
    roleDefinitionIdOrName: Required[Union[str, Literal['Contributor', 'DNS Resolver Contributor', 'DNS Zone Contributor', 'Domain Services Contributor', 'Domain Services Reader', 'Network Contributor', 'Owner', 'Private DNS Zone Contributor', 'Reader', 'Role Based Access Control Administrator (Preview)']]]
    """The role to assign. You can provide either the display name of the role definition, the role definition GUID, or its fully qualified ID in the following format: '/providers/Microsoft.Authorization/roleDefinitions/c2f4ef07-c644-48eb-af81-4b1b4947fb11'."""
    condition: str
    """The conditions on the role assignment. This limits the resources it can be assigned to. e.g.: @Resource[Microsoft.Storage/storageAccounts/blobServices/containers:ContainerName] StringEqualsIgnoreCase "foo_storage_container"."""
    conditionVersion: Literal['2.0']
    """Version of the condition."""
    delegatedManagedIdentityResourceId: str
    """The Resource Id of the delegated managed identity resource."""
    description: str
    """The description of the role assignment."""
    name: str
    """The name (as GUID) of the role assignment. If not provided, a GUID will be generated."""
    principalType: Literal['Device', 'ForeignGroup', 'Group', 'ServicePrincipal', 'User']
    """The principal type of the assigned principal ID."""


class PrivateEndpoint(TypedDict, total=False):
    """Configuration details for private endpoints. For security reasons, it is recommended to use private endpoints whenever possible."""
    subnetResourceId: Required[str]
    """Resource ID of the subnet where the endpoint needs to be created."""
    applicationSecurityGroupResourceIds: List[object]
    """Application security groups in which the Private Endpoint IP configuration is included."""
    customDnsConfigs: List['CustomDnsConfig']
    """Custom DNS configurations."""
    customNetworkInterfaceName: str
    """The custom name of the network interface attached to the Private Endpoint."""
    enableTelemetry: bool
    """Enable/Disable usage telemetry for module."""
    ipConfigurations: List['IpConfiguration']
    """A list of IP configurations of the Private Endpoint. This will be used to map to the first-party Service endpoints."""
    isManualConnection: bool
    """If Manual Private Link Connection is required."""
    location: str
    """The location to deploy the Private Endpoint to."""
    lock: 'Lock'
    """Specify the type of lock."""
    manualConnectionRequestMessage: str
    """A message passed to the owner of the remote resource with the manual connection request."""
    name: str
    """The name of the Private Endpoint."""
    privateDnsZoneGroup: 'PrivateDnsZoneGroup'
    """The private DNS Zone Group to configure for the Private Endpoint."""
    privateLinkServiceConnectionName: str
    """The name of the private link connection to create."""
    resourceGroupName: str
    """Specify if you want to deploy the Private Endpoint into a different Resource Group than the main resource."""
    roleAssignments: List['RoleAssignment']
    """Array of role assignments to create."""
    service: str
    """The subresource to deploy the Private Endpoint for. For example "vault" for a Key Vault Private Endpoint."""
    tags: Dict[str, object]
    """Tags to be applied on all resources/Resource Groups in this deployment."""


class RoleAssignment(TypedDict, total=False):
    """Array of role assignments to create."""
    principalId: Required[str]
    """The principal ID of the principal (user/group/identity) to assign the role to."""
    roleDefinitionIdOrName: Required[Union[str, Literal['AzureML Compute Operator', 'AzureML Data Scientist', 'AzureML Metrics Writer (preview)', 'AzureML Registry User', 'Contributor', 'Owner', 'Reader', 'Role Based Access Control Administrator', 'User Access Administrator']]]
    """The role to assign. You can provide either the display name of the role definition, the role definition GUID, or its fully qualified ID in the following format: '/providers/Microsoft.Authorization/roleDefinitions/c2f4ef07-c644-48eb-af81-4b1b4947fb11'."""
    condition: str
    """The conditions on the role assignment. This limits the resources it can be assigned to. e.g.: @Resource[Microsoft.Storage/storageAccounts/blobServices/containers:ContainerName] StringEqualsIgnoreCase "foo_storage_container"."""
    conditionVersion: Literal['2.0']
    """Version of the condition."""
    delegatedManagedIdentityResourceId: str
    """The Resource Id of the delegated managed identity resource."""
    description: str
    """The description of the role assignment."""
    name: str
    """The name (as GUID) of the role assignment. If not provided, a GUID will be generated."""
    principalType: Literal['Device', 'ForeignGroup', 'Group', 'ServicePrincipal', 'User']
    """The principal type of the assigned principal ID."""


class ServerlessComputeSetting(TypedDict, total=False):
    """Settings for serverless compute created in the workspace."""
    serverlessComputeCustomSubnet: str
    """The resource ID of an existing virtual network subnet in which serverless compute nodes should be deployed."""
    serverlessComputeNoPublicIP: bool
    """The flag to signal if serverless compute nodes deployed in custom vNet would have no public IP addresses for a workspace with private endpoint."""


class WorkspaceHubConfig(TypedDict, total=False):
    """Configuration for workspace hub settings."""
    additionalWorkspaceStorageAccounts: List[object]
    """The resource IDs of additional storage accounts to attach to the workspace."""
    defaultWorkspaceResourceGroup: str
    """The resource ID of the default resource group for projects created in the workspace hub."""


class MachineLearningServicesWorkspaceParams(TypedDict, total=False):
    """"""
    name: str
    """The name of the machine learning workspace."""
    sku: Literal['Basic', 'Free', 'Premium', 'Standard']
    """Specifies the SKU, also referred as 'edition' of the Azure Machine Learning workspace."""
    associatedApplicationInsightsResourceId: str
    """The resource ID of the associated Application Insights. Required if 'kind' is 'Default' or 'FeatureStore'."""
    associatedKeyVaultResourceId: str
    """The resource ID of the associated Key Vault. Required if 'kind' is 'Default', 'FeatureStore' or 'Hub'."""
    associatedStorageAccountResourceId: str
    """The resource ID of the associated Storage Account. Required if 'kind' is 'Default', 'FeatureStore' or 'Hub'."""
    featureStoreSettings: 'FeatureStoreSetting'
    """Settings for feature store type workspaces. Required if 'kind' is set to 'FeatureStore'."""
    hubResourceId: str
    """The resource ID of the hub to associate with the workspace. Required if 'kind' is set to 'Project'."""
    primaryUserAssignedIdentity: str
    """The user assigned identity resource ID that represents the workspace identity. Required if 'userAssignedIdentities' is not empty and may not be used if 'systemAssignedIdentity' is enabled."""
    associatedContainerRegistryResourceId: str
    """The resource ID of the associated Container Registry."""
    computes: List['ComputeParams']
    """Computes to create respectively attach to the workspace."""
    connections: List['ConnectionParams']
    """Connections to create in the workspace."""
    customerManagedKey: 'CustomerManagedKey'
    """The customer managed key definition."""
    description: str
    """The description of this workspace."""
    diagnosticSettings: List['DiagnosticSetting']
    """The diagnostic settings of the service."""
    discoveryUrl: str
    """URL for the discovery service to identify regional endpoints for machine learning experimentation services."""
    enableTelemetry: bool
    """Enable/Disable usage telemetry for module."""
    hbiWorkspace: bool
    """The flag to signal HBI data in the workspace and reduce diagnostic data collected by the service."""
    imageBuildCompute: str
    """The compute name for image build."""
    kind: Literal['Default', 'FeatureStore', 'Hub', 'Project']
    """The type of Azure Machine Learning workspace to create."""
    location: str
    """Location for all resources."""
    lock: 'Lock'
    """The lock settings of the service."""
    managedIdentities: 'ManagedIdentity'
    """The managed identity definition for this resource. At least one identity type is required."""
    managedNetworkSettings: 'ManagedNetworkSetting'
    """Managed Network settings for a machine learning workspace."""
    privateEndpoints: List['PrivateEndpoint']
    """Configuration details for private endpoints. For security reasons, it is recommended to use private endpoints whenever possible."""
    publicNetworkAccess: Literal['Disabled', 'Enabled']
    """Whether or not public network access is allowed for this resource. For security reasons it should be disabled."""
    roleAssignments: List['RoleAssignment']
    """Array of role assignments to create."""
    serverlessComputeSettings: 'ServerlessComputeSetting'
    """Settings for serverless compute created in the workspace."""
    serviceManagedResourcesSettings: Dict[str, object]
    """The service managed resource settings."""
    sharedPrivateLinkResources: List[object]
    """The list of shared private link resources in this workspace. Note: This property is not idempotent."""
    systemDatastoresAuthMode: Literal['accessKey', 'identity']
    """The authentication mode used by the workspace when connecting to the default storage account."""
    tags: Dict[str, object]
    """Resource tags."""
    workspaceHubConfig: 'WorkspaceHubConfig'
    """Configuration for workspace hub settings."""
