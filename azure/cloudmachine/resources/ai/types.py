from typing import TYPE_CHECKING, TypedDict, Literal, List, Dict, Union
from typing_extensions import Required

from ..._bicep.expressions import Parameter

RESOURCE = "Microsoft.CognitiveServices/accounts"
VERSION = "2024-10-01"


# class ApiProperties(TypedDict, total=False):
#     aadClientId: Union[str, Parameter[str]]
#     """(Metrics Advisor Only) The Azure AD Client Id (Application Id)."""
#     aadTenantId: Union[str, Parameter[str]]
#     """(Metrics Advisor Only) The Azure AD Tenant Id."""
#     eventHubConnectionString: Union[str, Parameter[str]]
#     """(Personalization Only) The flag to enable statistics of Bing Search."""
#     qnaAzureSearchEndpointId: Union[str, Parameter[str]]
#     """(QnAMaker Only) The Azure Search endpoint id of QnAMaker."""
#     qnaAzureSearchEndpointKey: Union[str, Parameter[str]]
#     """(QnAMaker Only) The Azure Search endpoint key of QnAMaker."""
#     qnaRuntimeEndpoint: Union[str, Parameter[str]]
#     """(QnAMaker Only) The runtime endpoint of QnAMaker."""
#     statisticsEnabled: Union[bool, Parameter[bool]]
#     """(Bing Search Only) The flag to enable statistics of Bing Search."""
#     storageAccountConnectionString: Union[str, Parameter[str]]
#     """(Personalization Only) The storage account connection string."""
#     superUser: Union[str, Parameter[str]]
#     """(Metrics Advisor Only) The super user of Metrics Advisor."""
#     websiteName: Union[str, Parameter[str]]
#     """(Metrics Advisor Only) The website name of Metrics Advisor."""


# class AccountProperties(TypedDict, total=False):
#     allowedFqdnList: Union[List[Union[str, Parameter[str]]], Parameter[List[str]]]
#     """List of allowed FQDN."""
#     amlWorkspace: Union[UserOwnedAmlWorkspace, Parameter[UserOwnedAmlWorkspace]]
#     """The user owned AML workspace properties."""
#     apiProperties: Union[ApiProperties, Parameter[ApiProperties]]
#     """The api properties for special APIs."""
#     customSubDomainName: Union[str, Parameter[str]]
#     """Optional subdomain name used for token-based authentication."""
#     disableLocalAuth: Union[bool, Parameter[bool]]
#     """Allow only Azure AD authentication. Should be enabled for security reasons."""
#     dynamicThrottlingEnabled: Union[bool, Parameter[bool]]
#     """The flag to enable dynamic throttling."""
#     encryption: Union[Encryption, Parameter[Encryption]]
#     """The encryption properties for this resource."""
#     locations: Union[MultiRegionSettings, Parameter[MultiRegionSettings]]
#     """The multiregion settings of Cognitive Services account."""
#     migrationToken: Union[str, Parameter[str]]
#     """Resource migration token."""
#     networkAcls: Union[NetworkRuleSet, Parameter[NetworkRuleSet]]
#     """A collection of rules governing the accessibility from specific network locations."""
#     publicNetworkAccess: Union[Literal['Disabled', 'Enabled'], Parameter[str]]
#     """Whether or not public endpoint access is allowed for this account."""
#     raiMonitorConfig: Union[RaiMonitorConfig, Parameter[RaiMonitorConfig]]
#     """Cognitive Services Rai Monitor Config."""
#     restore: Union[bool, Parameter[bool]]
#     """Restore a soft-deleted cognitive service at deployment time. Will fail if no such soft-deleted resource exists."""
#     restrictOutboundNetworkAccess: Union[bool, Parameter[bool]]
#     """Restrict outbound network access."""
#     userOwnedStorage: Union[List[Union[UserOwnedStorage, Parameter[UserOwnedStorage]]], Parameter[List[UserOwnedStorage]]]
#     """The storage accounts for this resource."""

