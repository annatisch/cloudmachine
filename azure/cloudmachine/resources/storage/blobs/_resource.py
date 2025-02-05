from typing import TYPE_CHECKING, Callable, Dict, Literal, Self, Union, Unpack, overload, Optional, Any, Type, TypeVar

from ....resources.resourcegroup._resource import ResourceGroup
from ...._bicep.expressions import ModuleSymbol, Output, ResourceGroupSymbol, ResourceSymbol
from ...._resource import Resource, _ClientResource
from .._resource import _DEFAULT_STORAGE_ACCOUNT, StorageAccount

if TYPE_CHECKING:
    from .. import StorageAccountParams
    from . import BlobServiceParams, BlobStorageKwargs


_DEFAULT_BLOB_STORAGE: 'BlobServiceParams' = {
    'containers': []
}

ClientType = TypeVar("ClientType")
 
 
class BlobStorage(_ClientResource):
    identifier: Literal["storage:blobs"] = "storage:blobs"
    module: Literal["br/public:avm/res/storage/storage-account"] = "br/public:avm/res/storage/storage-account"
    DEFAULTS: 'StorageAccountParams' = _DEFAULT_STORAGE_ACCOUNT
    DEFAULT_SERVICES: 'BlobServiceParams' = _DEFAULT_BLOB_STORAGE
    resource: Literal["Microsoft.Storage/storageAccounts/blobServices"]
    properties: 'StorageAccountParams'

    def __init__(
            self,
            properties: Optional['BlobServiceParams'] = None,
            /,
            storage_name: Optional[str] = None,
            *,
            role_assignments = ['Storage Blob Data Contributor'],
            **kwargs: Unpack['BlobStorageKwargs']
    ) -> None:
        storage_params: 'StorageAccountParams' = {}
        if storage_name:
            storage_params['name'] = storage_name
        blob_service_params: 'BlobServiceParams' = properties or {}
        if 'automatic_snapshot_policy_enabled' in kwargs:
            blob_service_params['automaticSnapshotPolicyEnabled'] = kwargs.pop('automatic_snapshot_policy_enabled')
        if 'change_feed_enabled' in kwargs:
            blob_service_params['changeFeedEnabled'] = kwargs.pop('change_feed_enabled')
        if 'change_feed_retention_in_days' in kwargs:
            blob_service_params['changeFeedRetentionInDays'] = kwargs.pop('change_feed_retention_in_days')
        if 'container_delete_retention_policy_allow_permanent_delete' in kwargs:
            blob_service_params['containerDeleteRetentionPolicyAllowPermanentDelete'] = kwargs.pop('container_delete_retention_policy_allow_permanent_delete')
        if 'container_delete_retention_policy_days' in kwargs:
            blob_service_params['containerDeleteRetentionPolicyDays'] = kwargs.pop('container_delete_retention_policy_days')
        if 'container_delete_retention_policy_enabled' in kwargs:
            blob_service_params['containerDeleteRetentionPolicyEnabled'] = kwargs.pop('container_delete_retention_policy_enabled')
        if 'containers' in kwargs:
            blob_service_params['containers'] = kwargs.pop('containers')
        if 'cors_rules' in kwargs:
            blob_service_params['corsRules'] = kwargs.pop('cors_rules')
        if 'default_service_version' in kwargs:
            blob_service_params['defaultServiceVersion'] = kwargs.pop('default_service_version')
        if 'delete_retention_policy_allow_permanent_delete' in kwargs:
            blob_service_params['deleteRetentionPolicyAllowPermanentDelete'] = kwargs.pop('delete_retention_policy_allow_permanent_delete')
        if 'delete_retention_policy_days' in kwargs:
            blob_service_params['deleteRetentionPolicyDays'] = kwargs.pop('delete_retention_policy_days')
        if 'delete_retention_policy_enabled' in kwargs:
            blob_service_params['deleteRetentionPolicyEnabled'] = kwargs.pop('delete_retention_policy_enabled')
        if 'diagnostic_settings' in kwargs:
            blob_service_params['diagnosticSettings'] = kwargs.pop('diagnostic_settings')
        if 'is_versioning_enabled' in kwargs:
            blob_service_params['isVersioningEnabled'] = kwargs.pop('is_versioning_enabled')
        if 'last_access_time_tracking_policy_enabled' in kwargs:
            blob_service_params['lastAccessTimeTrackingPolicyEnabled'] = kwargs.pop('last_access_time_tracking_policy_enabled')
        if 'restore_policy_days' in kwargs:
            blob_service_params['restorePolicyDays'] = kwargs.pop('restore_policy_days')
        if 'restore_policy_enabled' in kwargs:
            blob_service_params['restorePolicyEnabled'] = kwargs.pop('restore_policy_enabled')
        storage_params['blobServices'] = blob_service_params
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
        if role_assignments:
            storage_params['roleAssignments'] = role_assignments
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
            service_prefix=["blobs", "storage"],
            **kwargs
        )
        self._supports_managed_identity = True

    @property
    def resource(self) -> str:
        if self._resource:
            return self._resource
        from . import MODULE_RESOURCE
        return MODULE_RESOURCE

    @property
    def version(self) -> str:
        if self._version:
            return self._version
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
            resource_group: Optional[str] = None,
            subscription: Optional[str] = None
    ) -> Self:
        if resource_id:
            return super().reference(resource_id)
        from . import MODULE_RESOURCE, MODULE_VERSION
        resource = f"{MODULE_RESOURCE}@{MODULE_VERSION}"

        parent = StorageAccount.reference(
            name=name,
            resource_group=resource_group,
            subscription=subscription
        )
        existing = super().reference(resource=resource, name='default', parent=parent)
        return existing

    def _build_endpoint(self) -> str:
        return f"https://{self.name()}.blob.core.windows.net/"

    def _outputs(
            self,
             *,
             symbol: ResourceSymbol,
             attrname: Optional[str],
             resource_group: ResourceGroupSymbol,
             parent: Optional[ResourceSymbol] = None,
             **kwargs
    ) -> Dict[str, Output]:
        outputs = super()._outputs(symbol=symbol, attrname=attrname, resource_group=resource_group)
        suffix = self._get_suffix()
        if parent:
            outputs[f"AZURE_BLOBS_ENDPOINT{suffix}"] = Output("properties.primaryEndpoints.blob", parent)
        else:
            outputs[f"AZURE_BLOBS_ENDPOINT{suffix}"] = Output("outputs.serviceEndpoints.blob", symbol)
        return outputs

    def _merge_params(
            self,
            params: 'StorageAccountParams',
            *,
            symbol: ModuleSymbol,
            attrname: Optional[str] = None,
            **kwargs
        ) -> Dict[str, Any]:
        blob_services = params.pop("blobServices", dict(self.DEFAULT_SERVICES))
        blob_services.update(self.properties["blobServices"])
        output_config = super()._merge_params(params, symbol=symbol, attrname=attrname, **kwargs)
        params['blobServices'] = blob_services
        return output_config


class DatalakeStorage(BlobStorage):
    identifier: Literal["storage:datalake"] = "storage:datalake"

    def __init__(
            self,
            properties: Optional['BlobServiceParams'] = None,
            storage_name: Optional[str] = None,
            *,
            role_assignments = ['Storage Blob Data Contributor'],
            **kwargs: Unpack['BlobStorageKwargs']
    ) -> None:
        super().__init__(
            properties=properties,
            storage_name=storage_name,
            enable_hierarchical_namespace=True,
            role_assignments=role_assignments,
            **kwargs
        )

    def _build_endpoint(self) -> str:
        raise NotImplementedError()
