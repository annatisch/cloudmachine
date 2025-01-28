from typing import TYPE_CHECKING, TypedDict, Literal, List, Dict, Union
from typing_extensions import Required


if TYPE_CHECKING:
    from .table import Table


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


class TableServiceParams(TypedDict, total=False):
    """"""
    diagnosticSettings: List['DiagnosticSetting']
    """The diagnostic settings of the service."""
    tables: List['Table']
    """tables to create."""



class TableStorageKwargs(TypedDict, total=False):
    """"""
    tables: List['Table']
    """tables to create."""
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
    enable_telemetry: bool
    """Enable/Disable usage telemetry for module."""
    is_local_user_enabled: bool
    """Enables local users feature, if set to true."""
    key_rype: Literal['Account', 'Service']
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