from inspect import get_annotations
from enum import StrEnum
from typing import (
    TYPE_CHECKING,
    Mapping,
    Self,
    dataclass_transform,
    overload,
    TypeVar,
    Any, Union, Literal, Optional, Callable, Dict, List, Type, Unpack
)

from ._bicep.expressions import Parameter
from ._resource import Resource, DefaultAction, _load_dev_environment, ResourceReference
from .resources._identifiers import ResourceIdentifiers

MISSING = DefaultAction.MISSING
BUILD_DEFAULT = DefaultAction.BUILD_DEFAULT


CLIENT_BY_ANNOTATION: Dict[str, ResourceIdentifiers] = {
    'BlobServiceClient': ResourceIdentifiers.blob_storage,
    'DataLakeServiceClient': ResourceIdentifiers.blob_storage,
    'ContainerClient': ResourceIdentifiers.blob_container,
    'FileSystemClient': ResourceIdentifiers.blob_container,
    'TableServiceClient': ResourceIdentifiers.table_storage,
    'ShareServiceClient': ResourceIdentifiers.file_share,
    'ShareClient': ResourceIdentifiers.file_share,
    'QueueServiceClient': ResourceIdentifiers.queue_storage,
    'KeyClient': ResourceIdentifiers.keyvault,
    'SecretClient': ResourceIdentifiers.keyvault,
    'CertificateClient': ResourceIdentifiers.keyvault,
    'ChatCompletionsClient': ResourceIdentifiers.ai_chat_deployment,
    'Chat': ResourceIdentifiers.ai_chat_deployment,
    'AsyncChat': ResourceIdentifiers.ai_chat_deployment,
    'EmbeddingsClient': ResourceIdentifiers.ai_embeddings_deployment,
    'Embeddings': ResourceIdentifiers.ai_embeddings_deployment,
    'AsyncEmbeddings': ResourceIdentifiers.ai_embeddings_deployment,
    'AIServices': ResourceIdentifiers.ai_services,
    'AIHub': ResourceIdentifiers.ai_hub,
    'AIProject': ResourceIdentifiers.ai_project,
    'AIProjectClient': ResourceIdentifiers.ai_project,
    'SearchIndexerClient': ResourceIdentifiers.search,
    'SearchIndexClient': ResourceIdentifiers.search
}


class AnnotationResource:
    def __init__(self, resource: Optional[Resource], default_action: DefaultAction, **kwargs):
        self._annotation: Optional[ResourceIdentifiers] = None
        self._default_action = default_action
        self._default_factory = kwargs.pop('default_factory', None)
        self._resource: Optional[Resource] = resource
        self._resource_kwargs = kwargs
        self._owner: Optional[Type] = None
        self._attrname: Optional[str] = None

    def __set_name__(self, owner: Type, name: str) -> None:
        self._owner = owner
        self._attrname = name
        if self._resource:
            self._resource._infra_objects.append(self._owner)
            self._resource._infra_attr_names.append(self._attrname)
        try:
            self._annotation = get_annotations(owner)[name]
        except KeyError:
            raise RuntimeError(f"Resource '{name}' is missing type hint or resource identifier.") from None

    def __get__(self, *args) -> Resource:
        if self._resource:
            return self._resource
        elif self._default_factory:
            return self._default_factory(self._resource_kwargs)
        self._resource = self._annotation(default_action=self._default_action, **self._resource_kwargs)
        self._resource._infra_objects.append(self._owner)
        self._resource._infra_attr_names.append(self._attrname)
        return self._resource


def resource(*, default: Optional[Union[Resource, DefaultAction]] = BUILD_DEFAULT, default_factory: Optional[Callable[[Dict[str, Any]], Resource]] = None) -> Resource:
    if isinstance(default, Resource):
        if default_factory:
            raise TypeError("Cannot specify both 'default' and 'default_factory'.")
        default_action = MISSING
        resource = default
    else:
        default_action = default
        resource = None
    return AnnotationResource(
        resource=resource,
        default_action=default_action,
        default_factory=default_factory
    )


def _parameter(*, default = None, default_factory = None, **kwargs):
    # TODO not sure how we should handle this yet
    if default:
        return default
    if default_factory:
        return default_factory()
    return None


