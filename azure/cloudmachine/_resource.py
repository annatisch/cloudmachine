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
import os
import json
from typing import (
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

from ._setting import StoredPrioritizedSetting
from ._bicep.expressions import Guid, ModuleSymbol, Output, Expression, Parameter, ResourceGroupSymbol, ResourceSymbol, Subscription, UniqueString, Variable
from ._bicep.utils import serialize, generate_suffix, resolve_value, serialize_dict, clean_name

if TYPE_CHECKING:
    from .resources.resourcegroup._resource import ResourceGroup


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

class ResourceReference(TypedDict, total=False):
    name: Required[str]
    scope: ResourceGroup
    parent: ResourceSymbol


class FieldType(NamedTuple):
    resource: str
    params: Dict[str, Any]
    symbol: ResourceSymbol
    outputs: Dict[str, Union[str, Output]]
    resource_group: ResourceGroupSymbol
    version: str

FieldsType = Dict[str, FieldType]


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


class Resource:
    identifier: str = ""
    module: str = ""
    DEFAULTS: Mapping[str, Any] = _EMPTY_DEFAULT
    resource: str
    module: str
    version: str
    tag: str
    name: PrioritizedSetting[str, str]
    id: PrioritizedSetting[str, str]
    subscription: PrioritizedSetting[str, str]
    properties: Mapping[str, Any]
    component: Type
    attr: str

    def __init__(self, **kwargs) -> None:
        """This constructor should not be used directly."""
        self.properties: Dict[str, Any] = kwargs.pop('properties', {})
        self._resource = ""
        self._version = ""
        self._prefixes: List[str] = kwargs.pop('service_prefix', [])
        self._default = kwargs.pop('default', DefaultAction.BUILD_DEFAULT)
        self._default_factory: Optional[Callable[[Dict[str, Any]], Any]] = kwargs.pop('default_factory', None)
        self._supports_managed_identity = False
        self._existing = False
        self._reference: Optional[ResourceReference] = None

        self._suffix = generate_suffix(5)
        self._component: Optional[Type] = None
        self._component_attr: Optional[str] = None
        self._apps: List[str] = []
        self._attrs: List[str] = []
        self._inferred_resource: Optional[str] = None
        self._inferred_reference: Optional[str] = None
        self._inferred_obj: Optional[Resource] = None

        self._args = kwargs.pop('args', [])
        self._kwargs = kwargs.pop('kwargs', {})
        if kwargs:
            raise TypeError(f"Resource {self.__class__.__name__} got unexpected kwargs: {list(kwargs.keys())}")

        self.name = StoredPrioritizedSetting(
            'name',
            env_vars=_build_envs(self._prefixes, ['NAME']),
        )
        self.id = StoredPrioritizedSetting(
            name='resource_id',
            env_vars=_build_envs(self._prefixes, ['ID', 'RESOURCE_ID']),
            system_hook=self._build_resource_id
        )
        self.subscription = StoredPrioritizedSetting(
            name='subscription_id',
            env_var='AZURE_SUBSCRIPTION_ID',
        )
        self.resource_group = StoredPrioritizedSetting(
            name='resource_group',
            env_vars=_build_envs(self._prefixes, ['RESOURCE_GROUP']),
        )
        self._settings: Dict[str, StoredPrioritizedSetting] = {
            "name": self.name,
            "id": self.id,
            "subscription_id": self.subscription,
            "resource_group": self.resource_group,
        }

    @overload
    @classmethod
    def reference(cls, resource_id: str, /) -> Self:
        ...
    @overload
    @classmethod
    def reference(
        cls,
        *,
        resource: str,
        name: str,
        resource_group: Optional[Union[str, 'ResourceGroup']] = None,
        subscription: Optional[str] = None,
    ) -> Self:
        ...
    @classmethod
    def reference(
            cls,
            resource_id: Optional[str] = None,
            *,
            resource: Optional[str] = None,
            name: Optional[str] = None,
            resource_group: Optional[Union[str, 'ResourceGroup']] = None,
            subscription: Optional[str] = None,
            parent: Optional[Resource] = None,
    ) -> Self:
        if resource_id:
            # We got resource ID.
            raise NotImplementedError("TODO: Parse resource ID")
        properties = ResourceReference(name=name)
        if parent:
            properties['parent'] = parent
        if resource_group:
            if isinstance(resource_group, str):
                from .resources.resourcegroup._resource import ResourceGroup
                resource_group = ResourceGroup.reference(name=resource_group, subscription=subscription)
            properties['scope'] = resource_group

        resource_ref = cls({})
        resource_ref.name.set_value(name)
        if resource_group:
            resource_ref.resource_group.set_value(resource_group._reference['name'])
        if subscription:
            resource_ref.subscription.set_value(subscription)
        resource_ref._reference = properties
        resource_type, resource_version = resource.split('@')
        resource_ref._resource = resource_type
        resource_ref._version = resource_version
        resource_ref._existing = True
        suffix = '_' + clean_name(name).upper()
        resource_ref._append_suffix(suffix)
        return resource_ref

    @classmethod
    def _from_inferred_resource(cls, *args, **kwargs):
        return cls(
            properties={},
            service_prefix=[],
            args=args,
            kwargs=kwargs,
        )

    def __repr__(self) -> str:
        if self._reference:
            name = self._reference['name']
        else:
            name = self.properties.get('name', '<default>')
        return f"{self.__class__.__name__}('{name}')"

    def __set_name__(self, owner: Type, name: str) -> None:
        self.attr = name
        if self._component is None:
            if not self.resource:
                from .resources import RESOURCE_BY_ANNOTATION
                try:
                    annotation = get_annotations(owner)[name]
                except KeyError:
                    raise RuntimeError(f"Resource '{name}' is missing type hint or resource identifier.") from None
                self._inferred_resource = RESOURCE_BY_ANNOTATION[annotation.__name__].identifier
        self.component = owner

    def __get__(self, *args) -> Self:
        if self._inferred_obj:
            return self._inferred_obj
        if self._inferred_resource:
            from ._component import resource, reference
            inferred_resource = resource(
                self._inferred_resource,
                *self._args,
                **self._kwargs
            )
            inferred_resource._append_suffix(self._get_suffix())
            inferred_resource._component = self._component
            inferred_resource._component_attr = self._component_attr
            inferred_resource._apps = self._apps
            inferred_resource._attrs = self._attrs
            inferred_resource._suffix = self._suffix
            self._inferred_obj = inferred_resource
            return inferred_resource
        return self

    @property
    def resource(self) -> str:
        return self._resource

    @property
    def version(self) -> str:
        return self._version

    @property
    def tag(self) -> str:
        return ""

    @property
    def component(self) -> Type:
        if not self._component:
            raise ValueError("Resource not declared within a CloudMachine component.")
        return self._component
    
    @component.setter
    def component(self, value: Type) -> None:
        if value not in self._apps:
            self._apps.append(value)
        if not self._component:
            self._component = value

    @property
    def attr(self) -> str:
        if not self._component_attr:
            raise ValueError("Resource not declared within a CloudMachine component.")
        return self._component_attr

    @attr.setter
    def attr(self, value: str) -> None:
        if value not in self._attrs:
            self._attrs.append(value)
            suffix = clean_name(value).upper()
            self._append_suffix('_' + suffix)
        if not self._component_attr:
            self._component_attr = value

    def _build_resource_id(self) -> str:
        raise NotImplementedError()

    def add_config_store(self, config: Mapping[str, Any], position: Literal['first', 'last'] = 'first') -> None:
        if position == 'first':
            for setting in self._settings.values():
                setting.config_stores.insert(0, config)
        else:
            for setting in self._settings.values():
                setting.config_stores.append(config)

    def _append_suffix(self, suffix: str) -> None:
        for setting in self._settings.values():
            setting.suffix = suffix

    def _get_suffix(self) -> str:
        return self._settings['id'].suffix

    def _symbol(self) -> ResourceSymbol:
        if not self.resource:
            raise TypeError("Empty Resource object cannot be provisioned.")
        resource_ref = self.resource.split("/")[0].split(".")[1]
        symbol = f"{resource_ref.lower()}_{self._suffix}"
        pid = None
        if self.module and not self._existing:
            if self.properties.get('managedIdentities', {}).get('systemAssigned', False):
                pid = "outputs.systemAssignedMIPrincipalId"
            return ModuleSymbol(symbol, principal_id=pid)
        if self.properties.get('identity', {}).get('type', "").startswith('SystemAssigned'):
            pid = "principalId"
        return ResourceSymbol(symbol, principal_id=pid)
    
    def _outputs(
            self,
             *,
             symbol: ResourceSymbol,
             attrname: Optional[str],
             resource_group: Optional[ResourceGroupSymbol],
             **kwargs
    ) -> Dict[str, Output]:
        suffix = clean_name(attrname or self.properties.get('name', '')).upper()
        suffix = ('_' + suffix) if suffix else suffix
        self._append_suffix(suffix)
        is_module = bool(self.module) and not self._existing
        outputs = {
            f"AZURE_{self._prefixes[0].upper()}_ID{suffix}": Output(
                "outputs.resourceId" if is_module else "id",
                symbol
            ),
            f"AZURE_{self._prefixes[0].upper()}_NAME{suffix}": Output(
                "outputs.name" if is_module else "name",
                symbol
            ),
        }
        rg_output = f"AZURE_{self._prefixes[0].upper()}_RESOURCE_GROUP{suffix}"
        if is_module:
            outputs[rg_output] = Output("outputs.resourceGroupName", symbol)
        elif resource_group:
            outputs[rg_output] = resource_group if isinstance(resource_group, str ) else resource_group.name
        return outputs
    
    
    def _merge_params(
            self,
            params: Dict[str, Any],
            **kwargs
        ) -> Dict[str, Any]:
        params.update(self.properties)
        return {}

    def _find_field(self, resource: List[str], fields: FieldsType, index: int = 0) -> Optional[FieldType]:
        try:
            return [f for f in reversed(list(fields.values())) if f.resource in resource][index]
        except IndexError:
            return None

    def _find_resource_group(
            self,
            fields: FieldsType,
            parameters: Dict[str, Parameter],
            *,
            name: Optional[str] = None
    ) -> ResourceGroupSymbol:
        rg = ["br/public:avm/res/resources/resource-group", "Microsoft.Resources/resourceGroups"]
        for field in [f for f in reversed(list(fields.values())) if f.resource in rg]:
            if name:
                if field.params['name'] == name:
                    return field.symbol
                continue
            else:
                return field.symbol
        from .resources.resourcegroup._resource import ResourceGroup
        if name:
            existing_rg = ResourceGroup.reference(name=name)
            return existing_rg.__bicep__(fields, parameters=parameters)
        default_rg = ResourceGroup()
        return default_rg.__bicep__(fields, parameters=parameters)

    def _find_identity(
            self,
            fields: FieldsType,
            parameters: Dict[str, Parameter],
            *,
            index: int = 0) -> Optional[ModuleSymbol]:
        ua = [
            "br/public:avm/res/managed-identity/user-assigned-identity",
            "Microsoft.ManagedIdentity/userAssignedIdentities"
        ]
        try:
            return self._find_field(ua, fields, index).symbol
        except AttributeError:
            from .resources.managedidentity._resource import UserAssignedIdentity
            new_identity = UserAssignedIdentity()
            return new_identity.__bicep__(fields, parameters=parameters)


    def _find_resource_match(
            self,
            fields: FieldsType,
            rg: ResourceGroupSymbol,
            name: Optional[Union[str, Expression]] = None,
    ) -> Optional[FieldType]:
        for field in [f for f in reversed(list(fields.values())) if f.resource == self.module]:
            if name:
                if field.params['name'] == name and field.resource_group == rg:
                    return field
            else:
                if field.resource_group == rg:
                    return field
        return None

    def _substitute_globals(self, params: Dict[str, Any], globals: Dict[str, Parameter]) -> None:
        if not 'location' in params:
            params['location'] = globals['location']
        if not 'tags' in params:
            # TODO: This should be a union if user provided tags
            params['tags'] = globals['tags']

    def _update_role_assignments(
            self,
            params: Dict[str, Any],
            updated_params: Optional[List[Dict[str, Any]]] = None,
            *,
            symbol: ModuleSymbol,
            identity: Optional[ModuleSymbol] = None,
            user_principal: Optional[Parameter] = None,
    ) -> None:
        if updated_params:
            role_assignments = params.pop("roleAssignments", [])
            updated_params.extend(role_assignments)
            params['roleAssignments'] = updated_params
        if 'roleAssignments' in params:
            updated_roles = {}
            for role in params['roleAssignments']:
                if isinstance(role, str):
                    if identity:
                        principal_id = identity.principal_id
                        key = (principal_id, role)
                        if key in updated_roles:
                            continue
                        updated_roles[key] = {
                            'name': Guid(self.__class__.__name__, params['name'], principal_id, role),
                            'principalId': principal_id,
                            'principalType': 'ServicePrincipal',
                            'roleDefinitionIdOrName': role
                    }
                    if user_principal:
                        key = (user_principal, role)
                        if key in updated_roles:
                            continue
                        updated_roles[key] = {
                            'name': Guid(self.__class__.__name__, params['name'], user_principal, role),
                            'principalId': user_principal,
                            'principalType': 'User',
                            'roleDefinitionIdOrName': role
                        }
                    if not user_principal and not identity:
                        raise ValueError("Role cannot be defined as string without a managedidentity or user principal.")
                else:
                    updated_roles[(role['principalId'], role['roleDefinitionIdOrName'])] = role
            params['roleAssignments'] = list(updated_roles.values())

    def _update_managed_identities(
            self,
            params: Dict[str, Any],
            updated_params: Optional[Dict[str, Any]] = None,
            *,
            identity: Optional[ModuleSymbol] = None
    ) -> None:
        if updated_params:
            managed_identities = params.pop("managedIdentities", {})
            user_assigned_identities = managed_identities.pop("userAssignedResourceIds", [])
            user_assigned_identities.extend(updated_params.get('userAssignedResourceIds', []))
            managed_identities.update(updated_params)
            managed_identities["userAssignedResourceIds"] = user_assigned_identities
            params['managedIdentities'] = managed_identities
        if identity and self._supports_managed_identity:
            if 'managedIdentities' not in params:
                params['managedIdentities'] = {
                    'userAssignedResourceIds': [identity.id]
                }
            else:
                identities = params['managedIdentities'].get('userAssignedResourceIds', [])
                existing = [i for i in identities if (hasattr(i, 'symbol') and i.symbol == identity) or i == identity]
                if not existing:
                    identities.append(identity.id)
                    params['managedIdentities']['userAssignedResourceIds'] = identities

    def __bicep__(
            self,
            fields: FieldsType,
            *,
            parameters: Dict[str, Parameter],
            app_component: Optional[Type] = None,
            attrname: Optional[str] = None
    ) -> ResourceSymbol:
        field_id = self._component.__name__ if self._component else '__main__'
        if self._existing:
            properties = dict(self._reference)
            suffix = attrname or clean_name(properties['name']).upper()
            rg = None
            if self._reference.get('parent'):
                properties['parent'] = self._reference['parent'].__bicep__(
                    fields,
                    parameters=parameters,
                    app_component=app_component,
                    attrname=suffix
                )
            else:
                rg_name = self._reference.get('scope')
                if isinstance(rg_name, Resource):
                    rg = rg_name.__bicep__(fields, parameters=parameters)
                else:
                    rg = self._find_resource_group(fields, parameters, name=rg_name)
                properties['scope'] = rg
            symbol = self._symbol()
            outputs = self._outputs(
                symbol=symbol,
                attrname=suffix,
                resource_group=rg,
                **properties
            )
            symbol = self._symbol()
            field = FieldType(
                self.resource,
                properties,
                symbol,
                outputs,
                rg,
                self.version
            )
            fields[f"{field_id}.{attrname if attrname else symbol.resolve()}"] = field
            return symbol

        reference = self.module or self.resource
        if not reference:
            raise TypeError("Empty Resource object cannot be provisioned.")
        rg_name = self._find_resource_group(fields, parameters)
        identity = self._find_identity(fields, parameters)
        resource_name = self.properties.get('name')
        field = self._find_resource_match(fields, rg_name, resource_name)
        if field:
            resource_name = field.params['name']
        else:
            if self._default == DefaultAction.MISSING:
                raise TypeError(f'Missing resource of type: {reference}')
            resource_name = resource_name or parameters['defaultName']
        if field:
            params = field.params
            symbol = field.symbol
            outputs = field.outputs
        else:
            params = dict(self.DEFAULTS)
            params['name'] = resource_name
            symbol = self._symbol()
            outputs = {}
            field = FieldType(reference, params, symbol, outputs, rg_name, self.tag or self.version)
            fields[f"{field_id}.{self._component_attr if self._component_attr else symbol.resolve()}"] = field

        managed_identities = params.pop("managedIdentities", {})
        role_assignments = params.pop("roleAssignments", [])
        output_config = self._merge_params(
            params,
            fields=fields,
            parameters=parameters,
            identity=identity,
            symbol=symbol,
            attrname=attrname,
            resource_group=rg_name
        )
        resource_outputs = self._outputs(
            symbol=symbol,
            attrname=attrname,
            resource_group=rg_name,
            **output_config
        )
        self._substitute_globals(params, parameters)
        self._update_role_assignments(
            params,
            role_assignments,
            symbol=symbol,
            identity=identity,
            user_principal=parameters.get("principalId")
        )
        self._update_managed_identities(
            params,
            managed_identities,
            identity=identity
        )
        # We only want to export the outputs if either this is a resource not nested inside a
        # component, or if it's in the root component.
        if not self._component or (app_component and app_component in self._apps and attrname in self._attrs):
            outputs.update(resource_outputs)
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
