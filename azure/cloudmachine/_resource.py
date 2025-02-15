# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# --------------------------------------------------------------------------

from __future__ import annotations

from inspect import get_annotations
import inspect
from itertools import takewhile, product, accumulate
from enum import Enum
from copy import deepcopy
from collections import defaultdict
import os
import json
from typing import (
    Generic,
    Mapping,
    Required,
    Tuple,
    TypedDict,
    runtime_checkable,
    Type,
    Optional,
    Callable,
    Union,
    Dict,
    List,
    Any,
    TypeVar,
    Literal,
    overload,
    NamedTuple,
    TYPE_CHECKING
)
from typing_extensions import Self

from dotenv import dotenv_values

from azure.core.credentials import (
    SupportsTokenInfo,
    AzureKeyCredential,
    AzureSasCredential,
    AzureNamedKeyCredential
)
from azure.core.credentials_async import AsyncSupportsTokenInfo
from azure.core.settings import PrioritizedSetting

from ._parameters import DEFAULT_NAME, LOCATION, AZD_TAGS
from ._setting import StoredPrioritizedSetting
from ._bicep.expressions import Guid, Output, Expression, Parameter, ResourceSymbol, ResourceGroup, UniqueString, Variable
from ._bicep.utils import serialize, generate_suffix, resolve_value, serialize_dict, clean_name

if TYPE_CHECKING:
    from .resources.resourcegroup import ResourceGroup
    from .resources._extension import RoleAssignment
    from ._component import AzureInfrastructure



class DefaultAction(Enum):
    MISSING = 'MISSING'
    BUILD_DEFAULT = 'BUILD_DEFAULT'


ClientType = TypeVar("ClientType")
CredentialTypes = Union[
    AsyncSupportsTokenInfo,
    SupportsTokenInfo,
    Callable[[], SupportsTokenInfo],
    Callable[[], AsyncSupportsTokenInfo],
    Literal['default', 'managedidentity'],
]


def _load_dev_environment(name: Optional[str] = None, label: Optional[str] = None) -> Dict[str, str]:
    azd_dir = os.path.join(os.getcwd(), ".azure")
    if name and not name.endswith('.env'):
        if not os.path.isdir(azd_dir):
            return {}
        env_name = name + (f"-{label}" if label else "")
        env_path = os.path.join(azd_dir, env_name, ".env")
    elif name:
        env_path = name
    else:
        scriptname = os.path.splitext(os.path.basename(inspect.stack()[-1][0].f_code.co_filename))[0]
        scriptenv = os.path.join(azd_dir, scriptname, ".env")
        if os.path.isdir(azd_dir) and os.path.isfile(scriptenv):
            env_path = scriptenv
        else:
            env_path = ".env"
    values = dotenv_values(env_path)
    return values


def _build_envs(services: List[str], attributes: List[str]) -> List[str]:
    all_vars = product(services, attributes)
    return ["_".join(['AZURE'] + list(var)).upper() for var in all_vars]


_EMPTY_DEFAULT = {}
_EMPTY_DEFAULT_EXTENSIONS = {}


class ResourceReference(TypedDict, total=False):
    name: Required[Union[str, Parameter[str]]]
    resource_group: 'ResourceGroup'
    subscription: Union[str, Parameter[str]]


class ExtensionResources(TypedDict, total=False):
    managed_identity_roles: Union[Parameter[List[Union['RoleAssignment', str]]], List[Union[Parameter[Union[str, 'RoleAssignment']], 'RoleAssignment', str]]]
    user_roles: Union[Parameter[List[Union['RoleAssignment', str]]], List[Union[Parameter[Union[str, 'RoleAssignment']], 'RoleAssignment', str]]]
    # lock
    # diagnostics
    # private endpoint
    # secret store


ResourcePropertiesType = TypeVar("ResourcePropertiesType", bound=dict[str, Any])

