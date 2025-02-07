from typing import TYPE_CHECKING, Callable, Dict, Literal, Self, Union, Unpack, overload, Optional, Any, Type, TypeVar

from azure.cloudmachine.resources.resourcegroup._resource import ResourceGroup

from ...._bicep.expressions import ModuleSymbol, Output, ResourceGroupSymbol, ResourceSymbol
from ...._resource import Resource, _ClientResource
from .._resource import _DEFAULT_STORAGE_ACCOUNT, StorageAccount

if TYPE_CHECKING:
    from .. import StorageAccountParams
    from . import FileServiceParams, FileStorageKwargs
    from azure.storage.fileshare import ShareServiceClient


_DEFAULT_FILE_STORAGE: 'FileServiceParams' = {
    'shares': []
}

ClientType = TypeVar("ClientType")


class FileShareStorage(_ClientResource):
    identifier: Literal["storage:files"] = "storage:files"
    module: Literal["br/public:avm/res/storage/storage-account"] = "br/public:avm/res/storage/storage-account"
    DEFAULTS: 'StorageAccountParams' = _DEFAULT_STORAGE_ACCOUNT
    DEFAULT_SERVICES: 'FileServiceParams' = _DEFAULT_FILE_STORAGE
    resource: Literal["Microsoft.Storage/storageAccounts/fileServices"]
    properties: 'StorageAccountParams'

    def __init__(
            self,
            properties: Optional['FileServiceParams'] = None,
            storage_name: Optional[str] = None,
            *,
            role_assignments = ['Storage File Data Privileged Contributor'],
            **kwargs: Unpack['FileStorageKwargs']
    ) -> None:
        storage_params: 'StorageAccountParams' = {}
        if storage_name:
            storage_params['name'] = storage_name
        file_service_params: 'FileServiceParams' = properties or {}
        if 'shares' in kwargs:
            file_service_params['shares'] = kwargs.pop('shares')
        if 'diagnostic_settings' in kwargs:
            file_service_params['diagnosticSettings'] = kwargs.pop('diagnostic_settings')
        if 'protocol_settings' in kwargs:
            file_service_params['protocolSettings'] = kwargs.pop('protocol_settings')
        if 'share_delete_retention_policy' in kwargs:
            file_service_params['shareDeleteRetentionPolicy'] = kwargs.pop('share_delete_retention_policy')
        storage_params['fileServices'] = file_service_params
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
            service_prefix=["files", "storage"],
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
        return f"https://{self.name()}.file.core.windows.net/"

    def _outputs(
            self,
            *,
            symbol: ResourceSymbol,
            attrname: Optional[str],
            resource_group: ResourceGroupSymbol,
            parent: Optional[ResourceSymbol] = None,
            **kwargs,
    ) -> Dict[str, Output]:
        outputs = super()._outputs(symbol=symbol, attrname=attrname, resource_group=resource_group)
        suffix = self._get_suffix()
        if self._existing:
            outputs[f"AZURE_FILES_ENDPOINT{suffix}"] = Output("properties.primaryEndpoints.file", parent)
        else:
            outputs[f"AZURE_FILES_ENDPOINT{suffix}"] = Output("outputs.serviceEndpoints.file", symbol)
        return outputs

    def _merge_params(
            self,
            params: 'StorageAccountParams',
            *,
            symbol: ModuleSymbol,
            attrname: Optional[str] = None,
            **kwargs
        ) -> Dict[str, Any]:
        blob_services = params.pop("fileServices", dict(self.DEFAULT_SERVICES))
        blob_services.update(self.properties["fileServices"])
        output_config = super()._merge_params(params, symbol=symbol, attrname=attrname, **kwargs)
        params['fileServices'] = blob_services
        return output_config