class ClientBuilder:
    def __init__(self, resource: Optional[Resource] = MISSING, **client_options):
        self.client_options = client_options
        self.client_cls: Optional[Type] = None
        self._resource = resource
        self._default_factory = client_options.pop('default_factory', None)
        self._owner: Optional[Type] = None
        self._attrname: Optional[str] = None

    def __set_name__(self, owner: Type, name: str) -> None:
        self._owner = owner
        self._attrname = name
        try:
            self.client_cls = get_annotations(owner)[name]
        except KeyError:
            raise RuntimeError(f"Resource '{name}' is missing client type hint.") from None

    def __get__(self, *args):
        if self._resource is not MISSING:
            if isinstance(self._resource, Resource):
                return self._resource.get_client(self.client_cls, **self.client_options)
            return self._resource
        elif self._default_factory:
            return self._default_factory(self.client_options)
        raise AttributeError("No default resource provided.")


def client(*, default: Optional[Resource] = MISSING, default_factory: Optional[Callable[[Dict[str, Any]], Resource]] = None, **client_options):
    # TODO: There's other field specifier options we should add (even if they're not supported.)
    if default is not MISSING and default_factory:
        raise TypeError("Cannot specify both 'default' and 'default_factory'.")
    return ClientBuilder(resource=default, default_factory=default_factory, **client_options)


@dataclass_transform(field_specifiers=(resource, _parameter, client), kw_only_default=True)
class CloudMachineComponent(type):

    def __call__(cls, **kwargs):
        if kwargs.get('env_name'):
            kwargs['config_store'] = _load_dev_environment(kwargs['env_name'])
        annotations = get_annotations(cls)
        required_params = [k for k in annotations.keys() if k not in cls.__dict__]
        if issubclass(cls, AzureInfrastructure):
            instance_kwargs = {}
            for attr in cls.__dict__:
                instance_kwargs[attr] = kwargs.get(attr, getattr(cls, attr))
                value = kwargs.get(attr, getattr(cls, attr))
                if isinstance(value, Resource) and 'config_store' in kwargs:
                    value.set_config_store(kwargs['config_store'])
                    # annotation = annotations.get(attr)
                    # instance_kwargs[attr] = value(
                    #     annotation,
                    #     config_store=kwargs.get('config_store')
                    # )
                instance_kwargs[attr] = value
            kwargs.update(instance_kwargs)
        elif issubclass(cls, AzureApp):
            instance_kwargs = {}
            for attr, attr_type in annotations.items():
                if attr in kwargs:
                    value = kwargs[attr]
                    if isinstance(value, Resource) and attr in cls.__dict__ and isinstance(cls.__dict__[attr], ClientBuilder):
                        instance_kwargs[attr] = value.get_client(attr_type, **cls.__dict__[attr].client_options)
                elif attr in cls.__dict__ and isinstance(cls.__dict__[attr], ClientBuilder):
                    try:
                        instance_kwargs[attr] = getattr(cls, attr)
                    except AttributeError:
                        raise TypeError(f"Missing required keyword argument '{attr}'.")
                elif attr in cls.__dict__:
                    instance_kwargs[attr] = getattr(cls, attr)

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


class AzureApp(metaclass=CloudMachineComponent):
    _config_store: Mapping[str, Any] = _parameter(alias="config_store", default_factory=dict)
    _env_name: Optional[str] = _parameter(alias="env_name", default=None)

    def __init__(self, **kwargs):
        self._config_store = kwargs.pop('config_store', {})
        self._env_name = kwargs.pop('env_name', None)
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def from_infra(cls, infra: Union[AzureInfrastructure], /) -> Self:
        infra_resources = {r.identifier: r for r in infra.__dict__.values() if isinstance(r, Resource)}
        app_resources = {attr: value for attr, value in cls.__dict__.items() if isinstance(value, ClientBuilder)}
        kwargs = {}
        for key, value in app_resources.items():
            app_resource = CLIENT_BY_ANNOTATION[value.client_cls.__name__]
            if app_resource in infra_resources:
                kwargs[key] = infra_resources[app_resource]
        return cls(**kwargs)