class FieldType(NamedTuple, Generic[ResourcePropertiesType]):
    resource: str
    version: str
    properties: ResourcePropertiesType
    symbol: ResourceSymbol
    outputs: Dict[str, Output]
    resource_group: ResourceSymbol
    extensions: ExtensionResources
    existing: bool
    name: Optional[Union[str, Parameter[str]]]
    add_defaults: Optional[Callable[[FieldType, Dict[str, Parameter]], None]]
    

FieldsType = Dict[str, FieldType]

class Resource(Generic[ResourcePropertiesType]):
    DEFAULTS: Mapping[str, Any] = _EMPTY_DEFAULT
    DEFAULT_EXTENSIONS = _EMPTY_DEFAULT_EXTENSIONS
    resource: str
    version: str
    name: PrioritizedSetting[str, str]
    id: PrioritizedSetting[str, str]
    subscription: PrioritizedSetting[str, str]
    properties: ResourcePropertiesType
    extensions: ExtensionResources

    def __init__(self, properties: Optional[Dict[str, Any]] = None, /, **kwargs) -> None:
        """This constructor should not be used directly."""
        self.properties: ResourcePropertiesType = properties or {}
        self.extensions: ExtensionResources = kwargs.pop('extensions', {})
        self.parent: Optional[Resource] = kwargs.pop('parent', None)
        self._resource: str = kwargs.pop('resource', "")
        self._subresource: Optional[str] = kwargs.pop('subresource', '')
        self._version: str = kwargs.pop('resource_version', "")
        self._suffix = ""
        self._properties_to_merge = ['properties']
        self._properties_to_update = ['tags']
        self._existing: bool = kwargs.pop('existing', False)
        self._prefixes: List[str] = kwargs.pop('service_prefix', [])
        self._default_action: DefaultAction = kwargs.pop('default_action', DefaultAction.BUILD_DEFAULT)
        self._supports_managed_identity: bool = False
        self._infra_objects: List[Type['AzureInfrastructure']] = []
        self._infra_attr_names: List[str] = []
        if self.parent and not self._subresource:
            raise ValueError('Parent must be specified with subresource.')
        if kwargs:
            raise TypeError(f"Resource {self.__class__.__name__} got unexpected kwargs: {list(kwargs.keys())}")

        self.name = StoredPrioritizedSetting(
            'name',
            env_vars=_build_envs(self._prefixes, ['NAME']),
        )
        if 'name' in self.properties:
            self.name.set_value(properties['name'])
        self.resource_id = StoredPrioritizedSetting(
            name='resource_id',
            env_vars=_build_envs(self._prefixes, ['ID', 'RESOURCE_ID']),
            system_hook=self._build_resource_id
        )
        self.subscription = StoredPrioritizedSetting(
            name='subscription_id',
            env_var='AZURE_SUBSCRIPTION_ID',
            system_hook=self._existing_subscription_id
        )
        self.resource_group = StoredPrioritizedSetting(
            name='resource_group',
            env_vars=_build_envs(self._prefixes, ['RESOURCE_GROUP']),
        )
        self._settings: Dict[str, StoredPrioritizedSetting] = {
            "name": self.name,
            "resource_id": self.resource_id,
            "subscription_id": self.subscription,
            "resource_group": self.resource_group,
        }

    def __eq__(self, value: Any) -> bool:
        """Resource comparison. Resource is the same if it's the same type and same name."""
        try:
            return value.resource == self.resource and value.properties.get('name') == self.properties.get('name')
        except:
            return False

    @property
    def resource(self) -> str:
        return self._resource

    @property
    def version(self) -> str:
        return self._version

    @property
    def infrastructure(self) -> Type['AzureInfrastructure']:
        try:
            return self._infra_objects[0]
        except IndexError:
            raise TypeError(f"Resource {repr(self)} has not been declared in an AzureInfrastructure class.")

    @classmethod
    def reference(
            cls,
            resource: str,
            *,
            name: Union[str, Parameter[str]],
            resource_group: Optional[Union[str, Parameter[str], 'ResourceGroup']] = None,
            subscription: Optional[Union[str, Parameter[str]]] = None,
            parent: Optional[Resource] = None,
    ) -> Self[ResourceReference]:
        if parent and resource_group:
            raise ValueError("Cannot specify both parent and resource_group.")
        resource_type, resource_version = resource.split('@')
        properties = ResourceReference(name=name)
        if resource_group:
            if isinstance(resource_group, (str, Parameter)):
                from .resources.resourcegroup import ResourceGroup
                resource_group = ResourceGroup.reference(name=resource_group, subscription=subscription)
            properties['resource_group'] = resource_group
        elif subscription:
            properties['subscription'] = subscription
        resource_ref = cls(
            properties,
            resource=resource_type,
            resource_version=resource_version,
            parent=parent,
            existing=True
        )
        resource_ref._set_suffix(name)
        if resource_group and resource_group.properties.get('name'):
            resource_ref.resource_group.set_value(resource_group.properties['name'])
        if subscription and isinstance(subscription, (str, Parameter)):
            resource_ref.subscription.set_value(subscription)
        return resource_ref

    def __repr__(self) -> str:
        name = self.properties.get('name', '<default>')
        return f"{self.__class__.__name__}('{name}')"

    def __set_name__(self, owner: Type, name: str) -> None:
        self._infra_objects.append(owner)
        self._infra_attr_names.append(name)

    def _add_attr(self, value: str) -> None:
        if value in self._infra_attr_names:
            return
        self._infra_attr_names.append(value)
        self._set_suffix(value)

    def _set_suffix(self, value: Union[str, Parameter] = None) -> None:
        if value:
            if isinstance(value, str):
                self._suffix = '_' + clean_name(value).upper()
            else:
                self._suffix = '_' + clean_name(value.value).upper()
            for setting in self._settings.values():
                setting.suffix = self._suffix
        elif self._infra_attr_names:
            self._suffix = '_' + self._infra_attr_names[0].upper()
            for setting in self._settings.values():
                setting.suffix = self._suffix

    def _existing_subscription_id(self) -> str:
        if self._existing and 'resource_group' in self.properties:
            return self.properties['resource_group'].subscription()
        raise RuntimeError("Existing resource group reference has no subscription specified.")

    def _build_resource_id(self) -> str:
        if not self._resource:
            raise ValueError("No resource specified.")
        if self.parent:
            return f"{self.parent._build_resource_id()}/{self._subresource}/{self.name()}"
        prefix = f"/subscriptions/{self.subscription()}/resourceGroups/{self.resource_group()}/providers/"
        return prefix + f"{self._resource}/{self.name()}"

    def set_config_store(self, config: Mapping[str, Any]) -> None:
        for setting in self._settings.values():
            setting.config_store = config
        if self.parent:
            self.parent.set_config_store(config)

    def _symbol(self) -> ResourceSymbol:
        if not self.resource:
            raise TypeError("Empty Resource object cannot be provisioned.")
        resource_ref = self.resource.split("/")[-1].lower()
        if resource_ref.endswith("ies"):
            resource_ref = resource_ref.rstrip("ies") + "y"
        else:
            resource_ref = resource_ref.rstrip('s')
        symbol = f"{resource_ref}{self._suffix.lower()}" if self._suffix else resource_ref
        principal_id = None
        if self.properties.get('identity', {}).get('type', "").startswith('SystemAssigned'):
            principal_id = "principalId"
        return ResourceSymbol(symbol, principal_id=principal_id)

    def _outputs(
            self,
             *,
             symbol: ResourceSymbol,
             **kwargs
    ) -> Dict[str, Output]:
        outputs = {
            'resource_id': Output(f"AZURE_{self._prefixes[0].upper()}_ID{self._suffix}", "id", symbol),
            'name': Output(f"AZURE_{self._prefixes[0].upper()}_NAME{self._suffix}", "name", symbol),
        }
        rg_output = f"AZURE_{self._prefixes[0].upper()}_RESOURCE_GROUP{self._suffix}"
        if self._existing and self.properties.get('resource_group'):
            outputs['resource_group'] = Output(rg_output, self.properties['resource_group'].properties['name'])
        else:
            outputs['resource_group'] = Output(rg_output, ResourceGroup().name)
        return outputs
    
    def _merge_properties(
            self,
            current_properties: Dict[str, Any],
            new_properties: Dict[str, Any],
            **kwargs
        ) -> Dict[str, Any]:
        for key, value in new_properties.items():
            if key in current_properties:
                if key in self._properties_to_merge:
                    self._merge_properties(current_properties[key], value)
                elif key in self._properties_to_update:
                    current_properties[key].update(value)
                elif current_properties[key] != value:
                    raise ValueError(f"{repr(self)} cannot set '{key}' to '{value}', already set to: '{current_properties[key]}'.")
            else:
                current_properties[key] = value
        return {}

    def _find_last_resource_match(
            self,
            fields: FieldsType,
            *,
            resource: Optional[str] = None,
            resource_group: Optional[ResourceSymbol] = None,
            name: Optional[Union[str, Expression]] = None,
    ) -> Optional[FieldType]:
        resource = resource or self.resource
        for field in (f for f in reversed(list(fields.values())) if f.resource == resource):
            if name and resource_group:
                if field.properties.get('name') == name and field.resource_group == resource_group:
                    return field
            elif resource_group:
                if field.resource_group == resource_group:
                    return field
            elif name:
                if field.properties.get('name') == name:
                    return field
            else:
                return field
        return None

    def _find_resource_group(
            self,
            fields: FieldsType,
            parameters: Dict[str, Parameter],
            *,
            name: Optional[str] = None,
            module_name: Optional[str] = None
    ) -> ResourceSymbol:
        match = self._find_last_resource_match(
            fields,
            resource="Microsoft.Resources/resourceGroups",
            name=name
        )
        if match:
            return match.symbol
        from .resources.resourcegroup import ResourceGroup
        if name:
            existing_rg = ResourceGroup.reference(name=name)
            return existing_rg.__bicep__(fields, parameters=parameters, module_name=module_name)
        default_rg = ResourceGroup()
        return default_rg.__bicep__(fields, parameters=parameters, module_name=module_name)

    def _find_identity(
            self,
            fields: FieldsType,
            parameters: Dict[str, Parameter],
            *,
            module_name: Optional[str] = None,
    ) -> Optional[ResourceSymbol]:
        match = self._find_last_resource_match(
            fields,
            resource="Microsoft.ManagedIdentity/userAssignedIdentities",
        )
        if match:
            return match.symbol
        from .resources.managedidentity import UserAssignedIdentity
        new_identity = UserAssignedIdentity()
        return new_identity.__bicep__(fields, parameters=parameters, module_name=module_name)

    def _add_parameters(self, obj: Dict[str, Any], parameters):
        for value in obj.values():
            if isinstance(value, Parameter) and value.name:
                parameters[value.name] = value
            else:
                # TODO: Support lists
                try:
                    self._add_parameters(value, parameters)
                    continue
                except (AttributeError, TypeError):
                    pass
                        
    def _add_defaults(self, field: FieldType, parameters: Dict[str, Parameter]):
        for key, value in self.DEFAULTS.items():
            if field.properties.get(key):
                if key in self._properties_to_merge or key in self._properties_to_update:
                    try:
                        updated_default = value.copy()
                        updated_default.update(field.properties[key])
                        field.properties[key] = updated_default
                    except AttributeError:
                        # We probably got an Expression
                        # TODO: support union operation.
                        pass
            else:
                field.properties[key] = value
        self._add_parameters(field.properties, parameters)
        if 'managed_identity_roles' not in field.extensions:
            field.extensions['managed_identity_roles'] = self.DEFAULT_EXTENSIONS.get('managed_identity_roles', [])
        if 'user_roles' not in field.extensions:
            field.extensions['user_roles'] = self.DEFAULT_EXTENSIONS.get('user_roles', [])

    def __bicep__(
            self,
            fields: FieldsType,
            *,
            parameters: Dict[str, Parameter],
            app_component: Optional[Type] = None,
            attrname: Optional[str] = None,
            module_name: Optional[str] = None,
    ) -> ResourceSymbol:
        field_id = self._infra_objects[0].__name__ if self._infra_objects else '__main__'
        self._set_suffix(attrname or self.properties.get('name', ''))
        extensions = defaultdict(list)
        extensions.update(self.extensions)

        # We only want to export the outputs if either this is a resource not nested inside an
        # infrastructure object, or if it's in the root infrastructure object.
        output_resource = False
        if not self._infra_objects or (app_component and app_component in self._infra_objects and attrname in self._infra_attr_names):
            output_resource = True

        if self._existing:
            properties = dict(self.properties)
            if self.parent:
                properties['parent'] = self.parent.__bicep__(
                    fields,
                    parameters=parameters,
                    app_component=app_component,
                    attrname=self._suffix,
                    module_name=module_name
                )
            if 'resource_group' in properties:
                rg = properties.pop('resource_group').__bicep__(fields, parameters=parameters, module_name=module_name)
                properties['scope'] = rg
            else:
                rg = self._find_resource_group(fields, parameters, module_name=module_name)
                properties['scope'] = rg
            symbol = self._symbol()
            outputs = self._outputs(
                symbol=symbol,
                attrname=self._suffix,
                resource_group=rg,
                **properties
            )
            self._add_parameters(properties, parameters)
            field = FieldType(
                resource=self.resource,
                properties=properties,
                symbol=symbol,
                outputs=outputs,
                resource_group=rg,
                version=self.version,
                extensions=extensions,
                existing=True,
                name=properties['name'],
                add_defaults=None
            )
            fields[f"{field_id}.{attrname if attrname else symbol.value}"] = field
            return symbol

        rg = self._find_resource_group(fields, parameters, module_name=module_name)
        identity = None
        if self._supports_managed_identity:
            identity = self._find_identity(fields, parameters, module_name=module_name)
        field = self._find_last_resource_match(fields, resource_group=rg, name=self.properties.get('name'))
        if not field and self._default_action == DefaultAction.MISSING:
            raise TypeError(f'Missing resource of type: {self.resource}')
        if field:
            params = field.properties
            symbol = field.symbol
            outputs = field.outputs
            if 'managed_identity_roles' in self.extensions:
                field.extensions['managed_identity_roles'].extend(extensions['managed_identity_roles'])
            if 'user_roles' in self.extensions:
                field.extensions['user_roles'].extend(extensions['user_roles'])
        else:
            params = {}
            if self.parent:
                params['parent'] = self.parent.__bicep__(
                    fields,
                    parameters=parameters,
                    app_component=app_component,
                    attrname=self._suffix,
                    module_name=module_name
                )
            symbol = self._symbol()
            outputs = {}
            field = FieldType(
                resource=self.resource,
                properties=params,
                symbol=symbol,
                outputs=outputs,
                resource_group=rg,
                version=self.version,
                extensions=extensions,
                existing=False,
                name=self.properties.get('name'),
                add_defaults=self._add_defaults
            )
            fields[f"{field_id}.{self._infra_attr_names[-1] if self._infra_attr_names else symbol.value}"] = field

        output_config = self._merge_properties(
            params,
            self.properties,
            fields=fields,
            parameters=parameters,
            symbol=symbol,
            attrname=attrname,
            resource_group=rg,
            identity=identity,
        )
        if not outputs and output_resource:
            resource_outputs = self._outputs(
                symbol=symbol,
                attrname=attrname,
                resource_group=rg,
                parent=params.get('parent'),
                **output_config
            )
            outputs.update(resource_outputs)
        self._add_parameters(field.properties, parameters)
        # TODO: this wont really work yet
        # self._add_parameters(field.extensions, parameters)
        return symbol


    @overload
    def __call__(
        self,
        cls: Callable[..., ClientType],  # TODO: Needs protocol for from_resource
        /,
        *,
        options: Optional[Dict[str, Any]] = None,
        config_store: Optional[Mapping[str, Any]] = None,
        env_name: Optional[str] = None,
    ) -> ClientType:
        ...
    @overload
    def __call__(self, *, config_store: Optional[Mapping[str, Any]] = None, env_name: Optional[str] = None) -> Self:
        ...
    def __call__(self, cls=None, /, *, options=None, config_store=None, env_name=None, **kwargs):
        self._set_suffix(self._infra_attr_names[0] if self._infra_attr_names else self.properties.get('name', ''))
        if config_store is not None:
            self.set_config_store(config_store)
        elif env_name:
           self.set_config_store(_load_dev_environment(env_name))
        elif not self._settings['resource_id'].config_store:
            self.set_config_store(_load_dev_environment())
        if cls in [None, self.__class__]:
            return self
        elif hasattr(cls, 'from_resource'):
            return cls.from_resource(self, **options or {})
        elif hasattr(cls, '_from_resource'):
            return cls._from_resource(self, **options or {})
        raise TypeError(f"Unsupported type '{cls.__name__}' for resource '{self.__class__.__name__}'.")


