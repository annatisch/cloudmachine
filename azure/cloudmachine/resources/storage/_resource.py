from typing import TYPE_CHECKING, Literal, Unpack, Optional

from ..._resource import Resource

if TYPE_CHECKING:
    from . import StorageAccountParams, StorageAccountKwargs


_DEFAULT_STORAGE_ACCOUNT: 'StorageAccountParams' = {
    "accessTier": "Hot",
    "allowBlobPublicAccess": False,
    "kind": "StorageV2",
    "skuName": "Standard_LRS",
}


class StorageAccount(Resource):
    identifier: Literal["storage"] = "storage"
    module: Literal["br/public:avm/res/storage/storage-account"] = "br/public:avm/res/storage/storage-account"
    defaults: 'StorageAccountParams' = _DEFAULT_STORAGE_ACCOUNT
    resource: Literal["Microsoft.Storage/storageAccounts"]
    properties: 'StorageAccountParams'

    def __init__(
            self,
            properties: Optional['StorageAccountParams'] = None,
            storage_name: Optional[str] = None,
            **kwargs: Unpack['StorageAccountKwargs']
    ) -> None:
        storage_params: 'StorageAccountParams' = properties or {}
        if storage_name:
            storage_params['name'] = storage_name
        if 'access_tier' in kwargs:
            storage_params['accessTier'] = kwargs.pop('access_tier')
        if 'enable_hierarchical_namespace' in kwargs:
            storage_params['enableHierarchicalNamespace'] = kwargs.pop('enable_hierarchical_namespace')
        if 'allow_blob_public_access' in kwargs:
            storage_params['allowBlobPublicAccess'] = kwargs.pop('allow_blob_public_access')
        if 'allow_cross_tenant_replication' in kwargs:
            storage_params['allowCrossTenantReplication'] = kwargs.pop('allow_cross_tenant_replication')
        if 'allowed_copy_scope' in kwargs:
            storage_params['allowedCopyScope'] = kwargs.pop('allowed_copy_scope')
        if 'allow_shared_key_access' in kwargs:
            storage_params['allowSharedKeyAccess'] = kwargs.pop('allow_shared_key_access')
        if 'custom_domain_name' in kwargs:
            storage_params['customDomainName'] = kwargs.pop('custom_domain_name')
        if 'custom_domain_use_subdomain_name' in kwargs:
            storage_params['customDomainUseSubDomainName'] = kwargs.pop('custom_domain_use_subdomain_name')
        if 'customer_managed_key' in kwargs:
            storage_params['customerManagedKey'] = kwargs.pop('customer_managed_key')
        if 'default_to_oauth_authentication' in kwargs:
            storage_params['defaultToOAuthAuthentication'] = kwargs.pop('default_to_oauth_authentication')
        if 'diagnostic_settings' in kwargs:
            storage_params['diagnosticSettings'] = kwargs.pop('diagnostic_settings')
        if 'dns_endpoint_type' in kwargs:
            storage_params['dnsEndpointType'] = kwargs.pop('dns_endpoint_type')
        if 'enable_nfs_v3' in kwargs:
            storage_params['enableNfsV3'] = kwargs.pop('enable_nfs_v3')
        if 'enable_sftp' in kwargs:
            storage_params['enableSftp'] = kwargs.pop('enable_sftp')
        if 'enable_telemetry' in kwargs:
            storage_params['enableTelemetry'] = kwargs.pop('enable_telemetry')
        if 'is_local_user_enabled' in kwargs:
            storage_params['isLocalUserEnabled'] = kwargs.pop('is_local_user_enabled')
        if 'key_type' in kwargs:
            storage_params['keyType'] = kwargs.pop('key_type')
        if 'kind' in kwargs:
            storage_params['kind'] = kwargs.pop('kind')
        if 'location' in kwargs:
            storage_params['location'] = kwargs.pop('location')
        if 'lock' in kwargs:
            storage_params['lock'] = kwargs.pop('lock')
        if 'managed_identities' in kwargs:
            storage_params['managedIdentities'] = kwargs.pop('managed_identities')
        if 'management_policy_rules' in kwargs:
            storage_params['managementPolicyRules'] = kwargs.pop('management_policy_rules')
        if 'minimum_tls_version' in kwargs:
            storage_params['minimumTlsVersion'] = kwargs.pop('minimum_tls_version')
        if 'network_acls' in kwargs:
            storage_params['networkAcls'] = kwargs.pop('network_acls')
        if 'private_endpoints' in kwargs:
            storage_params['privateEndpoints'] = kwargs.pop('private_endpoints')
        if 'public_network_access' in kwargs:
            storage_params['publicNetworkAccess'] = kwargs.pop('public_network_access')
        if 'require_infrastructure_encryption' in kwargs:
            storage_params['requireInfrastructureEncryption'] = kwargs.pop('require_infrastructure_encryption')
        if 'role_assignments' in kwargs:
            storage_params['roleAssignments'] = kwargs.pop('role_assignments')
        if 'sas_expiration_period' in kwargs:
            storage_params['sasExpirationPeriod'] = kwargs.pop('sas_expiration_period')
        if 'secrets_export_configuration' in kwargs:
            storage_params['secretsExportConfiguration'] = kwargs.pop('secrets_export_configuration')
        if 'sku_name' in kwargs:
            storage_params['skuName'] = kwargs.pop('sku_name')
        if 'supports_https_traffic_only' in kwargs:
            storage_params['supportsHttpsTrafficOnly'] = kwargs.pop('supports_https_traffic_only')
        if 'tags' in kwargs:
            storage_params['tags'] = kwargs.pop('tags')

        super().__init__(
            properties=storage_params,
            service_prefix=["storage"],
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
