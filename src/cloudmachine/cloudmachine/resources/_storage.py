# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import functools
from typing import IO, Any, ClassVar, List, Mapping, Optional, Dict, Literal, Set, overload
from dataclasses import InitVar, dataclass, field

from ._resource import (
    _serialize_resource,
    Resource,
    LocatedResource,
    ResourceGroup,
    dataclass_model,
    generate_symbol,
    _UNSET
)


@dataclass_model
class Sku:
    name: Literal['Premium_LRS', 'Premium_ZRS', 'Standard_GRS', 'Standard_GZRS', 'Standard_LRS', 'Standard_RAGRS', 'Standard_RAGZRS', 'Standard_ZRS'] = field(metadata={'rest': 'name'})


@dataclass_model
class ExtendedLocation:
    name: str = field(metadata={'rest': 'name'})
    type: str = field(default='EdgeZone', metadata={'rest': 'type'})


@dataclass_model
class Identity:
    type: Literal['None', 'SystemAssigned', 'SystemAssigned,UserAssigned','UserAssigned'] = field(metadata={'rest': 'type'})
    user_assigned_identities: Optional[Dict[str, str]] = field(default=_UNSET, metadata={'rest': 'userAssignedIdentities'})


@dataclass_model
class ActiveDirectoryProperties:
    domain_guid: str = field(metadata={'rest': 'domainGuid'})
    domain_name: str = field(metadata={'rest': 'domainName'})
    account_type: Literal['Computer', 'User'] = field(metadata={'rest': 'accountType'})
    azure_storage_sid: Optional[str] = field(default=_UNSET, metadata={'rest': 'azureStorageSid'})
    domain_sid: Optional[str] = field(default=_UNSET, metadata={'rest': 'domainSid'})
    forest_name: Optional[str] = field(default=_UNSET, metadata={'rest': 'forestName'})
    net_bios_domain_name: Optional[str] = field(default=_UNSET, metadata={'rest': 'netBiosDomainName'})
    sam_account_name: Optional[str] = field(default=_UNSET, metadata={'rest': 'samAccountName'})


@dataclass_model
class AzureFilesIdentityBasedAuthentication:
    active_directory_properties: Optional[ActiveDirectoryProperties] = field(default=_UNSET, metadata={'rest': 'activeDirectoryProperties'})
    default_share_permission: Optional[Literal['StorageFileDataSmbShareContributor', 'StorageFileDataSmbShareElevatedContributor', 'StorageFileDataSmbShareReader']] = field(default=_UNSET, metadata={'rest': 'defaultSharePermission'})
    directory_service_options: Literal['AADKERB', 'AD', 'None'] = field(metadata={'rest': 'directoryServiceOptions'})


@dataclass_model
class CustomDomain:
    name: str = field(metadata={'rest': 'name'})
    use_sub_domain_name: Optional[bool] = field(default=_UNSET, metadata={'rest': 'useSubDomainName'})


@dataclass_model
class EncryptionIdentity:
    federated_identity_client_id: Optional[str] = field(default=_UNSET, metadata={'rest': 'federatedIdentityClientId'})
    user_assigned_identity: Optional[str] = field(default=_UNSET, metadata={'rest': 'userAssignedIdentity'})


@dataclass_model
class KeyVaultProperties:
    keyname: Optional[str] = field(default=_UNSET, metadata={'rest': 'keyname'})
    keyvaulturi: Optional[str] = field(default=_UNSET, metadata={'rest': 'keyvaulturi'})
    keyversion: Optional[str] = field(default=_UNSET, metadata={'rest': 'keyversion'})


@dataclass_model
class EncryptionService:
    enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'enabled'})
    key_type: Optional[Literal['Account', 'Service']] = field(default=_UNSET, metadata={'rest': 'keyType'})


@dataclass_model
class EncryptionServices:
    blob: Optional[EncryptionService] = field(default=_UNSET, metadata={'rest': 'blob'})
    file: Optional[EncryptionService] = field(default=_UNSET, metadata={'rest': 'file'})
    queue: Optional[EncryptionService] = field(default=_UNSET, metadata={'rest': 'queue'})
    table: Optional[EncryptionService] = field(default=_UNSET, metadata={'rest': 'table'})