class _ClientResource(Resource[ResourcePropertiesType]):
    endpoint: PrioritizedSetting[str, str]
    client_options: PrioritizedSetting[Dict[str, Any], Dict[str, Any]]
    audience: PrioritizedSetting[str, str]
    credential: PrioritizedSetting[CredentialTypes, CredentialTypes]
    api_version: PrioritizedSetting[str, str]

    def __init__(self, properties=None, /, **kwargs) -> None:
        super().__init__(properties, **kwargs)
        self.audience = StoredPrioritizedSetting(
            name='audience',
            env_vars=_build_envs(self._prefixes, ['AUDIENCE']),
        )
        self._settings['audience'] = self.audience
        self.endpoint = StoredPrioritizedSetting(
            name='endpoint',
            env_vars=_build_envs(self._prefixes, ['ENDPOINT']),
            system_hook=self._build_endpoint
        )
        self._settings['endpoint'] = self.endpoint
        self.api_version = StoredPrioritizedSetting(
            name='api_version',
            env_vars=_build_envs(self._prefixes, ['API_VERSION']),
        )
        self._settings['api_version'] = self.api_version
        self.client_options = StoredPrioritizedSetting(
            name='client_options',
            default={},
        )
        self._settings['client_options'] = self.client_options
        self.credential = StoredPrioritizedSetting(
            name='credential',
            default='default',
        )
        self._settings['credential'] = self.credential

    def _build_endpoint(self) -> str:
        raise NotImplementedError()

    def _build_credential(self, use_async: bool) -> Union[SupportsTokenInfo, AsyncSupportsTokenInfo]:
        value = self.credential()
        try:
            value = value.lower()
            if value == 'default':
                if use_async:
                    from azure.identity.aio import DefaultAzureCredential
                else:
                    from azure.identity import DefaultAzureCredential
                credential = DefaultAzureCredential()
                self.credential.set_value(credential)
                return credential
            if value == 'managedidentity':
                if use_async:
                    from azure.identity.aio import ManagedIdentityCredential
                else:
                    from azure.identity import ManagedIdentityCredential
                credential = ManagedIdentityCredential()
                self.credential.set_value(credential)
                return credential
        except AttributeError:
            pass
        try:
            constructed_value = value()
            self.credential.set_value(constructed_value)
            return constructed_value
        except TypeError:
            if isinstance(value, (SupportsTokenInfo, AsyncSupportsTokenInfo)):
                self.credential.set_value(value)
                return value
        raise ValueError(f'Cannot convert {value} to credential type.')

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
            return super().__call__(cls, options=options, config_store=config_store, env_name=env_name)
        except TypeError:
            pass
        kwargs = {}
        endpoint = self.endpoint()
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
        client = cls(endpoint, **kwargs)
        client.__resource_settings__ = self
        return client
