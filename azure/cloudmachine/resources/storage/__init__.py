from typing import TYPE_CHECKING, TypedDict, Literal, List, Dict, Union
from typing_extensions import Required

if TYPE_CHECKING:
    from .blobs import BlobServiceParams

MODULE = "br/public:avm/res/storage/storage-account"
MODULE_RESOURCE = "Microsoft.Storage/storageAccounts"
MODULE_VERSION = "0.14.0"


class CustomerManagedKey(TypedDict, total=False):
    """The customer managed key definition."""
    keyName: Required[str]
    """The name of the customer managed key to use for encryption."""
    keyVaultResourceId: Required[str]
    """The resource ID of a key vault to reference a customer managed key for encryption from."""
    keyVersion: str
    """The version of the customer managed key to reference for encryption. If not provided, using 'latest'."""
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
    """The managed identity definition for this resource."""
    systemAssigned: bool
    """Enables system assigned managed identity on the resource."""
    userAssignedResourceIds: List[object]
    """The resource ID(s) to assign to the resource. Required if a user assigned identity is used for encryption."""


class ResourceAccessRule(TypedDict, total=False):
    """Sets the resource access rules. Array entries must consist of "tenantId" and "resourceId" fields only."""
    resourceId: Required[str]
    """The resource ID of the target service. Can also contain a wildcard, if multiple services e.g. in a resource group should be included."""
    tenantId: Required[str]
    """The ID of the tenant in which the resource resides in."""


class NetworkAcl(TypedDict, total=False):
    """Networks ACLs, this value contains IPs to whitelist and/or Subnet information. If in use, bypass needs to be supplied. For security reasons, it is recommended to set the DefaultAction Deny."""
    bypass: Literal['AzureServices', 'AzureServices, Logging', 'AzureServices, Logging, Metrics', 'AzureServices, Metrics', 'Logging', 'Logging, Metrics', 'Metrics', 'None']
    """Specifies whether traffic is bypassed for Logging/Metrics/AzureServices. Possible values are any combination of Logging,Metrics,AzureServices (For example, "Logging, Metrics"), or None to bypass none of those traffics."""
    defaultAction: Literal['Allow', 'Deny']
    """Specifies the default action of allow or deny when no other rules match."""
    ipRules: List[object]
    """Sets the IP ACL rules."""
    resourceAccessRules: List['ResourceAccessRule']
    """Sets the resource access rules. Array entries must consist of "tenantId" and "resourceId" fields only."""
    virtualNetworkRules: List[object]
    """Sets the virtual network rules."""


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
    """A list of IP configurations of the private endpoint. This will be used to map to the First Party Service endpoints."""
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
    """The private DNS zone group to configure for the private endpoint."""
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
    service: Required[str]
    """The subresource to deploy the private endpoint for. For example "blob", "table", "queue" or "file" for a Storage Account's Private Endpoints."""
    subnetResourceId: Required[str]
    """Resource ID of the subnet where the endpoint needs to be created."""
    applicationSecurityGroupResourceIds: List[object]
    """Application security groups in which the private endpoint IP configuration is included."""
    customDnsConfigs: List['CustomDnsConfig']
    """Custom DNS configurations."""
    customNetworkInterfaceName: str
    """The custom name of the network interface attached to the private endpoint."""
    enableTelemetry: bool
    """Enable/Disable usage telemetry for module."""
    ipConfigurations: List['IpConfiguration']
    """A list of IP configurations of the private endpoint. This will be used to map to the First Party Service endpoints."""
    isManualConnection: bool
    """If Manual Private Link Connection is required."""
    location: str
    """The location to deploy the private endpoint to."""
    lock: 'Lock'
    """Specify the type of lock."""
    manualConnectionRequestMessage: str
    """A message passed to the owner of the remote resource with the manual connection request."""
    name: str
    """The name of the private endpoint."""
    privateDnsZoneGroup: 'PrivateDnsZoneGroup'
    """The private DNS zone group to configure for the private endpoint."""
    privateLinkServiceConnectionName: str
    """The name of the private link connection to create."""
    resourceGroupName: str
    """Specify if you want to deploy the Private Endpoint into a different resource group than the main resource."""
    roleAssignments: List['RoleAssignment']
    """Array of role assignments to create."""
    tags: Dict[str, object]
    """Tags to be applied on all resources/resource groups in this deployment."""