@dataclass_model
class Encryption:
    identity: Optional[EncryptionIdentity] = field(default=_UNSET, metadata={'rest': 'identity'})
    key_source: Optional[Literal['Microsoft.Keyvault', 'Microsoft.Storage']] = field(default=_UNSET, metadata={'rest': 'keySource'})
    keyvault_properties: Optional[KeyVaultProperties] = field(default=_UNSET, metadata={'rest': 'keyvaultProperties'})
    require_infrastructure_encryption: Optional[bool] = field(default=_UNSET, metadata={'rest': 'requireInfrastructureEncryption'})
    services: Optional[EncryptionServices] = field(default=_UNSET, metadata={'rest': 'services'})


@dataclass_model
class AccountImmutabilityPolicyProperties:
    allow_protected_append_writes: Optional[bool] = field(default=_UNSET, metadata={'rest': 'allowProtectedAppendWrites'})
    immutability_period_since_creation_in_days: Optional[int] = field(default=_UNSET, metadata={'rest': 'immutabilityPeriodSinceCreationInDays'})
    state: Optional[Literal['Disabled', 'Locked', 'Unlocked']] = field(default=_UNSET, metadata={'rest': 'state'})


@dataclass_model
class ImmutableStorageAccount:
    enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'enabled'})
    immutability_policy: Optional[AccountImmutabilityPolicyProperties] = field(default=_UNSET, metadata={'rest': 'immutabilityPolicy'})


@dataclass_model
class KeyPolicy:
    key_expiration_period_in_days: int = field(metadata={'rest': 'keyExpirationPeriodInDays'})


@dataclass_model
class IPRule:
    action: Optional[Literal['Allow']] = field(default=_UNSET, metadata={'rest': 'action'})
    value: str = field(metadata={'rest': 'value'})


@dataclass_model
class ResourceAccessRule:
    resource_id: str = field(metadata={'rest': 'resourceId'})
    tenant_id: str = field(metadata={'rest': 'tenantId'})


@dataclass_model
class VirtualNetworkRule:
    action: Optional[Literal['Allow']] = field(default=_UNSET, metadata={'rest': 'action'})
    id: str = field(metadata={'rest': 'id'})


@dataclass_model
class NetworkRuleSet:
    bypass: Optional[Literal['AzureServices', 'Logging', 'Metrics', 'None']] = field(default=_UNSET, metadata={'rest': 'bypass'})
    default_action: Literal['Allow', 'Deny'] = field(metadata={'rest': 'defaultAction'})
    ip_rules: Optional[List[IPRule]] = field(default=_UNSET, metadata={'rest': 'ipRules'})
    resource_access_rules: Optional[List[ResourceAccessRule]] = field(default=_UNSET, metadata={'rest': 'resourceAccessRules'})
    virtual_network_rules: Optional[List[VirtualNetworkRule]] = field(default=_UNSET, metadata={'rest': 'virtualNetworkRules'})


@dataclass_model
class RoutingPreference:
    publish_internet_endpoints: Optional[bool] = field(default=_UNSET, metadata={'rest': 'publishInternetEndpoints'})
    publish_microsoft_endpoints: Optional[bool] = field(default=_UNSET, metadata={'rest': 'publishMicrosoftEndpoints'})
    routing_choice: Optional[Literal['InternetRouting', 'MicrosoftRouting']] = field(default=_UNSET, metadata={'rest': 'routingChoice'})


@dataclass_model
class SasPolicy:
    expiration_action: Literal["Log"] = field(metadata={'rest': 'expirationAction'})
    sas_expiration_period: str = field(metadata={'rest': 'sasExpirationPeriod'})


