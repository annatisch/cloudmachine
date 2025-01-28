from typing import TYPE_CHECKING, Callable, Dict, List, Literal, Self, Unpack, overload, Optional, Any, Type, TypeVar

from ....._bicep.expressions import ModuleSymbol, Output, Parameter
from ....._setting import StoredPrioritizedSetting
from ....._resource import (
    Resource,
    _ClientResource,
    _convert_str_from_setting,
    _build_envs,
    _convert_to_str
)
from ..._resource import _DEFAULT_STORAGE_ACCOUNT
from .._resource import _DEFAULT_BLOB_STORAGE


if TYPE_CHECKING:
    from .. import BlobServiceParams
    from ... import StorageAccountParams
    from . import ContainerParams, ContainerKwargs
    from azure.storage.blob import ContainerClient
    from azure.storage.blob.aio import ContainerClient as AsyncContainerClient

_DEFAULT_CONTAINER: 'ContainerParams' = {}

ClientType = TypeVar("ClientType")


class BlobContainer(_ClientResource):
    resource: Literal["Microsoft.Storage/storageAccounts/blobServices/containers"] = "Microsoft.Storage/storageAccounts/blobServices/containers"
    module: Literal["br/public:avm/res/storage/storage-account:0.14.0"] = "br/public:avm/res/storage/storage-account:0.14.0"
    identifier: Literal["storage:blobs:container"] = "storage:blobs:container"
    defaults: 'StorageAccountParams' = _DEFAULT_STORAGE_ACCOUNT
    default_services: 'BlobServiceParams' = _DEFAULT_BLOB_STORAGE
    default_container: 'ContainerParams' = _DEFAULT_CONTAINER
    properties: 'StorageAccountParams'

    def __init__(
            self,
            properties: Optional['ContainerParams'] = None,
            storage_name: Optional[str] = None,
            container_name: Optional[str] = None,
            *,
            role_assignments = ['Storage Blob Data Contributor'],
            **kwargs: Unpack['ContainerKwargs']
    ) -> None:
        storage_params: 'StorageAccountParams' = {}
        if storage_name:
            storage_params['name'] = storage_name
        blob_service_params: 'BlobServiceParams' = {}
        container_params: 'ContainerParams' = properties or {}
        if container_name:
            container_params['name'] = container_name
        if 'default_encryption_scope' in kwargs:
            container_params['defaultEncryptionScope'] = kwargs.pop('default_encryption_scope')
        if 'deny_encryption_scope_override' in kwargs:
            container_params['denyEncryptionScopeOverride'] = kwargs.pop('deny_encryption_scope_override')
        if 'enable_nfsv3_all_squash' in kwargs:
            container_params['enableNfsV3AllSquash'] = kwargs.pop('enable_nfsv3_all_squash')
        if 'enable_nfsv3_root_squash' in kwargs:
            container_params['enableNfsV3RootSquash'] = kwargs.pop('enable_nfsv3_root_squash')
        if 'immutability_policy_name' in kwargs:
            container_params['immutabilityPolicyName'] = kwargs.pop('immutability_policy_name')
        if 'immutability_policy_properties' in kwargs:
            container_params['immutabilityPolicyProperties'] = kwargs.pop('immutability_policy_properties')
        if 'immutable_storage_with_versioning_enabled' in kwargs:
            container_params['immutableStorageWithVersioningEnabled'] = kwargs.pop('immutable_storage_with_versioning_enabled')
        if 'metadata' in kwargs:
            container_params['metadata'] = kwargs.pop('metadata')
        if 'public_access' in kwargs:
            container_params['publicAccess'] = kwargs.pop('public_access')
        if role_assignments:
            container_params['roleAssignments'] = role_assignments

        blob_service_params["containers"] = [container_params]
        storage_params["blobServices"] = blob_service_params
        super().__init__(
            properties=storage_params,
            service_prefix=["blobs", "storage"],
            **kwargs
        )
        self.container_name = StoredPrioritizedSetting(
            name='container_name',
            env_vars=_build_envs(self._prefixes, ['CONTAINER_NAME']),
            convert=_convert_str_from_setting,
            to_str=_convert_to_str,
        )
        self.container_endpoint = StoredPrioritizedSetting(
            name='container_name',
            env_vars=_build_envs(self._prefixes, ['CONTAINER_ENDPOINT']),
            convert=_convert_str_from_setting,
            to_str=_convert_to_str,
        )
        self._settings['container_name'] = self.container_name
        self._settings['container_endpoint'] = self.container_endpoint

    def _merge_containers(
            self,
            containers: List['ContainerParams'],
            new_container: 'ContainerParams',
            default_name: Parameter
    ) -> List['ContainerParams']:
        container_name = new_container.get('name') or default_name
        existing = False
        for container in containers:
            if container['name'] == container_name:
                existing = True
                container.update(new_container)
        if not existing:
            container = dict(self.default_container)
            container.update(new_container)
            containers.append(container)
        return container_name, containers
 
    def _merge_params(
            self,
            params: 'StorageAccountParams',
            *,
            symbol: ModuleSymbol,
            parameters: Dict[str, Parameter],
            identity: ModuleSymbol,
            attrname: Optional[str] = None,
            **kwargs
    ) -> Dict[str, Output]:
        new_container = self.properties["blobServices"]["containers"][0]
        self._update_role_assignments(
            new_container,
            symbol=symbol,
            identity=identity,
            user_principal=parameters.get("principalId")
        )
        blob_services = params.pop("blobServices", dict(self.default_services))
        container_name, containers = self._merge_containers(
            blob_services.pop("containers", []),
            new_container,
            parameters['cloudmachineId']
            )
        blob_services["containers"] = containers
        outputs = super()._merge_params(params, symbol=symbol, attrname=attrname)
        params.update(self.properties)
        params["blobServices"] = blob_services
        
        suffix = (attrname or self._suffix).upper()
        if isinstance(container_name, str):
            container_suffix = container_name
        else:
            container_suffix = container_name.format()
        outputs[f"AZURE_BLOBS_ENDPOINT_{suffix}"] = Output("outputs.primaryBlobEndpoint", symbol)
        outputs[f"AZURE_BLOBS_CONTAINER_ENDPOINT_{suffix}"] = Output(
            "outputs.primaryBlobEndpoint",
            symbol
        ).format(suffix=f"/{container_suffix}")
        outputs[f"AZURE_BLOBS_CONTAINER_NAME_{suffix}"] = container_name
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
    def __call__(self, *, transport: Any = None, options: Optional[Dict[str, Any]] = None) -> 'ContainerClient':
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
        kwargs['credential'] = self.credential()
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
        if cls and cls.__name__ != 'ContainerClient':
            client = cls(self.endpoint(), **kwargs)
        else:
            from azure.storage.blob import ContainerClient
            try:
                client = ContainerClient.from_container_url(
                    container_url=self.container_endpoint(),
                    **kwargs
                )
            except RuntimeError:
                client = ContainerClient(
                    self.endpoint(),
                    self.container_name(),
                    **kwargs
                )
        client.__resource_settings__ = self
        return client