"""
Encryption
Name	Description	Value
keySource	Enumerates the possible value of keySource for Encryption	'Microsoft.CognitiveServices'
'Microsoft.KeyVault'
keyVaultProperties	Properties of KeyVault	KeyVaultProperties

Identity
Name	Description	Value
type	The identity type.	'None'
'SystemAssigned'
'SystemAssigned, UserAssigned'
'UserAssigned'
userAssignedIdentities	The list of user assigned identities associated with the resource. The user identity dictionary key references will be ARM resource ids in the form: '/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/{identityName}	IdentityUserAssignedIdentities

IdentityUserAssignedIdentities
Name	Description	Value

IpRule
Name	Description	Value
value	An IPv4 address range in CIDR notation, such as '124.56.78.91' (simple IP address) or '124.56.78.0/24' (all addresses that start with 124.56.78).	string (required)

KeyVaultProperties
Name	Description	Value
identityClientId		string
keyName	Name of the Key from KeyVault	string
keyVaultUri	Uri of KeyVault	string
keyVersion	Version of the Key from KeyVault	string


MultiRegionSettings
Name	Description	Value
regions		RegionSetting[]
routingMethod	Multiregion routing methods.	'Performance'
'Priority'
'Weighted'

NetworkRuleSet
Name	Description	Value
bypass	Setting for trusted services.	'AzureServices'
'None'
defaultAction	The default action when no rule from ipRules and from virtualNetworkRules match. This is only used after the bypass property has been evaluated.	'Allow'
'Deny'
ipRules	The list of IP address rules.	IpRule[]
virtualNetworkRules	The list of virtual network rules.	VirtualNetworkRule[]

RaiMonitorConfig
Name	Description	Value
adxStorageResourceId	The storage resource Id.	string
identityClientId	The identity client Id to access the storage.	string

RegionSetting
Name	Description	Value
customsubdomain	Maps the region to the regional custom subdomain.	string
name	Name of the region.	string
value	A value for priority or weighted routing methods.	int

Sku
Name	Description	Value
capacity	If the SKU supports scale out/in then the capacity integer should be included. If scale out/in is not possible for the resource this may be omitted.	int
family	If the service has different generations of hardware, for the same SKU, then that can be captured here.	string
name	The name of the SKU. Ex - P3. It is typically a letter+number code	string (required)
size	The SKU size. When the name field is the combination of tier and some other value, this would be the standalone code.	string
tier	This field is required to be implemented by the Resource Provider if the service has more than one tier, but is not required on a PUT.	'Basic'
'Enterprise'
'Free'
'Premium'
'Standard'

UserAssignedIdentity
Name	Description	Value

UserOwnedAmlWorkspace
Name	Description	Value
identityClientId	Identity Client id of a AML workspace resource.	string
resourceId	Full resource id of a AML workspace resource.	string

UserOwnedStorage
Name	Description	Value
identityClientId		string
resourceId	Full resource id of a Microsoft.Storage resource.	string

VirtualNetworkRule
Name	Description	Value
id	Full resource id of a vnet subnet, such as '/subscriptions/subid/resourceGroups/rg1/providers/Microsoft.Network/virtualNetworks/test-vnet/subnets/subnet1'.	string (required)
ignoreMissingVnetServiceEndpoint	Ignore missing vnet service endpoint or not.	bool
state	Gets the state of virtual network rule.
"""


class CognitiveServicesAccountResource(TypedDict, total=False):
    identity: 'Identity'
    """Identity for the resource."""
    kind: Union[Literal['AIServices', 'AnomalyDetector', 'CognitiveServices', 'ComputerVision', 'ContentModerator', 'ContentSafety', 'ConversationalLanguageUnderstanding', 'CustomVision.Prediction', 'CustomVision.Training', 'Face', 'FormRecognizer', 'HealthInsights', 'ImmersiveReader', 'Internal.AllInOne', 'LanguageAuthoring', 'LUIS', 'LUIS.Authoring', 'MetricsAdvisor', 'OpenAI', 'Personalizer', 'QnAMaker.v2', 'SpeechServices', 'TextAnalytics', 'TextTranslation'], Parameter[str]]
    """The Kind of the resource."""
    location: Union[str, Parameter[str]]
    """The geo-location where the resource lives."""
    name: Union[str, Parameter[str]]
    """The resource name."""
    properties:	'AccountProperties'
    """Properties of Cognitive Services account."""
    sku: 'Sku'
    """The resource model definition representing SKU"""
    tags: Union[Dict[str, Union[str, Parameter[str]]], Parameter[Dict[str, str]]]
    """Resource tags	Dictionary of tag names and values. See Tags in templates"""





























class Model(TypedDict, total=False):
    """Properties of Cognitive Services account deployment model."""
    format: Required[str]
    """The format of Cognitive Services account deployment model."""
    name: Required[str]
    """The name of Cognitive Services account deployment model."""
    version: Required[str]
    """The version of Cognitive Services account deployment model."""


class Sku(TypedDict, total=False):
    """The resource model definition representing SKU."""
    name: Required[str]
    """The name of the resource model definition representing SKU."""
    capacity: int
    """The capacity of the resource model definition representing SKU."""


class Deployment(TypedDict, total=False):
    """Array of deployments about cognitive service accounts to create."""
    model: Required['Model']
    """Properties of Cognitive Services account deployment model."""
    name: str
    """Specify the name of cognitive service account deployment."""
    raiPolicyName: str
    """The name of RAI policy."""
    sku: 'Sku'
    """The resource model definition representing SKU."""







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
    roleDefinitionIdOrName: Required[Union[str, Literal['Contributor', 'DNS Resolver Contributor', 'DNS Zone Contributor', 'Domain Services Contributor', 'Domain Services Reader', 'Network Contributor', 'Owner', 'Private DNS Zone Contributor', 'Reader', 'Role Based Access Control Administrator']]]
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




