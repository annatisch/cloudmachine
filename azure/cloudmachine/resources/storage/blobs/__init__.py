from typing import TYPE_CHECKING, TypedDict, Literal, List, Dict
from typing_extensions import Required


if TYPE_CHECKING:
    from .container.immutability_policy import ImmutabilityPolicy
    from .. import (
        CustomerManagedKey,
        ManagedIdentity,
        RoleAssignment,
        Lock,
        NetworkAcl,
        PrivateEndpoint,
        SecretsExportConfiguration
    )

MODULE = "br/public:avm/res/storage/storage-account"
MODULE_RESOURCE = "Microsoft.Storage/storageAccounts/blobServices"
MODULE_VERSION = "2022-09-01"
MODULE_TAG = "0.14.0"


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


class Container(TypedDict, total=False):
    """"""
    name: str
    """The name of the storage container to deploy."""
    defaultEncryptionScope: str
    """Default the container to use specified encryption scope for all writes."""
    denyEncryptionScopeOverride: bool
    """Block override of encryption scope from the container default."""
    enableNfsV3AllSquash: bool
    """Enable NFSv3 all squash on blob container."""
    enableNfsV3RootSquash: bool
    """Enable NFSv3 root squash on blob container."""
    immutabilityPolicyName: str
    """Name of the immutable policy."""
    immutabilityPolicyProperties: 'ImmutabilityPolicy'
    """Configure immutability policy."""
    immutableStorageWithVersioningEnabled: bool
    """This is an immutable property, when set to true it enables object level immutability at the container level. The property is immutable and can only be set to true at the container creation time. Existing containers must undergo a migration process."""
    metadata: Dict[str, object]
    """A name-value pair to associate with the container as metadata."""
    publicAccess: Literal['Blob', 'Container', 'None']
    """Specifies whether data in the container may be accessed publicly and the level of access."""
    roleAssignments: List['RoleAssignment']
    """Array of role assignments to create."""


class BlobServiceParams(TypedDict, total=False):
    """"""
    automaticSnapshotPolicyEnabled: bool
    """Automatic Snapshot is enabled if set to true."""
    changeFeedEnabled: bool
    """The blob service properties for change feed events. Indicates whether change feed event logging is enabled for the Blob service."""
    changeFeedRetentionInDays: int
    """Indicates whether change feed event logging is enabled for the Blob service. Indicates the duration of changeFeed retention in days. If left blank, it indicates an infinite retention of the change feed."""
    containerDeleteRetentionPolicyAllowPermanentDelete: bool
    """This property when set to true allows deletion of the soft deleted blob versions and snapshots. This property cannot be used with blob restore policy. This property only applies to blob service and does not apply to containers or file share."""
    containerDeleteRetentionPolicyDays: int
    """Indicates the number of days that the deleted item should be retained."""
    containerDeleteRetentionPolicyEnabled: bool
    """The blob service properties for container soft delete. Indicates whether DeleteRetentionPolicy is enabled."""
    containers: List['Container']
    """Blob containers to create."""
    corsRules: List[object]
    """Specifies CORS rules for the Blob service. You can include up to five CorsRule elements in the request. If no CorsRule elements are included in the request body, all CORS rules will be deleted, and CORS will be disabled for the Blob service."""
    defaultServiceVersion: str
    """Indicates the default version to use for requests to the Blob service if an incoming request's version is not specified. Possible values include version 2008-10-27 and all more recent versions."""
    deleteRetentionPolicyAllowPermanentDelete: bool
    """This property when set to true allows deletion of the soft deleted blob versions and snapshots. This property cannot be used with blob restore policy. This property only applies to blob service and does not apply to containers or file share."""
    deleteRetentionPolicyDays: int
    """Indicates the number of days that the deleted blob should be retained."""
    deleteRetentionPolicyEnabled: bool
    """The blob service properties for blob soft delete."""
    diagnosticSettings: List['DiagnosticSetting']
    """The diagnostic settings of the service."""
    isVersioningEnabled: bool
    """Use versioning to automatically maintain previous versions of your blobs."""
    lastAccessTimeTrackingPolicyEnabled: bool
    """The blob service property to configure last access time based tracking policy. When set to true last access time based tracking is enabled."""
    restorePolicyDays: int
    """How long this blob can be restored. It should be less than DeleteRetentionPolicy days."""
    restorePolicyEnabled: bool
    """The blob service properties for blob restore policy. If point-in-time restore is enabled, then versioning, change feed, and blob soft delete must also be enabled."""


class BlobStorageKwargs(TypedDict, total=False):
    """"""
    automatic_snapshot_policy_enabled: bool
    """Automatic Snapshot is enabled if set to true."""
    change_feed_enabled: bool
    """The blob service properties for change feed events. Indicates whether change feed event logging is enabled for the Blob service."""
    change_feed_retention_in_days: int
    """Indicates whether change feed event logging is enabled for the Blob service. Indicates the duration of changeFeed retention in days. If left blank, it indicates an infinite retention of the change feed."""
    container_delete_retention_policy_allow_permanent_delete: bool
    """This property when set to true allows deletion of the soft deleted blob versions and snapshots. This property cannot be used with blob restore policy. This property only applies to blob service and does not apply to containers or file share."""
    container_delete_retention_policy_days: int
    """Indicates the number of days that the deleted item should be retained."""
    container_delete_retention_policy_enabled: bool
    """The blob service properties for container soft delete. Indicates whether DeleteRetentionPolicy is enabled."""
    containers: List['Container']
    """Blob containers to create."""
    cors_rules: List[object]
    """Specifies CORS rules for the Blob service. You can include up to five CorsRule elements in the request. If no CorsRule elements are included in the request body, all CORS rules will be deleted, and CORS will be disabled for the Blob service."""
    default_service_version: str
    """Indicates the default version to use for requests to the Blob service if an incoming request's version is not specified. Possible values include version 2008-10-27 and all more recent versions."""
    delete_retention_policy_allow_permanent_delete: bool
    """This property when set to true allows deletion of the soft deleted blob versions and snapshots. This property cannot be used with blob restore policy. This property only applies to blob service and does not apply to containers or file share."""
    delete_retention_policy_days: int
    """Indicates the number of days that the deleted blob should be retained."""
    delete_retention_policy_enabled: bool
    """The blob service properties for blob soft delete."""
    is_versioning_enabled: bool
    """Use versioning to automatically maintain previous versions of your blobs."""
    last_access_time_tracking_policy_enabled: bool
    """The blob service property to configure last access time based tracking policy. When set to true last access time based tracking is enabled."""
    restore_policy_days: int
    """How long this blob can be restored. It should be less than DeleteRetentionPolicy days."""
    restore_policy_enabled: bool
    """The blob service properties for blob restore policy. If point-in-time restore is enabled, then versioning, change feed, and blob soft delete must also be enabled."""
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