class RoleAssignment(TypedDict, total=False):
    """Array of role assignments to create."""
    principalId: Required[str]
    """The principal ID of the principal (user/group/identity) to assign the role to."""
    roleDefinitionIdOrName: Required[Union[str, Literal['Contributor', 'Owner', 'Reader', 'Reader and Data Access', 'Role Based Access Control Administrator', 'Storage Account Backup Contributor', 'Storage Account Contributor', 'Storage Account Key Operator Service Role', 'Storage Blob Data Contributor', 'Storage Blob Data Owner', 'Storage Blob Data Reader', 'Storage Blob Delegator', 'Storage File Data Privileged Contributor', 'Storage File Data Privileged Reader', 'Storage File Data SMB Share Contributor', 'Storage File Data SMB Share Elevated Contributor', 'Storage File Data SMB Share Reader', 'Storage Queue Data Contributor', 'Storage Queue Data Message Processor', 'Storage Queue Data Message Sender', 'Storage Queue Data Reader', 'Storage Table Data Contributor', 'Storage Table Data Reader', 'User Access Administrator']]]
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


class SecretsExportConfiguration(TypedDict, total=False):
    """Key vault reference and secret settings for the module's secrets export."""
    keyVaultResourceId: Required[str]
    """The key vault name where to store the keys and connection strings generated by the modules."""
    accessKey1: str
    """The accessKey1 secret name to create."""
    accessKey2: str
    """The accessKey2 secret name to create."""
    connectionString1: str
    """The connectionString1 secret name to create."""
    connectionString2: str
    """The connectionString2 secret name to create."""


