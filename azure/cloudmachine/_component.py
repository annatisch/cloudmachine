from inspect import get_annotations
from typing import (
    TYPE_CHECKING,
    Mapping,
    Protocol,
    Self,
    dataclass_transform,
    overload,
    TypeVar,
    Any, Union, Literal, Optional, Callable, Dict, List, Type, Unpack
)

from ._bicep.expressions import Parameter, MISSING, Default
from ._resource import Resource, _load_dev_environment, ResourceReference
from .resources._identifiers import ResourceIdentifiers
from .resources.resourcegroup import ResourceGroup
from .resources.managedidentity import UserAssignedIdentity

if TYPE_CHECKING:
    from .resources.resourcegroup.types import ResourceGroupResource
    from .resources.managedidentity.types import UserAssignedIdentityResource


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

class DefaultFactory(Protocol):
    def __call__(self, **kwargs) -> Any:
        ...


class ComponentField(Parameter[Any]):
    def __init__(
            self,
            *,
            default: Any,
            factory: Union[Literal[Default.MISSING], DefaultFactory],
            repr: bool,
            init: bool,
            alias: Optional[str],
            **kwargs
    ):
        self._factory = factory
        self._kwargs = kwargs
        self._default = default
        self._repr = repr
        self._init = init
        self._alias = alias
        self._owner: Optional[Type] = None
        self._attrname: Optional[str] = None
        self._name: Optional[str] = None
        self.module = "main"  # TODO: refactor this away

    @property
    def name(self) -> str:
        if not self._owner or not self._name:
            raise ValueError("ComponentField not used in component class.")
        return f"{self._owner.__name__}.{self._name}"

    @property
    def default(self) -> Any:
        return self._default   
        
    def __repr__(self) -> str:
        if self._default is not MISSING:
            return f"FieldComponent(default={repr(self._default)})"
        if self._factory is not MISSING:
            return f"FieldComponent(default={self._factory._name_}(**kwargs))"
        return "FieldComponent()"

    def __set_name__(self, owner: Type, name: str) -> None:
        self._owner = owner
        self._name = name
        self._attrname = '_' + name
        try:
            self._type = get_annotations(owner)[name]
        except KeyError:
            raise RuntimeError(f"'{owner.__name__}.{name}' is missing type hint.") from None

    def __get__(self, obj, obj_type):
        if obj is None:
            if self._default is not MISSING:
                return self._default
            if self._factory is not MISSING:
                return self._factory(**self._kwargs)
            raise AttributeError(f"No default value provided for '{self._owner.__name__}.{self._name}'.")
        return getattr(obj, self._attrname)

    def __set__(self, obj, value):
        setattr(obj, self._attrname, value)

    def get(self, obj = None, /) -> Any:
        return self.__get__(obj, obj.__class__)


def field(
        *,
        default: Union[Any, Literal[Default.MISSING]] = MISSING,
        factory: Union[DefaultFactory, Literal[Default.MISSING]] = MISSING,
        repr: bool = True,
        init: bool = True,
        alias: Optional[str] = None,
        **kwargs
) -> ComponentField:
    if default is not MISSING and factory is not MISSING:
        raise ValueError("Cannot specify both 'default' and 'default_factory'.")
    return ComponentField(
        default=default,
        factory=factory,
        repr=repr,
        init=init,
        alias=alias,
        **kwargs
    )


def _parameter(*, default = None, default_factory = None, **kwargs):
    # TODO not sure how we should handle this yet
    if default:
        return default
    if default_factory:
        return default_factory()
    return None


@dataclass_transform(field_specifiers=(field, _parameter), kw_only_default=True)
class AzureInfraComponent(type):
    # TODO: The typing of the __call__ function is breaking
    # typing when kwargs are passed into the constructor.
    # Need to figure that out.....
    def __call__(cls, **kwargs):
        instance_kwargs = {}
        missing_kwargs = []
        mro = cls.mro()
        # We want to skip objects in the heirachy above AzureInfrastructure, which should
        # only be 'object', but just in case that changes, we'll strip everything.
        for cls_type in reversed(mro[:mro.index(AzureInfrastructure) + 1]):
            for attr in get_annotations(cls_type):
                try:
                    try:
                        instance_kwargs[attr] = kwargs.pop(attr)
                    except KeyError:
                        instance_kwargs[attr] = getattr(cls, attr)
                    if attr in missing_kwargs:
                        missing_kwargs.pop(missing_kwargs.index(attr))
                except AttributeError:
                    missing_kwargs.append(attr)
        if kwargs:
            argument = "argument" if len(missing_kwargs) == 1 else "arguments"
            args = ', '.join([f"'{arg}'" for arg in kwargs])
            raise TypeError(f"{cls.__name__} got unexpected keyword {argument}: {args}")
        if missing_kwargs:
            argument = "argument" if len(missing_kwargs) == 1 else "arguments"
            attrs = ', '.join([f"'{attr}'" for attr in missing_kwargs])
            raise TypeError(f"{cls.__name__} missing required keyword {argument}: {attrs}.")
        kwargs.update(instance_kwargs)
        return super().__call__(**kwargs)


class AzureInfrastructure(metaclass=AzureInfraComponent):
    resource_group: ResourceGroup = field(default=ResourceGroup(), repr=False)
    identity: Optional[UserAssignedIdentity] = field(default=UserAssignedIdentity(), repr=False)

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self) -> str:
        attrs = []
        for attr in get_annotations(self.__class__):
            try:
                in_repr = self.__class__.__dict__[attr]._repr
                if in_repr:
                    attrs.append(f"{attr}={repr(getattr(self, attr))}")
            except (KeyError, AttributeError):
                attrs.append(f"{attr}={repr(getattr(self, attr))}")
        repr_str = ", ".join(attrs)
        return f"{self.__class__.__name__}({repr_str})"

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
    def from_infra(cls, infra: Union[AzureInfrastructure], /, config_store: Optional[Mapping[str, Any]] = None) -> Self:
        infra_resources = {r.identifier: r for r in infra.__dict__.values() if isinstance(r, Resource)}
        app_resources = {attr: value for attr, value in cls.__dict__.items() if isinstance(value, ClientBuilder)}
        kwargs = {}
        for key, value in app_resources.items():
            app_resource = CLIENT_BY_ANNOTATION[value.client_cls.__name__]
            if app_resource in infra_resources:
                kwargs[key] = infra_resources[app_resource]
        return cls(config_store=config_store, **kwargs)
