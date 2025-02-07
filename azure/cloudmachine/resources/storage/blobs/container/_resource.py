
import inspect
from typing import TYPE_CHECKING, Callable, Dict, List, Literal, Mapping, Self, Union, Unpack, overload, Optional, Any, Type, TypeVar

from azure.cloudmachine.resources.resourcegroup._resource import ResourceGroup

from ....._bicep.expressions import ModuleSymbol, Output, Parameter, ResourceSymbol, Expression
from ....._setting import StoredPrioritizedSetting
from ....._resource import (
    Resource,
    _ClientResource,
    _build_envs,
)
from ..._resource import _DEFAULT_STORAGE_ACCOUNT
from .._resource import _DEFAULT_BLOB_STORAGE, BlobStorage


if TYPE_CHECKING:
    from .. import BlobServiceParams
    from ... import StorageAccountParams
    from . import ContainerParams, ContainerKwargs
    from azure.storage.blob import ContainerClient
    from azure.storage.filedatalake import FileSystemClient

_DEFAULT_CONTAINER: 'ContainerParams' = {}

ClientType = TypeVar("ClientType")


class BlobContainer(_ClientResource):
    identifier: Literal["storage:blobs:container"] = "storage:blobs:container"
    module: Literal["br/public:avm/res/storage/storage-account"] = "br/public:avm/res/storage/storage-account"
    DEFAULTS: 'StorageAccountParams' = _DEFAULT_STORAGE_ACCOUNT
    DEFAULT_SERVICES: 'BlobServiceParams' = _DEFAULT_BLOB_STORAGE
    DEFAULT_CONTAINER: 'ContainerParams' = _DEFAULT_CONTAINER
    resource: Literal["Microsoft.Storage/storageAccounts/blobServices/containers"]
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
        )
        self.container_endpoint = StoredPrioritizedSetting(
            name='container_endpoint',
            env_vars=_build_envs(self._prefixes, ['CONTAINER_ENDPOINT']),
            system_hook=self._build_container_endpoint
        )
        self._settings['container_name'] = self.container_name
        self._settings['container_endpoint'] = self.container_endpoint

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
            account_name: str,
            container_name: str,
            resource_group: Optional[Union[str, ResourceGroup]] = None,
            subscription: Optional[str] = None,
    ) -> Self:
        ...
    @classmethod
    def reference(
            cls,
            resource_id: Optional[str] = None,
            *,
            account_name: Optional[str] = None,
            container_name: Optional[str] = None,
            resource_group: Optional[str] = None,
            subscription: Optional[str] = None
    ) -> Self:
        if resource_id:
            return super().reference(resource_id)
        from . import MODULE_RESOURCE, MODULE_VERSION
        resource = f"{MODULE_RESOURCE}@{MODULE_VERSION}"

        parent = BlobStorage.reference(
            name=account_name,
            resource_group=resource_group,
            subscription=subscription
        )
        existing = super().reference(resource=resource, name=container_name, parent=parent)
        existing.container_name.set_value(container_name)
        return existing

    def _build_endpoint(self) -> str:
        return f"https://{self.name()}.blob.core.windows.net/"

    def _build_container_endpoint(self) -> str:
        return f"https://{self.name()}.blob.core.windows.net/{self.container_name()}"

    def _merge_containers(
            self,
            containers: List['ContainerParams'],
            new_container: 'ContainerParams',
            *,
            symbol: ModuleSymbol,
            parameters: Dict[str, Parameter],
            identity: ModuleSymbol,
    ) -> List['ContainerParams']:
        container_name = new_container.get('name') or parameters['defaultName']
        existing = False
        for container in containers:
            if container['name'] == container_name:
                existing = True
                role_assignments = container.pop('roleAssignments')
                container.update(new_container)
                self._update_role_assignments(
                    container,
                    role_assignments,
                    symbol=symbol,
                    identity=identity,
                    user_principal=parameters.get("principalId")
                )
        if not existing:
            container = dict(self.DEFAULT_CONTAINER)
            container['name'] = container_name
            container.update(new_container)
            self._update_role_assignments(
                container,
                symbol=symbol,
                identity=identity,
                user_principal=parameters.get("principalId")
            )
            containers.append(container)
        return container_name, containers

    def _outputs(
            self,
            *,
            symbol: ResourceSymbol,
            name: Union[str, Expression],
            parent: Optional[ResourceSymbol] = None,
            **kwargs
        ) -> Dict[str, Union[Output, str]]:
        suffix = self._get_suffix()
        if isinstance(name, str):
            url_suffix = name
        else:
            url_suffix = name.format()
        if parent:
            outputs = {}
            outputs[f"AZURE_BLOBS_CONTAINER_ENDPOINT{suffix}"] = Output(
                "properties.primaryEndpoints.blob",
                symbol
            ).format(suffix=f"{url_suffix}")
            outputs[f"AZURE_BLOBS_CONTAINER_NAME{suffix}"] = name
        else:
            outputs = super()._outputs(symbol=symbol, **kwargs)
            outputs[f"AZURE_BLOBS_ENDPOINT{suffix}"] = Output("outputs.serviceEndpoints.blob", symbol)
            outputs[f"AZURE_BLOBS_CONTAINER_ENDPOINT{suffix}"] = Output(
                "outputs.serviceEndpoints.blob",
                symbol
            ).format(suffix=f"{url_suffix}")
            outputs[f"AZURE_BLOBS_CONTAINER_NAME{suffix}"] = name
        return outputs

    def _merge_params(
            self,
            params: 'StorageAccountParams',
            *,
            symbol: ModuleSymbol,
            parameters: Dict[str, Parameter],
            identity: ModuleSymbol,
            attrname: Optional[str] = None,
            **kwargs
    ) -> Dict[str, Any]:
        new_container = self.properties["blobServices"]["containers"][0]
        blob_services = params.pop("blobServices", dict(self.DEFAULT_SERVICES))
        container_name, containers = self._merge_containers(
            blob_services.pop("containers", []),
            new_container,
            parameters=parameters,
            identity=identity,
            symbol=symbol
        )
        blob_services["containers"] = containers
        output_config = super()._merge_params(params, symbol=symbol, attrname=attrname, **kwargs)
        output_config['name'] = container_name
        params["blobServices"] = blob_services
        return output_config

    @overload
    def __call__(
            self,
            cls: Callable[..., ClientType],
            /,
            *,
            transport: Any = None,
            options: Optional[Dict[str, Any]] = None,
            config_store: Optional[Mapping[str, Any]] = None,
            env_name: Optional[str] = None,
    ) -> ClientType:
        ...
    @overload
    def __call__(self, *, config_store: Optional[Mapping[str, Any]] = None, env_name: Optional[str] = None) -> Self:
        ...
    def __call__(self, cls=None, /, *, transport=None, options=None, config_store=None, env_name=None):
        options = options or {}
        if transport:
            options['transport'] = transport
        try:
            # First we check if it's a Resource type or whether it has 'from_resource' constructor
            return Resource.__call__(self, cls, options=options, config_store=config_store, env_name=env_name)
        except TypeError:
            pass
        kwargs = {}
        is_async = inspect.iscoroutinefunction(getattr(cls, 'close'))
        kwargs['credential'] = self._build_credential(is_async)
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
        if hasattr(cls, 'from_container_url'):
            endpoint = self.container_endpoint()
            client = cls.from_container_url(endpoint, **kwargs)
        else:
            endpoint = self.endpoint()
            kwargs['container_name'] = self.container_name()
            client = cls(endpoint, **kwargs)
        client.__resource_settings__ = self
        return client


class FileSystem(BlobContainer):
    identifier: Literal["storage:datalake:filesystem"] = "storage:datalake:filesystem"

    def __init__(
            self,
            properties: Optional['ContainerParams'] = None,
            storage_name: Optional[str] = None,
            filesystem_name: Optional[str] = None,
            *,
            role_assignments = ['Storage Blob Data Contributor'],
            **kwargs: Unpack['ContainerKwargs']
    ) -> None:
        super().__init__(
            properties=properties,
            storage_name=storage_name,
            container_name=filesystem_name,
            role_assignments=role_assignments,
            **kwargs
        )

    def _build_endpoint(self) -> str:
        raise NotImplementedError()