class StorageAccountParams(TypedDict, total=False):
    """"""
    name: Required[str]
    """Name of the Storage Account. Must be lower-case."""
    accessTier: Literal['Cool', 'Hot', 'Premium']
    """Required if the Storage Account kind is set to BlobStorage. The access tier is used for billing. The "Premium" access tier is the default value for premium block blobs storage account type and it cannot be changed for the premium block blobs storage account type."""
    enableHierarchicalNamespace: bool
    """If true, enables Hierarchical Namespace for the storage account. Required if enableSftp or enableNfsV3 is set to true."""
    allowBlobPublicAccess: bool
    """Indicates whether public access is enabled for all blobs or containers in the storage account. For security reasons, it is recommended to set it to false."""
    allowCrossTenantReplication: bool
    """Allow or disallow cross AAD tenant object replication."""
    allowedCopyScope: Literal['', 'AAD', 'PrivateLink']
    """Restrict copy to and from Storage Accounts within an AAD tenant or with Private Links to the same VNet."""
    allowSharedKeyAccess: bool
    """Indicates whether the storage account permits requests to be authorized with the account access key via Shared Key. If false, then all requests, including shared access signatures, must be authorized with Azure Active Directory (Azure AD). The default value is null, which is equivalent to true."""
    azureFilesIdentityBasedAuthentication: Dict[str, object]
    """Provides the identity based authentication settings for Azure Files."""
    blobServices: 'BlobServiceParams'
    """Blob service and containers to deploy."""
    customDomainName: str
    """Sets the custom domain name assigned to the storage account. Name is the CNAME source."""
    customDomainUseSubDomainName: bool
    """Indicates whether indirect CName validation is enabled. This should only be set on updates."""
    customerManagedKey: 'CustomerManagedKey'
    """The customer managed key definition."""
    defaultToOAuthAuthentication: bool
    """A boolean flag which indicates whether the default authentication is OAuth or not."""
    diagnosticSettings: List['DiagnosticSetting']
    """The diagnostic settings of the service."""
    dnsEndpointType: Literal['', 'AzureDnsZone', 'Standard']
    """Allows you to specify the type of endpoint. Set this to AzureDNSZone to create a large number of accounts in a single subscription, which creates accounts in an Azure DNS Zone and the endpoint URL will have an alphanumeric DNS Zone identifier."""
    enableNfsV3: bool
    """If true, enables NFS 3.0 support for the storage account. Requires enableHierarchicalNamespace to be true."""
    enableSftp: bool
    """If true, enables Secure File Transfer Protocol for the storage account. Requires enableHierarchicalNamespace to be true."""
    enableTelemetry: bool
    """Enable/Disable usage telemetry for module."""
    fileServices: 'FileService'
    """File service and shares to deploy."""
    isLocalUserEnabled: bool
    """Enables local users feature, if set to true."""
    keyType: Literal['Account', 'Service']
    """The keyType to use with Queue & Table services."""
    kind: Literal['BlobStorage', 'BlockBlobStorage', 'FileStorage', 'Storage', 'StorageV2']
    """Type of Storage Account to create."""
    largeFileSharesState: Literal['Disabled', 'Enabled']
    """Allow large file shares if sets to 'Enabled'. It cannot be disabled once it is enabled. Only supported on locally redundant and zone redundant file shares. It cannot be set on FileStorage storage accounts (storage accounts for premium file shares)."""
    localUsers: List['LocalUser']
    """Local users to deploy for SFTP authentication."""
    location: str
    """Location for all resources."""
    lock: 'Lock'
    """The lock settings of the service."""
    managedIdentities: 'ManagedIdentity'
    """The managed identity definition for this resource."""
    managementPolicyRules: List[object]
    """The Storage Account ManagementPolicies Rules."""
    minimumTlsVersion: Literal['TLS1_2', 'TLS1_3']
    """Set the minimum TLS version on request to storage. The TLS versions 1.0 and 1.1 are deprecated and not supported anymore."""
    networkAcls: 'NetworkAcl'
    """Networks ACLs, this value contains IPs to whitelist and/or Subnet information. If in use, bypass needs to be supplied. For security reasons, it is recommended to set the DefaultAction Deny."""
    privateEndpoints: List['PrivateEndpoint']
    """Configuration details for private endpoints. For security reasons, it is recommended to use private endpoints whenever possible."""
    publicNetworkAccess: Literal['', 'Disabled', 'Enabled']
    """Whether or not public network access is allowed for this resource. For security reasons it should be disabled. If not specified, it will be disabled by default if private endpoints are set and networkAcls are not set."""
    queueServices: 'QueueService'
    """Queue service and queues to create."""
    requireInfrastructureEncryption: bool
    """A Boolean indicating whether or not the service applies a secondary layer of encryption with platform managed keys for data at rest. For security reasons, it is recommended to set it to true."""
    roleAssignments: List['RoleAssignment']
    """Array of role assignments to create."""
    sasExpirationPeriod: str
    """The SAS expiration period. DD.HH:MM:SS."""
    secretsExportConfiguration: 'SecretsExportConfiguration'
    """Key vault reference and secret settings for the module's secrets export."""
    skuName: Literal['Premium_LRS', 'Premium_ZRS', 'Standard_GRS', 'Standard_GZRS', 'Standard_LRS', 'Standard_RAGRS', 'Standard_RAGZRS', 'Standard_ZRS']
    """Storage Account Sku Name."""
    supportsHttpsTrafficOnly: bool
    """Allows HTTPS traffic only to storage service if sets to true."""
    tableServices: 'TableService'
    """Table service and tables to create."""
    tags: Dict[str, object]
    """Tags of the resource."""


