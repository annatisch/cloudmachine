from inspect import get_annotations
from typing import (
    TYPE_CHECKING,
    Mapping,
    Self,
    dataclass_transform,
    overload,
    TypeVar,
    Any, Union, Literal, Optional, Callable, Dict, List, Type, Unpack
)

from ._resource import Resource, DefaultResource, _load_dev_environment
from .resources._identifiers import ResourceIdentifiers


MISSING = DefaultResource.MISSING
BUILD_DEFAULT = DefaultResource.BUILD_DEFAULT
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


class InfrastructureResource:
    def __init__(
            self,
            resource: Union[DefaultResource, Resource],
            resource_factory: Union[Literal[DefaultResource.MISSING], Callable[[Mapping[str, Any]], Resource]],
            **kwargs
    ):
        self._resource_factory = resource_factory
        self._resource = resource
        self._resource_kwargs = kwargs
        self._annotation: Optional[Type] = None
        self._owner: Optional[Type] = None
        self._attrname: Optional[str] = None

    def __set_name__(self, owner: Type, name: str) -> None:
        self._owner = owner
        self._attrname = '_' + name
        try:
            self._annotation = get_annotations(owner)[name]
        except KeyError:
            raise RuntimeError(f"'{owner.__name__}.{name}' is missing type hint.") from None
        if not issubclass(self._annotation, Resource):
            raise RuntimeError(f"Incompatible type hint for {owner.__name__}.{name} - must be a Resource type.")

    def __get__(self, obj, _) -> Resource:
        if obj is None:
            if isinstance(self._resource, Resource):
                return self._resource
            if self._resource_factory is not MISSING:
                return self._resource_factory(self._resource_kwargs)
            if self._resource is MISSING:
                raise AttributeError(f"No default value provided for '{self._owner.__name__}.{self._attrname}'.")
            else:
                return self._annotation(**self._resource_kwargs)
        return getattr(obj, self._attrname)

    def __set__(self, obj: 'AzureInfrastructure', value: Resource):
        if not isinstance(value, self._annotation):
            raise TypeError(f"{self._owner.__name__}.{self._attrname} must be an instance of resource '{self._annotation}'.")
        value._set_infra(obj)
        setattr(obj, self._attrname, value)


def resource(
        *,
        default: Union[Resource, DefaultResource] = BUILD_DEFAULT,
        default_factory: Union[Callable[[Mapping[str, Any]], Resource], Literal[DefaultResource.MISSING]] = MISSING
) -> InfrastructureResource:
    if isinstance(default, Resource):
        if default_factory is not MISSING:
            raise ValueError("Cannot specify both 'default' and 'default_factory'.")

    return InfrastructureResource(
        resource=default,
        resource_factory=default_factory
    )


def _parameter(*, default = None, default_factory = None, **kwargs):
    # TODO not sure how we should handle this yet
    if default:
        return default
    if default_factory:
        return default_factory()
    return None


@dataclass_transform(field_specifiers=(resource, _parameter), kw_only_default=True)
class AzureInfraComponent(type):
    # TODO: The typing of the __call__ function is breaking
    # typing when kwargs are passed into the constructor.
    # Need to figure that out.....
    def __call__(cls, **kwargs):
        if 'env_name' in kwargs:
            if 'config_store' in kwargs:
                raise ValueError("Cannot specify both 'config_store' and 'env_name'.")
            kwargs['config_store'] = _load_dev_environment(kwargs['env_name'])
        instance_kwargs = {}
        for attr in get_annotations(cls):
            try:
                # TODO: This doesn't support None/Optional as a value, but that's
                # fine for now as Union type hints aren't supported. Could be a future
                # addition.
                instance_kwargs[attr] = kwargs.get(attr) or getattr(cls, attr)
            except AttributeError:
                raise TypeError(f"{cls.__name__} missing required keyword argument: '{attr}'.")
        kwargs.update(instance_kwargs)
        return super().__call__(**kwargs)


class AzureInfrastructure(metaclass=AzureInfraComponent):
    _config_store: Mapping[str, Any] = _parameter(alias="config_store", default_factory=dict)
    _env_name: Optional[str] = _parameter(alias="env_name", default=None)

    def __init__(self, **kwargs):
        self._config_store = kwargs.pop('config_store', {})
        self._env_name = kwargs.pop('env_name', None)
        for key, value in kwargs.items():
            setattr(self, key, value)


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

    def __get__(self, obj, type):
        if obj is None:
            if self._resource is not MISSING:
                if isinstance(self._resource, Resource):
                    return self._resource.get_client(self.client_cls, **self.client_options)
                return self._resource
            elif self._default_factory:
                return self._default_factory(self.client_options)
            raise AttributeError("No default resource provided.")
        return getattr(obj, self._attrname)



def client(*, default: Optional[Resource] = MISSING, default_factory: Optional[Callable[[Dict[str, Any]], Resource]] = None, **client_options):
    # TODO: There's other field specifier options we should add (even if they're not supported.)
    if default is not MISSING and default_factory:
        raise TypeError("Cannot specify both 'default' and 'default_factory'.")
    return ClientBuilder(resource=default, default_factory=default_factory, **client_options)


@dataclass_transform(field_specifiers=(_parameter, client), kw_only_default=True)
class AzureAppComponent(type):
    def __call__(cls, **kwargs):
        if kwargs.get('env_name'):
            kwargs['config_store'] = _load_dev_environment(kwargs['env_name'])
        annotations = get_annotations(cls)
        required_params = [k for k in annotations.keys() if k not in cls.__dict__]
        if issubclass(cls, AzureApp):
            instance_kwargs = {}
            for attr, attr_type in annotations.items():
                if attr in kwargs:
                    value = kwargs[attr]
                    if isinstance(value, Resource) and attr in cls.__dict__ and isinstance(cls.__dict__[attr], ClientBuilder):
                        instance_kwargs[attr] = value.get_client(attr_type, config_store=kwargs.get('config_store'), **cls.__dict__[attr].client_options)
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


class AzureApp(metaclass=AzureAppComponent):
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
        return cls(config_store=infra._config_store, **kwargs)
