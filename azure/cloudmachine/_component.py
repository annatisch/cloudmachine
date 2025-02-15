from inspect import get_annotations
from enum import StrEnum
from typing import (
    TYPE_CHECKING,
    Mapping,
    dataclass_transform,
    overload,
    TypeVar,
    Any, Union, Literal, Optional, Callable, Dict, List, Type, Unpack
)

from ._bicep.expressions import Parameter
from ._resource import Resource, DefaultAction, _load_dev_environment, ResourceReference
from .resources._identifiers import ResourceIdentifiers

if TYPE_CHECKING:
    from .resources.managedidentity import UserAssignedIdentity, UserAssignedIdentityKwargs
    from .resources.resourcegroup import ResourceGroup, ResourceGroupKwargs
    from .resources.storage import StorageAccount, StorageAccountKwargs
    from .resources.ai import AIServices, AIServicesKwargs
    from .resources.ai.deployment import DeploymentKwargs, AIChat, AIEmbeddings, AIDeployment
    from .resources.ai.deployment.types import DeploymentResource

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
    from .resources.search._resource import SearchServiceParams, SearchServiceKwargs, SearchService


RESOURCE_BY_ANNOTATION: Dict[str, ResourceIdentifiers] = {
    'ResourceGroup': ResourceIdentifiers.resource_group,
    'UserAssignedIdentity': ResourceIdentifiers.user_assigned_identity,
    'StorageAccount': ResourceIdentifiers.storage_account,
    'BlobStorage': ResourceIdentifiers.blob_storage,
    'BlobServiceClient': ResourceIdentifiers.blob_storage,
    'DataLakeServiceClient': ResourceIdentifiers.datalake_storage,
    'BlobContainer': ResourceIdentifiers.blob_container,
    'ContainerClient': ResourceIdentifiers.blob_container,
    'FileSystemClient': ResourceIdentifiers.file_system,
    'TableStorage': ResourceIdentifiers.table_storage,
    'TableServiceClient': ResourceIdentifiers.table_storage,
    'FileShareStorage': ResourceIdentifiers.file_storage,
    'ShareServiceClient': ResourceIdentifiers.file_share,
    'FileShare': ResourceIdentifiers.file_share,
    'ShareClient': ResourceIdentifiers.file_share,
    'QueueStorage': ResourceIdentifiers.queue_storage,
    'QueueServiceClient': ResourceIdentifiers.queue_storage,
    'EventSystemTopic': ResourceIdentifiers.system_topic,
    'SystemTopicSubscription': ResourceIdentifiers.system_topic_subscription,
    'KeyVault': ResourceIdentifiers.keyvault,
    'KeyClient': ResourceIdentifiers.keyvault,
    'SecretClient': ResourceIdentifiers.keyvault,
    'CertificateClient': ResourceIdentifiers.keyvault,
    'AIChatCompletions': ResourceIdentifiers.ai_chat_deployment,
    'ChatCompletionsClient': ResourceIdentifiers.ai_chat_deployment,
    'Chat': ResourceIdentifiers.ai_chat_deployment,
    'AsyncChat': ResourceIdentifiers.ai_chat_deployment,
    'AITextEmbeddings': ResourceIdentifiers.ai_embeddings_deployment,
    'EmbeddingsClient': ResourceIdentifiers.ai_embeddings_deployment,
    'Embeddings': ResourceIdentifiers.ai_embeddings_deployment,
    'AsyncEmbeddings': ResourceIdentifiers.ai_embeddings_deployment,
    'AIServices': ResourceIdentifiers.ai_services,
    'AIHub': ResourceIdentifiers.ai_hub,
    'AIProject': ResourceIdentifiers.ai_project,
    'AIProjectClient': ResourceIdentifiers.ai_project,
    'SearchService': ResourceIdentifiers.search,
    'SearchIndexerClient': ResourceIdentifiers.search,
    'SearchIndexClient': ResourceIdentifiers.search
}