class StorageAccountKwargs(TypedDict, total=False):
    """"""
    access_tier: Literal['Cool', 'Hot', 'Premium']
    """Required if the Storage Account kind is set to BlobStorage. The access tier is used for billing. The "Premium" access tier is the default value for premium block blobs storage account type and it cannot be changed for the premium block blobs storage account type."""
    enable_hierarchical_namespace: bool
    """If true, enables Hierarchical Namespace for the storage account. Required if enableSftp or enableNfsV3 is set to true."""
    allow_blob_public_access: bool
    """Indicates whether public access is enabled for all blobs or containers in the storage account. For security reasons, it is recommended to set it to false."""
    allow_cross_tenant_replication: bool
    """Allow or disallow cross AAD tenant object replication."""
    allowed_copy_scope: Literal['', 'AAD', 'PrivateLink']
    """Restrict copy to and from Storage Accounts within an AAD tenant or with Private Links to the same VNet."""
    allow_shared_key_access: bool
    """Indicates whether the storage account permits requests to be authorized with the account access key via Shared Key. If false, then all requests, including shared access signatures, must be authorized with Azure Active Directory (Azure AD). The default value is null, which is equivalent to true."""
    azure_files_identity_based_authentication: Dict[str, object]
    """Provides the identity based authentication settings for Azure Files."""
    custom_domain_name: str
    """Sets the custom domain name assigned to the storage account. Name is the CNAME source."""
    custom_domain_use_subdomain_name: bool
    """Indicates whether indirect CName validation is enabled. This should only be set on updates."""
    customer_managed_key: 'CustomerManagedKey'
    """The customer managed key definition."""
    default_to_oauth_authentication: bool
    """A boolean flag which indicates whether the default authentication is OAuth or not."""
    diagnostic_settings: List['DiagnosticSetting']
    """The diagnostic settings of the service."""
    dns_endpoint_type: Literal['', 'AzureDnsZone', 'Standard']
    """Allows you to specify the type of endpoint. Set this to AzureDNSZone to create a large number of accounts in a single subscription, which creates accounts in an Azure DNS Zone and the endpoint URL will have an alphanumeric DNS Zone identifier."""
    enable_nfs_v3: bool
    """If true, enables NFS 3.0 support for the storage account. Requires enableHierarchicalNamespace to be true."""
    enable_sftp: bool
    """If true, enables Secure File Transfer Protocol for the storage account. Requires enableHierarchicalNamespace to be true."""
    enable_telemetry: bool
    """Enable/Disable usage telemetry for module."""
    is_local_user_enabled: bool
    """Enables local users feature, if set to true."""
    key_type: Literal['Account', 'Service']
    """The keyType to use with Queue & Table services."""
    kind: Literal['BlobStorage', 'BlockBlobStorage', 'FileStorage', 'Storage', 'StorageV2']
    """Type of Storage Account to create."""
    large_file_shares_state: Literal['Disabled', 'Enabled']
    """Allow large file shares if sets to 'Enabled'. It cannot be disabled once it is enabled. Only supported on locally redundant and zone redundant file shares. It cannot be set on FileStorage storage accounts (storage accounts for premium file shares)."""
    location: str
    """Location for all resources."""
    lock: 'Lock'
    """The lock settings of the service."""
    managed_identities: 'ManagedIdentity'
    """The managed identity definition for this resource."""
    management_policy_rules: List[object]
    """The Storage Account ManagementPolicies Rules."""
    minimum_tls_version: Literal['TLS1_2', 'TLS1_3']
    """Set the minimum TLS version on request to storage. The TLS versions 1.0 and 1.1 are deprecated and not supported anymore."""
    network_acls: 'NetworkAcl'
    """Networks ACLs, this value contains IPs to whitelist and/or Subnet information. If in use, bypass needs to be supplied. For security reasons, it is recommended to set the DefaultAction Deny."""
    private_endpoints: List['PrivateEndpoint']
    """Configuration details for private endpoints. For security reasons, it is recommended to use private endpoints whenever possible."""
    public_network_access: Literal['', 'Disabled', 'Enabled']
    """Whether or not public network access is allowed for this resource. For security reasons it should be disabled. If not specified, it will be disabled by default if private endpoints are set and networkAcls are not set."""
    require_infrastructure_encryption: bool
    """A Boolean indicating whether or not the service applies a secondary layer of encryption with platform managed keys for data at rest. For security reasons, it is recommended to set it to true."""
    role_assignments: List['RoleAssignment']
    """Array of role assignments to create."""
    sas_expiration_period: str
    """The SAS expiration period. DD.HH:MM:SS."""
    secrets_export_configuration: 'SecretsExportConfiguration'
    """Key vault reference and secret settings for the module's secrets export."""
    sku_name: Literal['Premium_LRS', 'Premium_ZRS', 'Standard_GRS', 'Standard_GZRS', 'Standard_LRS', 'Standard_RAGRS', 'Standard_RAGZRS', 'Standard_ZRS']
    """Storage Account Sku Name."""
    supports_https_traffic_only: bool
    """Allows HTTPS traffic only to storage service if sets to true."""
    tags: Dict[str, object]
    """Tags of the resource."""