@dataclass_model
class Properties:
    access_tier: Optional[Literal["Hot", "Cool", "Premium"]] = field(default=_UNSET, metadata={'rest': 'accessTier'})
    allow_blob_public_acess: Optional[bool] = field(default=_UNSET, metadata={'rest': 'allowBlobPublicAccess'})
    allow_cross_tenant_replication: Optional[bool] = field(default=_UNSET, metadata={'rest': 'allowCrossTenantReplication'})
    allowed_copy_scope: Optional[Literal['AAD','PrivateLink']] = field(default=_UNSET, metadata={'rest': 'allowedCopyScope'})
    allow_shared_key_access: Optional[bool] = field(default=_UNSET, metadata={'rest': 'allowSharedKeyAccess'})
    custom_domain: Optional[CustomDomain] = field(default=_UNSET, metadata={'rest': 'customDomain'})
    default_to_oauth_authentication: Optional[bool] = field(default=_UNSET, metadata={'rest': 'defaultToOAuthAuthentication'})
    dns_endpoint_type: Optional[Literal['AzureDnsZone', 'Standard']] = field(default=_UNSET, metadata={'rest': 'dnsEndpointType'})
    immutable_storage_with_versioning: Optional[ImmutableStorageAccount] = field(default=_UNSET, metadata={'rest': 'immutableStorageWithVersioning'})
    is_hns_enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'isHnsEnabled'})
    is_local_user_enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'isLocalUserEnabled'})
    is_nfsv3_enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'isNfsV3Enabled'})
    is_sftp_enabled: Optional[bool] = field(default=_UNSET, metadata={'rest': 'isSftpEnabled'})
    key_policy: Optional[KeyPolicy] = field(default=_UNSET, metadata={'rest': 'keyPolicy'})
    large_file_shares_state: Optional[Literal['Disabled', 'Enabled']] = field(default=_UNSET, metadata={'rest': 'largeFileSharesState'})
    minimum_tls_version: Optional[Literal['TLS1_0', 'TLS1_1', 'TLS1_2']] = field(default=_UNSET, metadata={'rest': 'minimumTlsVersion'})
    network_acls: Optional[NetworkRuleSet] = field(default=_UNSET, metadata={'rest': 'networkAcls'})
    public_network_access: Optional[Literal['Disabled', 'Enabled']] = field(default=_UNSET, metadata={'rest': 'publicNetworkAccess'})
    routing_preference: Optional[RoutingPreference] = field(default=_UNSET, metadata={'rest': 'routingPreference'})
    sas_policy: Optional[SasPolicy] = field(default=_UNSET, metadata={'rest': 'sasPolicy'})
    supports_https_traffic_only: Optional[bool] = field(default=_UNSET, metadata={'rest': 'supportsHttpsTrafficOnly'})


@dataclass_model
class BlobServices(Resource):
    _resource: ClassVar[Literal['Microsoft.Storage/storageAccounts/blobServices']] = 'Microsoft.Storage/storageAccounts/blobServices'
    _version: ClassVar[str] = '2023-01-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("blobservice"), init=False, repr=False)
    name: Literal['default'] = field(default='default', init=False, metadata={'rest': 'name'})


@dataclass_model
class Container(Resource):
    _resource: ClassVar[Literal['Microsoft.Storage/storageAccounts/blobServices/containers']] = 'Microsoft.Storage/storageAccounts/blobServices/containers'
    _version: ClassVar[str] = '2023-01-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("container"), init=False, repr=False)


@dataclass_model
class StorageAccount(LocatedResource):
    sku: Sku = field(metadata={'rest': 'sku'})
    kind: str = field(metadata={'rest': 'kind'})
    extended_location : Optional[ExtendedLocation] = field(default=_UNSET, metadata={'rest': 'extendedLocation'})
    identity: Optional[Identity] = field(default=_UNSET, metadata={'rest': 'identity'})
    properties: Optional[Properties] = field(default=_UNSET, metadata={'rest': 'properties'})
    services: InitVar[Optional[BlobServices]] = None
    containers: InitVar[Optional[List[Container]]] = None
    _services: BlobServices = field(default_factory=BlobServices)
    _containers: List[Container] = field(init=False, default_factory=list)
    _resource: ClassVar[Literal['Microsoft.Storage/storageAccounts']] = 'Microsoft.Storage/storageAccounts'
    _version: ClassVar[str] = '2023-01-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("storage"), init=False, repr=False)

    def __post_init__(
            self,
            parent: Optional[Resource],
            scope: Optional[ResourceGroup],
            services: Optional[BlobServices],
            containers: Optional[List[Container]]
    ):
        if services:
            self._services = services
        self._services._parent = self
        if containers:
            for c in containers:
                c._parent = self._services
                self._containers.append(c)
        super().__post_init__(parent, scope)

    def write(self, bicep: IO[str]) -> None:
        _serialize_resource(bicep, self)
        self._services.write(bicep)
        for container in self._containers:
            container.write(bicep)
