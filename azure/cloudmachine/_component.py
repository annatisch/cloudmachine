from inspect import get_annotations
from typing import (
    TYPE_CHECKING,
    Mapping,
    dataclass_transform,
    overload,
    TypeVar,
    Any, Union, Literal, Optional, Callable, Dict, List, Type, Unpack
)

from ._resource import Resource, DefaultAction, _load_dev_environment

if TYPE_CHECKING:
    from .resources import (
        ResourceGroup,
        UserAssignedIdentity,
        StorageAccount,
        TableStorage,
        BlobStorage,
        BlobContainer,
        DatalakeStorage,
        QueueStorage,
        FileShareStorage,
        FileShare,
        EventSystemTopic,
        SystemTopicSubscription,
    )
    from .resources.managedidentity import UserAssignedIdentityParams, UserAssignedIdentityKwargs
    from .resources.resourcegroup import ResourceGroupParams, ResourceGroupKwargs
    from .resources.storage import StorageAccountParams, StorageAccountKwargs
    from .resources.storage.tables import TableServiceParams, TableStorageKwargs
    from .resources.storage.blobs import BlobServiceParams, BlobStorageKwargs
    from .resources.storage.blobs.container import ContainerParams, ContainerKwargs
    from .resources.storage.queues import QueueServiceParams, QueueStorageKwargs
    from .resources.storage.files import FileServiceParams, FileStorageKwargs
    from .resources.storage.files.share import ShareParams, ShareKwargs
    from .resources.eventgrid.systemtopic import SystemTopicParams, SystemTopicKwargs
    from .resources.eventgrid.systemtopic.subscription import SystemTopicSubscriptionParams, SystemTopicSubscriptionKwargs
    from. resources.keyvault._resource import KeyVaultParams, KeyVaultKwargs, KeyVault
    from .resources.ml._resource import MachineLearningServicesWorkspaceKwargs, AIHub, AIProject
    from .resources.ai._resource import CognitiveServicesKwargs, AIServices
    from .resources.ai.deployment._resource import DeploymentKwargs, DeploymentParams, AIChatCompletions, AITextEmbeddings, AIDeployment
    from .resources.search._resource import SearchServiceParams, SearchServiceKwargs, SearchService

AnnotationType = TypeVar('AnnotationType')