class AnnotationResource:
    def __init__(self, *args, **kwargs):
        self._resource_args = args
        self._resource_kwargs = kwargs
        self._annotation: Optional[ResourceIdentifiers] = None
        self._resource: Optional[Resource] = None
        self._owner: Optional[Type] = None
        self._attrname: Optional[str] = None

    def __set_name__(self, owner: Type, name: str) -> None:
        self._owner = owner
        self._attrname = name
        try:
            annotation = get_annotations(owner)[name]
        except KeyError:
            raise RuntimeError(f"Resource '{name}' is missing type hint or resource identifier.") from None
        try:
            self._annotation = RESOURCE_BY_ANNOTATION[annotation.__name__]
        except KeyError:
            raise RuntimeError(f"Unable to determine intended resource type for field name '{name}' with annotation: '{annotation}'.")

    def __get__(self, *args) -> Resource:
        if self._resource:
            return self._resource
        self._resource = resource(
            self._annotation,
            *self._resource_args,
            **self._resource_kwargs
        )
        self._resource._infra_objects.append(self._owner)
        self._resource._infra_attr_names.append(self._attrname)
        return self._resource


@overload
def resource(
    resource: Literal['resourcegroup'],
    /,
    name: Optional[Union[str, Parameter[str]]] = None,
    *,
    default: DefaultAction = DefaultAction.BUILD_DEFAULT,
    **kwargs: Unpack['ResourceGroupKwargs']
) -> 'ResourceGroup':
    ...
@overload
def resource(
    resource: Literal['userassignedidentity'],
    /,
    name: Optional[Union[str, Parameter[str]]] = None,
    *,
    default: DefaultAction = DefaultAction.BUILD_DEFAULT,
    **kwargs: Unpack['UserAssignedIdentityKwargs']
) -> 'UserAssignedIdentity':
    ...
@overload
def resource(
    resource: Literal['storage'],
    /,
    name: Optional[Union[str, Parameter[str]]] = None,
    *,
    default: DefaultAction = DefaultAction.BUILD_DEFAULT,
    **kwargs: Unpack['StorageAccountKwargs']
) -> 'StorageAccount':
    ...
@overload
def resource(
    resource: Literal['storage:tables'],
    /,
    name: Optional[Union[str, Parameter[str]]] = None,
    *,
    default: DefaultAction = DefaultAction.BUILD_DEFAULT,
    **kwargs: Unpack['TableStorageKwargs']
) -> 'TableStorage':
    ...
@overload
def resource(
    resource: Literal['storage:queues'],
    /,
    name: Optional[Union[str, Parameter[str]]] = None,
    *,
    default: DefaultAction = DefaultAction.BUILD_DEFAULT,
    **kwargs: Unpack['QueueStorageKwargs']
) -> 'QueueStorage':
    ...
@overload
def resource(
    resource: Literal['storage:blobs'],
    /,
    name: Optional[Union[str, Parameter[str]]] = None,
    *,
    default: DefaultAction = DefaultAction.BUILD_DEFAULT,
    **kwargs: Unpack['BlobStorageKwargs']
) -> 'BlobStorage':
    ...
@overload
def resource(
    resource: Literal['storage:blobs:container'],
    /,
    account_name: Optional[Union[str, Parameter[str]]] = None,
    container_name: Optional[Union[str, Parameter[str]]] = None,
    *,
    default: DefaultAction = DefaultAction.BUILD_DEFAULT,
    **kwargs: Unpack['ContainerKwargs']
) -> 'BlobContainer':
    ...
@overload
def resource(
    resource: Literal['storage:datalake'],
    /,
    name: Optional[Union[str, Parameter[str]]] = None,
    *,
    default: DefaultAction = DefaultAction.BUILD_DEFAULT,
    **kwargs: Unpack['BlobStorageKwargs']
) -> 'DatalakeStorage':
    ...
@overload
def resource(
    resource: Literal['storage:datalake:filesystem'],
    /,
    account_name: Optional[Union[str, Parameter[str]]] = None,
    container_name: Optional[Union[str, Parameter[str]]] = None,
    *,
    default: DefaultAction = DefaultAction.BUILD_DEFAULT,
    **kwargs: Unpack['ContainerKwargs']
) -> 'DatalakeStorage':
    ...
@overload
def resource(
    resource: Literal['storage:files'],
    /,
    name: Optional[Union[str, Parameter[str]]] = None,
    *,
    default: DefaultAction = DefaultAction.BUILD_DEFAULT,
    **kwargs: Unpack['FileStorageKwargs']
) -> 'FileShareStorage':
    ...