class RoleAssignment(TypedDict, total=False):
    """Array of role assignments to create."""
    principalId: Required[str]
    """The principal ID of the principal (user/group/identity) to assign the role to."""
    roleDefinitionIdOrName: Required[Union[str, Literal['Cognitive Services Contributor', 'Cognitive Services Custom Vision Contributor', 'Cognitive Services Custom Vision Deployment', 'Cognitive Services Custom Vision Labeler', 'Cognitive Services Custom Vision Reader', 'Cognitive Services Custom Vision Trainer', 'Cognitive Services Data Reader (Preview)', 'Cognitive Services Face Recognizer', 'Cognitive Services Immersive Reader User', 'Cognitive Services Language Owner', 'Cognitive Services Language Reader', 'Cognitive Services Language Writer', 'Cognitive Services LUIS Owner', 'Cognitive Services LUIS Reader', 'Cognitive Services LUIS Writer', 'Cognitive Services Metrics Advisor Administrator', 'Cognitive Services Metrics Advisor User', 'Cognitive Services OpenAI Contributor', 'Cognitive Services OpenAI User', 'Cognitive Services QnA Maker Editor', 'Cognitive Services QnA Maker Reader', 'Cognitive Services Speech Contributor', 'Cognitive Services Speech User', 'Cognitive Services User', 'Contributor', 'Owner', 'Reader', 'Role Based Access Control Administrator', 'User Access Administrator']]]
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



# class CognitiveServicesAccountResource(TypedDict, total=False):
#     """"""
#     kind: Required[Literal['AIServices', 'AnomalyDetector', 'CognitiveServices', 'ComputerVision', 'ContentModerator', 'ContentSafety', 'ConversationalLanguageUnderstanding', 'CustomVision.Prediction', 'CustomVision.Training', 'Face', 'FormRecognizer', 'HealthInsights', 'ImmersiveReader', 'Internal.AllInOne', 'LanguageAuthoring', 'LUIS', 'LUIS.Authoring', 'MetricsAdvisor', 'OpenAI', 'Personalizer', 'QnAMaker.v2', 'SpeechServices', 'TextAnalytics', 'TextTranslation']]
#     """Kind of the Cognitive Services account. Use 'Get-AzCognitiveServicesAccountSku' to determine a valid combinations of 'kind' and 'SKU' for your Azure region."""
#     name: Required[str]
#     """The name of Cognitive Services account."""
#     customSubDomainName: str
#     """Subdomain name used for token-based authentication. Required if 'networkAcls' or 'privateEndpoints' are set."""
#     allowedFqdnList: List[object]
#     """List of allowed FQDN."""
#     apiProperties: Dict[str, object]
#     """The API properties for special APIs."""
#     customerManagedKey: 'CustomerManagedKey'
#     """The customer managed key definition."""
#     deployments: List['Deployment']
#     """Array of deployments about cognitive service accounts to create."""
#     diagnosticSettings: List['DiagnosticSetting']
#     """The diagnostic settings of the service."""
#     disableLocalAuth: bool
#     """Allow only Azure AD authentication. Should be enabled for security reasons."""
#     dynamicThrottlingEnabled: bool
#     """The flag to enable dynamic throttling."""
#     enableTelemetry: bool
#     """Enable/Disable usage telemetry for module."""
#     location: str
#     """Location for all Resources."""
#     lock: 'Lock'
#     """The lock settings of the service."""
#     managedIdentities: 'ManagedIdentity'
#     """The managed identity definition for this resource."""
#     migrationToken: str
#     """Resource migration token."""
#     networkAcls: Dict[str, object]
#     """A collection of rules governing the accessibility from specific network locations."""
#     privateEndpoints: List['PrivateEndpoint']
#     """Configuration details for private endpoints. For security reasons, it is recommended to use private endpoints whenever possible."""
#     publicNetworkAccess: Literal['Disabled', 'Enabled']
#     """Whether or not public network access is allowed for this resource. For security reasons it should be disabled. If not specified, it will be disabled by default if private endpoints are set and networkAcls are not set."""
#     restore: bool
#     """Restore a soft-deleted cognitive service at deployment time. Will fail if no such soft-deleted resource exists."""
#     restrictOutboundNetworkAccess: bool
#     """Restrict outbound network access."""
#     roleAssignments: List['RoleAssignment']
#     """Array of role assignments to create."""
#     secretsExportConfiguration: 'SecretsExportConfiguration'
#     """Key vault reference and secret settings for the module's secrets export."""
#     sku: Literal['C2', 'C3', 'C4', 'F0', 'F1', 'S', 'S0', 'S1', 'S10', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7', 'S8', 'S9']
#     """SKU of the Cognitive Services account. Use 'Get-AzCognitiveServicesAccountSku' to determine a valid combinations of 'kind' and 'SKU' for your Azure region."""
#     tags: Dict[str, object]
#     """Tags of the resource."""
#     userOwnedStorage: List[object]
#     """The storage accounts for this resource."""