def reference(
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
                'storage:queues',
                'storage:files',
                'storage:files:share',
                'events:systemtopic',
                'events:systemtopic:subscription',
                'search',
                'keyvault',
                'ai:hub',
                'ai:project',
                'ai',
                'ai:model:chat',
                'ai:model:embeddings',
            ]
        ] = "",
        *,
        resource_group: Optional[Union[str, 'ResourceGroup']] = None,
        subscription: Optional[str] = None,
        **kwargs
) -> Resource:
    if resource == "resourcegroup":
        from .resources.resourcegroup._resource import ResourceGroup
        return ResourceGroup.reference(subscription=subscription, **kwargs)
    if resource == "userassignedidentity":
        from .resources.managedidentity._resource import UserAssignedIdentity
        return UserAssignedIdentity.reference(resource_group=resource_group, subscription=subscription, **kwargs)
    if resource == "storage":
        from .resources.storage._resource import StorageAccount
        return StorageAccount.reference(resource_group=resource_group, subscription=subscription, **kwargs)
    if resource == "storage:tables":
        from .resources.storage.tables._resource import TableStorage
        return TableStorage.reference(resource_group=resource_group, subscription=subscription, **kwargs)
    if resource == "storage:blobs":
        from .resources.storage.blobs._resource import BlobStorage
        return BlobStorage.reference(resource_group=resource_group, subscription=subscription, **kwargs)
    if resource == "storage:blobs:container":
        from .resources.storage.blobs.container._resource import BlobContainer
        return BlobContainer.reference(resource_group=resource_group, subscription=subscription, **kwargs)
    if resource == "storage:datalake":
        from .resources.storage.blobs._resource import DatalakeStorage
        return DatalakeStorage.reference(resource_group=resource_group, subscription=subscription, **kwargs)
    if resource == "storage:queues":
        from .resources.storage.queues._resource import QueueStorage
        return QueueStorage.reference(resource_group=resource_group, subscription=subscription, **kwargs)
    if resource == "storage:files":
        from .resources.storage.files._resource import FileShareStorage
        return FileShareStorage.reference(resource_group=resource_group, subscription=subscription, **kwargs)
    if resource == "storage:files:share":
        from .resources.storage.files.share._resource import FileShare
        return FileShare.reference(resource_group=resource_group, subscription=subscription, **kwargs)
    if resource == "events:systemtopic":
        from .resources.eventgrid.systemtopic._resource import EventSystemTopic
        return EventSystemTopic.reference(resource_group=resource_group, subscription=subscription, **kwargs)
    if resource == "events:systemtopic:subscription":
        from .resources.eventgrid.systemtopic.subscription._resource import SystemTopicSubscription
        return SystemTopicSubscription.reference(resource_group=resource_group, subscription=subscription, **kwargs)
    if resource == "keyvault":
        from .resources.keyvault._resource import KeyVault
        return KeyVault.reference(resource_group=resource_group, subscription=subscription, **kwargs)
    if resource == "ai":
        from .resources.ai._resource import AIServices
        return AIServices.reference(resource_group=resource_group, subscription=subscription, **kwargs)
    if resource == "ai:model:chat":
        from .resources.ai.deployment._resource import AIChatCompletions
        return AIChatCompletions.reference(resource_group=resource_group, subscription=subscription, **kwargs)
    if resource == "ai:model:embeddings":
        from .resources.ai.deployment._resource import AITextEmbeddings
        return AITextEmbeddings.reference(resource_group=resource_group, subscription=subscription, **kwargs)
    if resource == "ai:hub":
        from .resources.ml._resource import AIHub
        return AIHub.reference(resource_group=resource_group, subscription=subscription, **kwargs)
    if resource == "ai:project":
        from .resources.ml._resource import AIProject
        return AIProject.reference(resource_group=resource_group, subscription=subscription, **kwargs)
    if resource.startswith("Microsoft."):
        raise NotImplementedError("Raw resources not supported yet.")
    else:
        return Resource._from_inferred_resource(
            resource,
            resource_group=resource_group,
            subscription=subscription,
            **kwargs
        )


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
                'storage:queues',
                'storage:files',
                'storage:files:share',
                'events:systemtopic',
                'events:systemtopic:subscription',
                'search',
                'keyvault',
                'ai:hub',
                'ai:project',
                'ai',
                'ai:model:chat',
                'ai:model:embeddings',
            ]
        ] = "",
        *args,
        default: Union[DefaultAction, Resource, AnnotationType] = DefaultAction.BUILD_DEFAULT,
        default_factory: Optional[Union[Callable[[Dict[str, Any]], Resource], Callable[[Dict[str, Any]], AnnotationType]]] = None,
        **kwargs
) -> Resource:
    if isinstance(resource, Resource):
        if args:
            raise ValueError("Resource names cannot be specified alongside an existing resource.")
        # TODO: update resource params from kwargs
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
    if resource == "storage:datalake":
        from .resources.storage.blobs._resource import DatalakeStorage
        return DatalakeStorage(None, *args, default=default, default_factory=default_factory, **kwargs)
    if resource == "storage:queues":
        from .resources.storage.queues._resource import QueueStorage
        return QueueStorage(None, *args, default=default, default_factory=default_factory, **kwargs)
    if resource == "storage:files":
        from .resources.storage.files._resource import FileShareStorage
        return FileShareStorage(None, *args, default=default, default_factory=default_factory, **kwargs)
    if resource == "storage:files:share":
        from .resources.storage.files.share._resource import FileShare
        return FileShare(None, *args, default=default, default_factory=default_factory, **kwargs)
    if resource == "events:systemtopic":
        from .resources.eventgrid.systemtopic._resource import EventSystemTopic
        return EventSystemTopic(None, *args, default=default, default_factory=default_factory, **kwargs)
    if resource == "events:systemtopic:subscription":
        from .resources.eventgrid.systemtopic.subscription._resource import SystemTopicSubscription
        return SystemTopicSubscription(None, *args, default=default, default_factory=default_factory, **kwargs)
    if resource == "keyvault":
        from .resources.keyvault._resource import KeyVault
        return KeyVault(None, *args, default=default, default_factory=default_factory, **kwargs)
    if resource == "ai":
        from .resources.ai._resource import AIServices
        return AIServices(None, *args, default=default, default_factory=default_factory, **kwargs)
    if resource == "ai:model:chat":
        from .resources.ai._resource import AIChat
        return AIChatCompletions(None, *args, default=default, default_factory=default_factory, **kwargs)
    if resource == "ai:model:embeddings":
        from .resources.ai._resource import AIEmbeddings
        return AITextEmbeddings(None, *args, default=default, default_factory=default_factory, **kwargs)
    if resource == "ai:hub":
        from .resources.ml._resource import AIHub
        return AIHub(None, *args, default=default, default_factory=default_factory, **kwargs)
    if resource == "ai:project":
        from .resources.ml._resource import AIProject
        return AIProject(None, *args, default=default, default_factory=default_factory, **kwargs)
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


@dataclass_transform(field_specifiers=(resource, reference, _parameter, Resource), kw_only_default=True)
class CloudMachineComponent(type):

    def __call__(cls, **kwargs):
        if kwargs.get('env_name'):
            kwargs['config_store'] = _load_dev_environment(kwargs['env_name'])
        if issubclass(cls, CloudMachine):
            instance_kwargs = {}
            annotations = get_annotations(cls)
            required_params = [k for k in annotations.keys() if k not in cls.__dict__]
            for attr in cls.__dict__:
                value = kwargs.get(attr, getattr(cls, attr))
                if isinstance(value, Resource):
                    annotation = annotations.get(attr)
                    instance_kwargs[attr] = value(
                        annotation,
                        config_store=kwargs.get('config_store')
                    )
            kwargs.update(instance_kwargs)
            for param in required_params:
                if param not in kwargs:
                    raise TypeError(f"Missing required keyword argument '{param}'.")
        return super().__call__(**kwargs)


class CloudMachine(metaclass=CloudMachineComponent):
    _config_store: Mapping[str, Any] = _parameter(alias="config_store", default_factory=dict)
    _env_name: Optional[str] = _parameter(alias="env_name", default=None)

    def __init__(self, **kwargs):
        self._config_store = kwargs.pop('config_store', {})
        self._env_name = kwargs.pop('env_name', None)
        for key, value in kwargs.items():
            setattr(self, key, value)