@overload
def resource(
    resource: Literal['storage:files:share'],
    /,
    account_name: Optional[Union[str, Parameter[str]]] = None,
    share_name: Optional[Union[str, Parameter[str]]] = None,
    *,
    default: DefaultAction = DefaultAction.BUILD_DEFAULT,
    **kwargs: Unpack['ShareKwargs']
) -> 'FileShare':
    ...
@overload
def resource(
    resource: Literal['events:systemtopic'],
    /,
    name: Optional[Union[str, Parameter[str]]] = None,
    *,
    default: DefaultAction = DefaultAction.BUILD_DEFAULT,
    **kwargs: Unpack['SystemTopicKwargs']
) -> 'EventSystemTopic':
    ...
@overload
def resource(
    resource: Literal['events:systemtopic:subscription'],
    /,
    systemtopic_name: Optional[Union[str, Parameter[str]]] = None,
    subscription_name: Optional[Union[str, Parameter[str]]] = None,
    *,
    default: DefaultAction = DefaultAction.BUILD_DEFAULT,
    **kwargs: Unpack['SystemTopicSubscriptionKwargs']
) -> 'SystemTopicSubscription':
    ...
@overload
def resource(
    resource: Literal['keyvault'],
    /,
    name: Optional[Union[str, Parameter[str]]] = None,
    *,
    default: DefaultAction = DefaultAction.BUILD_DEFAULT,
    **kwargs: Unpack['KeyVaultKwargs']
) -> 'KeyVault':
    ...
@overload
def resource(
    resource: Literal['search'],
    /,
    name: Optional[Union[str, Parameter[str]]] = None,
    *,
    default: DefaultAction = DefaultAction.BUILD_DEFAULT,
    **kwargs: Unpack['SearchServiceKwargs']
) -> 'SearchService':
    ...
@overload
def resource(
    resource: Literal['ai'],
    /,
    name: Optional[Union[str, Parameter[str]]] = None,
    *,
    default: DefaultAction = DefaultAction.BUILD_DEFAULT,
    **kwargs: Unpack['AIServicesKwargs']
) -> 'AIServices':
    ...
@overload
def resource(
    resource: Literal['ai:hub'],
    /,
    name: Optional[Union[str, Parameter[str]]] = None,
    *,
    default: DefaultAction = DefaultAction.BUILD_DEFAULT,
    **kwargs: Unpack['MachineLearningServicesWorkspaceKwargs']
) -> 'AIHub':
    ...
@overload
def resource(
    resource: Literal['ai:project'],
    /,
    name: Optional[Union[str, Parameter[str]]] = None,
    *,
    default: DefaultAction = DefaultAction.BUILD_DEFAULT,
    **kwargs: Unpack['MachineLearningServicesWorkspaceKwargs']
) -> 'AIProject':
    ...
@overload
def resource(
    resource: Literal['ai:deployment'],
    /,
    name: Optional[Union[str, Parameter[str]]] = None,
    *,
    default: DefaultAction = DefaultAction.BUILD_DEFAULT,
    **kwargs: Unpack['DeploymentKwargs']
) -> 'AIDeployment':
    ...
@overload
def resource(
    resource: Literal['ai:deployment:chat'],
    /,
    account: Optional[Union[str, 'AIServices', Parameter[str]]] = None,
    *,
    default: DefaultAction = DefaultAction.BUILD_DEFAULT,
    **kwargs: Unpack['DeploymentKwargs']
) -> 'AIChat[DeploymentResource]':
    ...
