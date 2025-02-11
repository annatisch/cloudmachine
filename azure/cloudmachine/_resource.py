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
    from .resources._utils import RoleAssignment as SimpleRoleAssignment



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


class ResourceReference(TypedDict, total=False):
    name: Required[Union[str, Parameter[str]]]
    resource_group: 'ResourceGroup'
    subscription: Union[str, Parameter[str]]


class ExtensionResources(TypedDict, total=False):
    role_assignments: Union[Parameter[List[Union['SimpleRoleAssignment', str]]], List[Union[Parameter[Union[str, 'SimpleRoleAssignment']], 'SimpleRoleAssignment', str]]]
    user_role: Union[Union['SimpleRoleAssignment', str], Parameter[Union['SimpleRoleAssignment', str]]]
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
    outputs: List[Output]
    resource_group: ResourceSymbol
    extensions: ExtensionResources
    existing: bool
    name: Optional[Union[str, Parameter[str]]]
    add_defaults: Optional[Callable[[FieldType, Dict[str, Parameter]], None]]
    

FieldsType = Dict[str, FieldType]

class Resource(Generic[ResourcePropertiesType]):
    DEFAULTS: Mapping[str, Any] = _EMPTY_DEFAULT
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
        self._parent: Optional[Resource] = kwargs.pop('parent', None)
        self._resource: str = kwargs.pop('resource', "")
        self._subresource: Optional[str] = kwargs.pop('subresource', '')
        self._version: str = kwargs.pop('resource_version', "")
        self._suffix = ""
        self._existing: bool = kwargs.pop('existing', False)
        self._prefixes: List[str] = kwargs.pop('service_prefix', [])
        self._default_action: DefaultAction = kwargs.pop('default_action', DefaultAction.BUILD_DEFAULT)
        self._supports_managed_identity: bool = False
        self._project_objects: List[Type] = []
        self._project_attr_names: List[str] = []
        if self._parent and not self._subresource:
            raise ValueError('Parent must be specified with subresource.')
        if kwargs:
            raise TypeError(f"Resource {self.__class__.__name__} got unexpected kwargs: {list(kwargs.keys())}")

        self.name = StoredPrioritizedSetting(
            'name',
            env_vars=_build_envs(self._prefixes, ['NAME']),
        )
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

    @classmethod
    def reference(
            cls,
            resource: str,
            *,
            name: str,
            resource_group: Optional[Union[str, 'ResourceGroup']] = None,
            subscription: Optional[str] = None,
            parent: Optional[Resource] = None,
    ) -> Self[ResourceReference]:
        if parent and resource_group:
            raise ValueError("Cannot specify both parent and resource_group.")
        resource_type, resource_version = resource.split('@')
        properties = ResourceReference(name=name)
        if resource_group:
            if isinstance(resource_group, str):
                from .resources.resourcegroup import ResourceGroup
                resource_group = ResourceGroup.reference(name=resource_group, subscription=subscription)
            properties['resource_group'] = resource_group
        elif subscription:
            properties['subscription'] = str(subscription)
        resource_ref = cls(
            properties,
            resource=resource_type,
            resource_version=resource_version,
            parent=parent,
            existing=True
        )
        resource_ref._set_suffix(name)
        resource_ref.name.set_value(name)
        if resource_group and isinstance(resource_group.properties['name'], str):
            resource_ref.resource_group.set_value(resource_group.properties['name'])
        if subscription and isinstance(subscription, str):
            resource_ref.subscription.set_value(subscription)
        return resource_ref

    def __repr__(self) -> str:
        name = self.properties.get('name', '<default>')
        return f"{self.__class__.__name__}('{name}')"

    def __set_name__(self, owner: Type, name: str) -> None:
        self._project_objects.append(owner)
        self._project_attr_names.append(name)

    def _add_attr(self, value: str) -> None:
        if value in self._project_attr_names:
            return
        self._project_attr_names.append(value)
        self._set_suffix(value)

    def _set_suffix(self, value: Union[str, Parameter]) -> None:
        if value:
            if isinstance(value, str):
                self._suffix = '_' + clean_name(value).upper()
            else:
                self._suffix = '_' + clean_name(value.value).upper()
            for setting in self._settings.values():
                setting.suffix = self._suffix

    def _existing_subscription_id(self) -> str:
        if self._existing and 'resource_group' in self.properties:
            return self.properties['resource_group'].subscription()
        raise RuntimeError("Existing resource group reference has no subscription specified.")

    def _build_resource_id(self) -> str:
        if not self._resource:
            raise ValueError("No resource specified.")
        if self._parent:
            return f"{self._parent._build_resource_id()}/{self._subresource}/{self.name()}"
        prefix = f"/subscriptions/{self.subscription()}/resourceGroups/{self.resource_group()}/providers/"
        return prefix + f"{self._resource}/{self.name()}"

    def add_config_store(self, config: Mapping[str, Any], position: Literal['first', 'last'] = 'first') -> None:
        if position == 'first':
            for setting in self._settings.values():
                setting.config_stores.insert(0, config)
        else:
            for setting in self._settings.values():
                setting.config_stores.append(config)

    def _symbol(self) -> ResourceSymbol:
        if not self.resource:
            raise TypeError("Empty Resource object cannot be provisioned.")
        # resource_ref = self.resource.split("/")[0].split(".")[1]
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
    ) -> List[Output]:
        outputs = [
            Output(f"AZURE_{self._prefixes[0].upper()}_ID{self._suffix}", "id", symbol),
            Output(f"AZURE_{self._prefixes[0].upper()}_NAME{self._suffix}", "name", symbol),
        ]
        rg_output = f"AZURE_{self._prefixes[0].upper()}_RESOURCE_GROUP{self._suffix}"
        if self._existing and self.properties.get('resource_group'):
            outputs.append(Output(rg_output, self.properties['resource_group'].properties['name']))
        else:
            outputs.append(Output(rg_output, ResourceGroup().name))
        return outputs
    
    def _merge_properties(
            self,
            properties: Dict[str, Any],
            **kwargs
        ) -> Dict[str, Any]:
        for key, value in self.properties.items():
            if properties.get(key) and properties[key] != value:
                raise ValueError(f"{repr(self)} cannot set '{key}' to '{value}', already set to: '{properties[key]}'.")
            properties[key] = value
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
            name: Optional[str] = None
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
            return existing_rg.__bicep__(fields, parameters=parameters)
        default_rg = ResourceGroup()
        return default_rg.__bicep__(fields, parameters=parameters)

    def _find_identity(
            self,
            fields: FieldsType,
            parameters: Dict[str, Parameter],
    ) -> Optional[ResourceSymbol]:
        match = self._find_last_resource_match(
            fields,
            resource="Microsoft.ManagedIdentity/userAssignedIdentities",
        )
        if match:
            return match.symbol
        from .resources.managedidentity import UserAssignedIdentity
        new_identity = UserAssignedIdentity()
        return new_identity.__bicep__(fields, parameters=parameters)

    def _build_role_assignment(
            self,
            role: Union[str, 'SimpleRoleAssignment'],
            fields: FieldsType,
            name: Union[str, Parameter[str]],
            *,
            parameters: Dict[str, Parameter],
            symbol: ResourceSymbol,
            principal_id: Expression,
            principal_type: Literal['ServicePrincipal', 'User']
    ) -> ResourceSymbol:
        from .resources._extension.roles import RoleAssignment
        if isinstance(role, str):
            new_role = RoleAssignment(
                {
                    'name': Guid(self.__class__.__name__, name, principal_type, role),
                    'properties': {
                        'principalId': principal_id,
                        'principalType': principal_type,
                        'roleDefinitionId': role
                    },
                    'scope': symbol
                }
            )
            return new_role.__bicep__(fields, parameters=parameters)
        else:
            new_role = RoleAssignment(
                {
                    'name': role.get(
                        'name',
                        Guid(
                            self.__class__.__name__,
                            name,
                            role['principalId'],
                            role['roleDefinitionIdOrName']
                        )
                    ),
                    'properties': {
                        'condition': role.get('condition'),
                        'conditionVersion': role.get('conditionVersion'),
                        'delegatedManagedIdentityResourceId': role.get('delegatedManagedIdentityResourceId'),
                        'description': role.get('description'),
                        'principalType': role.get('principalType'),
                        'roleDefinitionId': role.get('roleDefinitionIdOrName')
                    },
                    'scope': symbol
                }
            )
            return new_role.__bicep__(fields, parameters=parameters)
    
    def _add_role_assignments(
            self,
            fields: FieldsType,
            properties: Dict[str, Any],
            *,
            extensions: Dict[str, Any],
            parameters: Dict[str, Parameter],
            symbol: ResourceSymbol,
            identity: Optional[ResourceSymbol],
            user_access: bool,
    ) -> None:
        if identity:
            for role in self.extensions.get('role_assignments', []):
                if not extensions.get('role_assignments'):
                    extensions['role_assignments'] = []
                role_symbol = self._build_role_assignment(
                    role,
                    fields,
                    properties.get('name', parameters['defaultName']),
                    parameters=parameters,
                    symbol=symbol,
                    principal_id=identity.principal_id,
                    principal_type='ServicePrincipal'
                )
                if role_symbol not in extensions['role_assignments']:
                    extensions['role_assignments'].append(role_symbol)
                
        if self.extensions.get('user_role') and user_access:
            if not extensions.get('user_roles'):
                extensions['user_roles'] = []
            role_symbol = self._build_role_assignment(
                self.extensions['user_role'],
                fields,
                properties.get('name', parameters['defaultName']),
                parameters=parameters,
                symbol=symbol,
                principal_id=parameters['principalId'],
                principal_type='User'
            )
            if role_symbol not in extensions['user_roles']:
                extensions['user_roles'].append(role_symbol)

    def _update_managed_identities(
            self,
            properties: Dict[str, Any],
            *,
            identity: Optional[ResourceSymbol] = None
    ) -> None:
        if identity and self._supports_managed_identity:
            if 'identity' not in properties:
                properties['identity'] = {
                    'type': 'UserAssigned',
                    'userAssignedIdentities': {identity: {}}
                }
            else:
                identities = properties['identity'].get('userAssignedIdentities', {})
                if identity not in identities:
                    identities[identity] = {}
                if properties['identity']['type'] == 'None':
                    properties['identity']['type'] = 'UserAssigned'
                elif properties['identity']['type'] == 'SystemAssigned':
                    properties['identity']['type'] = 'SystemAssigned,UserAssigned'
                properties['identity']['userAssignedIdentities'] = identities

    def _add_parameters(self, obj: Dict[str, Any], parameters):
        for value in obj.values():
            if isinstance(value, Parameter) and value.name:
                parameters[value.name] = value
            else:
                try:
                    self._add_parameters(value, parameters)
                except (AttributeError, TypeError):
                    pass

    def _add_defaults(self, field: FieldType, parameters: Dict[str, Parameter]):
        if 'name' not in field.properties:
            field.properties['name'] = DEFAULT_NAME
        if 'location' not in field.properties:
            field.properties['location'] = LOCATION
        if 'tags' not in field.properties:
            field.properties['tags'] = AZD_TAGS
        #field.name = field.properties['name']

    def __bicep__(
            self,
            fields: FieldsType,
            *,
            parameters: Dict[str, Parameter],
            app_component: Optional[Type] = None,
            attrname: Optional[str] = None
    ) -> ResourceSymbol:
        field_id = self._project_objects[0].__name__ if self._project_objects else '__main__'
        self._set_suffix(attrname or self.properties.get('name', ''))

        # We only want to add user access and export the outputs if either this is a resource not nested inside a
        # project object, or if it's in the root project object.
        output_resource = False
        if not self._project_objects or (app_component and app_component in self._project_objects and attrname in self._project_attr_names):
            output_resource = True
        
        # If the resource has a parent - add that to the fields first.
        parent: Optional[ResourceSymbol] = None
        if self._parent:
            parent = self._parent.__bicep__(
                fields,
                parameters=parameters,
                app_component=app_component,
                attrname=self._suffix
            )

        if self._existing:
            properties = dict(self.properties)
            if parent:
                properties['scope'] = parent
            if 'resource_group' in properties:
                rg = properties.pop('resource_group').__bicep__(fields, parameters=parameters)
                properties['scope'] = rg
            else:
                rg = self._find_resource_group(fields, parameters)
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
                extensions={},  # TODO: support adding role assignments to existing resources
                existing=True,
                name=properties['name'],
                add_defaults=None
            )
            fields[f"{field_id}.{attrname if attrname else symbol.value}"] = field
            return symbol

        rg = self._find_resource_group(fields, parameters)
        identity = self._find_identity(fields, parameters)
        field = self._find_last_resource_match(fields, resource_group=rg, name=self.properties.get('name'))
        if not field and self._default_action == DefaultAction.MISSING:
            raise TypeError(f'Missing resource of type: {self.resource}')
        if field:
            params = field.properties
            symbol = field.symbol
            outputs = field.outputs
        else:
            params = dict(self.DEFAULTS)
            symbol = self._symbol()
            outputs = []
            field = FieldType(
                resource=self.resource,
                properties=params,
                symbol=symbol,
                outputs=outputs,
                resource_group=rg,
                version=self.version,
                extensions={},
                existing=False,
                name=self.properties.get('name'),
                add_defaults=self._add_defaults
            )
            fields[f"{field_id}.{self._project_attr_names[-1] if self._project_attr_names else symbol.value}"] = field

        output_config = self._merge_properties(
            params,
            fields=fields,
            parameters=parameters,
            identity=identity,
            symbol=symbol,
            attrname=attrname,
            resource_group=rg
        )
        self._add_role_assignments(
            fields,
            params,
            parameters=parameters,
            symbol=symbol,
            identity=identity,
            extensions=field.extensions,
            user_access=(output_resource and parameters.get('principalId'))
        )
        self._update_managed_identities(params, identity=identity)
        if not outputs and output_resource:
            resource_outputs = self._outputs(
                symbol=symbol,
                attrname=attrname,
                resource_group=rg,
                **output_config
            )
            outputs.extend(resource_outputs)
        self._add_parameters(field.properties, parameters)
        self._add_parameters(field.extensions, parameters)
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
        if not isinstance(self._default, DefaultAction):
            raise NotImplementedError()
        if self._default_factory:
            return self._default_factory(self.properties)
        if config_store:
            self.add_config_store(config_store)
        elif env_name:
           self.add_config_store(_load_dev_environment(env_name))
        elif not self._settings['id'].config_stores:
            self.add_config_store(_load_dev_environment())
        if cls is None:
            return self
        elif hasattr(cls, 'from_resource'):
            return cls.from_resource(self, **options or {})
        elif hasattr(cls, '_from_resource'):
            return cls._from_resource(self, **options or {})
        raise TypeError(f"Unsupported type '{cls.__name__}' for resource '{self.__class__.__name__}'.")


class _ClientResource(Resource):
    endpoint: PrioritizedSetting[str, str]
    client_options: PrioritizedSetting[Dict[str, Any], Dict[str, Any]]
    audience: PrioritizedSetting[str, str]
    credential: PrioritizedSetting[CredentialTypes, CredentialTypes]
    api_version: PrioritizedSetting[str, str]

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
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
