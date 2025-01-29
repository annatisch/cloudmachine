from typing import TYPE_CHECKING, Callable, Dict, Literal, Self, Unpack, overload, Optional, Any, Type, TypeVar

from ...._bicep.expressions import ModuleSymbol, Output
from ...._resource import Resource, _ClientResource
from .._resource import _DEFAULT_STORAGE_ACCOUNT


if TYPE_CHECKING:
    from .. import StorageAccountParams
    from . import TableServiceParams, TableStorageKwargs
    from azure.data.tables import TableServiceClient
    from azure.data.tables.aio import TableServiceClient as AsyncTableServiceClient


_DEFAULT_TABLE_STORAGE: 'TableServiceParams' = {
    'tables': []
}


ClientType = TypeVar("ClientType")

class TableStorage(_ClientResource):
    resource: Literal["Microsoft.Storage/storageAccounts/tableServices"] = "Microsoft.Storage/storageAccounts/tableServices"
    module: Literal["br/public:avm/res/storage/storage-account:0.14.0"] = "br/public:avm/res/storage/storage-account:0.14.0"
    identifier: Literal["storage:tables"] = "storage:tables"
    defaults: 'StorageAccountParams' = _DEFAULT_STORAGE_ACCOUNT
    default_services: 'TableServiceParams' = _DEFAULT_TABLE_STORAGE 
    properties: 'StorageAccountParams'

    def __init__(
            self,
            properties: Optional['TableServiceParams'] = None,
            storage_name: Optional[str] = None,
            *,
            role_assignments=['Storage Table Data Contributor'],
            **kwargs: Unpack['TableStorageKwargs']
    ) -> None:
        storage_params: 'StorageAccountParams' = {}
        if storage_name:
            storage_params['name'] = storage_name
        table_service_params: 'TableServiceParams' = properties or {}
        if 'tables' in kwargs:
            table_service_params['tables'] = kwargs.pop('tables')
        if 'diagnostic_settings' in kwargs:
            table_service_params['diagnosticSettings'] = kwargs.pop('diagnostic_settings')

        storage_params['tableServices'] = table_service_params
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
            service_prefix=["tables", "storage"],
            **kwargs
        )
        self._supports_managed_identity = True

    def _merge_params(
            self,
            params: 'StorageAccountParams',
            *,
            symbol: ModuleSymbol,
            attrname: Optional[str] = None,
            **kwargs
        ) -> Dict[str, Output]:
        table_services = params.pop("tableServices", dict(self.default_services))
        table_services.update(self.properties["tableServices"])
        outputs = super()._merge_params(params, symbol=symbol, attrname=attrname, **kwargs)
        params['tableServices'] = table_services
        suffix = attrname or self._suffix
        outputs[f"AZURE_TABLES_ENDPOINT_{suffix.upper()}"] = Output("outputs.serviceEndpoints.table", symbol)
        return outputs

    @overload
    def __call__(
            self,
            cls: Callable[..., ClientType],
            /,
            *,
            transport: Any = None,
            options: Optional[Dict[str, Any]] = None,
    ) -> ClientType:
        ...
    @overload
    def __call__(self, *, transport: Any = None, options: Optional[Dict[str, Any]] = None) -> 'TableServiceClient':
        ...
    @overload
    def __call__(self, cls: Type[Resource], /) -> Self:
        ...
    def __call__(self, cls=None, /, *, transport=None, options=None):
        options = options or {}
        if transport:
            options['transport'] = transport
        try:
            # First we check if it's a Resource type or whether it has 'from_resource' constructor
            return super()(self, cls, options=options)
        except TypeError:
            pass
        kwargs = {}
        try:
            endpoint = self.endpoint()
            kwargs['credential'] = self.credential()
        except RuntimeError as e:
            raise RuntimeError(f"Unable to build client for storage container: {e}.") from e
        try:
            kwargs['api_version'] = self.api_version()
        except RuntimeError:
            pass
        try:
            kwargs['audience'] = self.audience()
        except RuntimeError:
            pass
        kwargs.update(self.client_options())
        kwargs.update(options)
        if cls and cls.__name__ != 'TableServiceClient':
            client = cls(endpoint, **kwargs)
        else:
            from azure.data.tables import TableServiceClient
            client = TableServiceClient(
                endpoint,
                **kwargs
            )
        client.__resource_settings__ = self
        return client