@overload
def resource(
    resource: Literal['ai:deployment:embeddings'],
    /,
    account: Optional[Union[str, 'AIServices', Parameter[str]]] = None,
    *,
    default: DefaultAction = DefaultAction.BUILD_DEFAULT,
    **kwargs: Unpack['DeploymentKwargs']
) -> 'AIEmbeddings[DeploymentResource]':
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
                'storage:datalake',
                'storage:blobs:container',
                'storage:datalake:filesystem',
                'storage:tables',
                'storage:queues',
                'storage:files',
                'storage:files:share',
                'events:systemtopic',
                'events:systemtopic:subscription'
                'keyvault',
                'search',
                'ai',
                'ai:project',
                'ai:hub',
                'ai:deployment',
                'ai:deployment:chat',
                'ai:deployment:embeddings',
            ]
        ] = "",
        *args,
        **kwargs
) -> Resource:
    try:
        default_action = DefaultAction(kwargs.pop('default'))
    except KeyError:
        default_action = DefaultAction.BUILD_DEFAULT
    kwargs['default_action'] = default_action
    if isinstance(resource, Resource):
        if args:
            raise ValueError("Resource names cannot be specified alongside an existing resource.")
        # TODO: update resource params from kwargs
        return resource
    if resource == ResourceIdentifiers.resource_group:
        from .resources.resourcegroup import ResourceGroup
        return ResourceGroup(None, *args, **kwargs)
    if resource == ResourceIdentifiers.user_assigned_identity:
        from .resources.managedidentity import UserAssignedIdentity
        return UserAssignedIdentity(None, *args, **kwargs)
    if resource == ResourceIdentifiers.storage_account:
        from .resources.storage import StorageAccount
        return StorageAccount(None, *args, **kwargs)
    if resource == ResourceIdentifiers.table_storage:
        from .resources.storage.tables._resource import TableStorage
        return TableStorage(None, *args, **kwargs)
    if resource == ResourceIdentifiers.blob_storage:
        from .resources.storage.blobs._resource import BlobStorage
        return BlobStorage(None, *args, **kwargs)
    if resource == ResourceIdentifiers.blob_container:
        from .resources.storage.blobs.container._resource import BlobContainer
        return BlobContainer(None, *args, **kwargs)
    if resource == ResourceIdentifiers.datalake_storage:
        from .resources.storage.blobs._resource import DatalakeStorage
        return DatalakeStorage(None, *args, **kwargs)
    if resource == ResourceIdentifiers.queue_storage:
        from .resources.storage.queues._resource import QueueStorage
        return QueueStorage(None, *args, **kwargs)
    if resource == ResourceIdentifiers.file_storage:
        from .resources.storage.files._resource import FileShareStorage
        return FileShareStorage(None, *args, **kwargs)
    if resource == ResourceIdentifiers.file_share:
        from .resources.storage.files.share._resource import FileShare
        return FileShare(None, *args, **kwargs)
    if resource == ResourceIdentifiers.system_topic:
        from .resources.eventgrid.systemtopic._resource import EventSystemTopic
        return EventSystemTopic(None, *args, **kwargs)
    if resource == ResourceIdentifiers.system_topic_subscription:
        from .resources.eventgrid.systemtopic.subscription._resource import SystemTopicSubscription
        return SystemTopicSubscription(None, *args, **kwargs)
    if resource == ResourceIdentifiers.keyvault:
        from .resources.keyvault._resource import KeyVault
        return KeyVault(None, *args, **kwargs)
    if resource == ResourceIdentifiers.ai_services:
        from .resources.ai import AIServices
        return AIServices(None, *args, **kwargs)
    if resource == ResourceIdentifiers.ai_chat_deployment:
        from .resources.ai.deployment import AIChat
        return AIChat(None, *args, **kwargs)
    if resource == ResourceIdentifiers.ai_embeddings_deployment:
        from .resources.ai.deployment import AIEmbeddings
        return AIEmbeddings(None, *args, **kwargs)
    if resource == ResourceIdentifiers.ai_hub:
        from .resources.ml._resource import AIHub
        return AIHub(None, *args, **kwargs)
    if resource == ResourceIdentifiers.ai_project:
        from .resources.ml._resource import AIProject
        return AIProject(None, *args, **kwargs)
    if resource.startswith("Microsoft."):
        raise NotImplementedError("Raw resources not supported yet.")
    else:
        return AnnotationResource(
            resource,
            *args,
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
        if kwargs.get('env_name'):
            kwargs['config_store'] = _load_dev_environment(kwargs['env_name'])
        if issubclass(cls, AzureInfrastructure):
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


class AzureInfrastructure(metaclass=CloudMachineComponent):
    _config_store: Mapping[str, Any] = _parameter(alias="config_store", default_factory=dict)
    _env_name: Optional[str] = _parameter(alias="env_name", default=None)

    def __init__(self, **kwargs):
        self._config_store = kwargs.pop('config_store', {})
        self._env_name = kwargs.pop('env_name', None)
        for key, value in kwargs.items():
            setattr(self, key, value)
