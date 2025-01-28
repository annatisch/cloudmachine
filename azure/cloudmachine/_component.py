from dataclasses import MISSING
from inspect import get_annotations
from typing import (
    TYPE_CHECKING,
    Mapping,
    dataclass_transform,
    overload,
    Any, Union, Literal, Optional, Callable, Dict, List, Type, Unpack
)

from ._resource import Resource

if TYPE_CHECKING:
    from .resources import (
        ResourceGroup,
        UserAssignedIdentity,
        StorageAccount,
        TableStorage,
        BlobStorage,
        BlobContainer,
    )
    from .resources.managedidentity import UserAssignedIdentityParams, UserAssignedIdentityKwargs
    from .resources.resourcegroup import ResourceGroupParams, ResourceGroupKwargs
    from .resources.storage import StorageAccountParams, StorageAccountKwargs
    from .resources.storage.tables import TableServiceParams, TableStorageKwargs
    from .resources.storage.blobs import BlobServiceParams, BlobStorageKwargs
    from .resources.storage.blobs.container import ContainerParams, ContainerKwargs


@overload
def resource(
    resource: Literal['resourcegroup'],
    /,
    storage_name: Optional[str] = None,
    *,
    default: 'ResourceGroupParams',
    default_factory: Optional[Callable[[], 'ResourceGroupParams']],
    **kwargs: Unpack['ResourceGroupKwargs']
) -> 'ResourceGroup':
    ...
@overload
def resource(
    resource: Literal['userassignedidentity'],
    /,
    storage_name: Optional[str] = None,
    *,
    default: 'UserAssignedIdentityParams',
    default_factory: Optional[Callable[[], 'UserAssignedIdentityParams']],
    **kwargs: Unpack['UserAssignedIdentityKwargs']
) -> 'UserAssignedIdentity':
    ...
@overload
def resource(
    resource: Literal['storage'],
    /,
    storage_name: Optional[str] = None,
    *,
    default: 'StorageAccountParams',
    default_factory: Optional[Callable[[], 'StorageAccountParams']],
    **kwargs: Unpack['StorageAccountKwargs']
) -> 'StorageAccount':
    ...
@overload
def resource(
    resource: Literal['storage:tables'],
    /,
    storage_name: Optional[str] = None,
    *,
    default: 'TableServiceParams',
    default_factory: Callable[[], 'TableServiceParams'],
    **kwargs: Unpack['TableStorageKwargs']
) -> 'TableStorage':
    ...
@overload
def resource(
    resource: Literal['storage:blobs'],
    /,
    storage_name: Optional[str] = None,
    *,
    default: 'BlobServiceParams',
    default_factory: Callable[[], 'BlobServiceParams'],
    **kwargs: Unpack['BlobStorageKwargs']
) -> 'BlobStorage':
    ...
@overload
def resource(
    resource: Literal['storage:blobs:container'],
    /,
    storage_name: Optional[str] = None,
    container_name: Optional[str] = None,
    *,
    default: 'ContainerParams',
    default_factory: Callable[[], 'ContainerParams'],
    **kwargs: Unpack['ContainerKwargs']
) -> 'BlobContainer':
    ...
def resource(
        resource: Union[
            Resource,
            str,
            Literal[
                'resourcegroup',
                'userassignedidentity',
                'storage',
                'storage:blobs',
                'storage:tables',
                'storage:blobs:container',
            ]
        ] = "",
        *args,
        default = MISSING,
        default_factory = MISSING,
        **kwargs
) -> Resource:
    if isinstance(resource, Resource):
        if args:
            raise ValueError("Resource names cannot be specified alongside an existing resource.")
        # TODO: update resource params from kwargs
        # return resource.__copy(**kwargs)
        return resource

    if resource == "resourcegroup":
        from .resources.resourcegroup._resource import ResourceGroup
        return ResourceGroup(None, *args, default=default, default_factory=default_factory, **kwargs)
    if resource == "userassignedidentity":
        from .resources.managedidentity._resource import UserAssignedIdentity
        return UserAssignedIdentity(None, *args, default=default, default_factory=default_factory, **kwargs)
    if resource == "storage":
        from .resources.storage._resource import StorageAccount
        return StorageAccount(None, *args, default=default, default_factory=default_factory, **kwargs)
    if resource == "storage:tables":
        from .resources.storage.tables._resource import TableStorage
        return TableStorage(None, *args, default=default, default_factory=default_factory, **kwargs)
    if resource == "storage:blobs":
        from .resources.storage.blobs._resource import BlobStorage
        return BlobStorage(None, *args, default=default, default_factory=default_factory, **kwargs)
    if resource == "storage:blobs:container":
        from .resources.storage.blobs.container._resource import BlobContainer
        return BlobContainer(None, *args, default=default, default_factory=default_factory, **kwargs)

    if resource.startswith("Microsoft."):
        raise NotImplementedError("Raw resources not supported yet.")
    else:
        return Resource._from_inferred_resource(
            resource,
            *args,
            default=default,
            default_factory=default_factory,
            **kwargs
        )


def _parameter(*, default = None, default_factory = None, **kwargs):
    # TODO not sure how we should handle this yet
    if default:
        return default
    if default_factory:
        return default_factory()
    return None


@dataclass_transform(field_specifiers=(resource, _parameter, Resource), kw_only_default=True)
class CloudMachineComponent(type):

    def __call__(cls, **kwargs):
        if issubclass(cls, CloudMachineClient):
            instance_kwargs = {}
            annotations = get_annotations(cls)
            required_params = [k for k in annotations.keys() if k not in cls.__dict__]
            for attr, default_value in cls.__dict__.items():
                value = kwargs.get(attr, default_value)
                if isinstance(value, Resource):
                    annotation = annotations.get(attr)
                    instance_kwargs[attr] = value(annotation)
            kwargs.update(instance_kwargs)
            for param in required_params:
                if param not in kwargs:
                    raise TypeError(f"Missing required keyword argument '{param}'.")
        return super().__call__(**kwargs)


class CloudMachineClient(metaclass=CloudMachineComponent):
    _config_store: Mapping[str, Any] = _parameter(alias="config_store", default_factory=dict)

    def __init__(self, **kwargs):
        self._config_store = kwargs.pop('config_store', {})
        self.__dict__.update(kwargs)


class AsyncCloudMachineClient(CloudMachineClient):
    ...
