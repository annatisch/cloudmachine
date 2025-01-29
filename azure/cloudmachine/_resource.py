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
from dataclasses import MISSING
from inspect import get_annotations
from itertools import takewhile, product, accumulate
import json
from typing import (
    Mapping,
    Tuple,
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
    TYPE_CHECKING
)
from typing_extensions import Self


from azure.core.credentials import (
    SupportsTokenInfo,
    AzureKeyCredential,
    AzureSasCredential,
    AzureNamedKeyCredential
)
from azure.core.credentials_async import AsyncSupportsTokenInfo
from azure.core.settings import PrioritizedSetting

from ._setting import StoredPrioritizedSetting
from ._bicep.expressions import Guid, ModuleSymbol, Output, Expression, Parameter, ResourceGroupSymbol, ResourceSymbol, Variable
from ._bicep.utils import serialize, generate_suffix, resolve_value, serialize_dict


ClientType = TypeVar("ClientType")
SyncCredentialInputTypes = Union[
    SupportsTokenInfo,
    Callable[[], SupportsTokenInfo],
    Literal['default', 'managedidentity'],
]
AsyncCredentialInputTypes = Union[
    AsyncSupportsTokenInfo,
    Callable[[], AsyncSupportsTokenInfo],
    Literal['default', 'managedidentity'],
]
FieldType = Tuple[Dict[str, Any], ResourceSymbol, Dict[str, Union[str, Output]], ResourceGroupSymbol]
FieldsType = List[Tuple[str, Dict[str, Any], ResourceSymbol, Dict[str, Union[str, Output]], ResourceGroupSymbol]]
ResourcesType = Dict[ResourceGroupSymbol, Dict[Tuple[str, str], FieldType]]


def _convert_dict(value: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
    if isinstance(value, str):
        return json.loads(value)
    return dict(value)


def _convert_str_from_setting(value: Union[str, PrioritizedSetting[Any, str]]) -> str:
    try:
        return value()
    except TypeError:
        return str(value)


def _convert_to_str(value: Any, include_sensitive: bool = False) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, type):
        module_path = value.__module__.split('.')
        public_path = ".".join(takewhile(lambda x: not x.startswith('_'), module_path))
        return public_path + f".{value.__name__}"
    if isinstance(value, dict):
        return json.dumps(value)
    if isinstance(value, PrioritizedSetting):
        return _convert_to_str(value())
    raise RuntimeError("Value cannot be stored.")


def _build_envs(services: List[str], attributes: List[str]) -> List[str]:
    all_vars = product(services, attributes)
    return ["_".join(['AZURE'] + list(var)).upper() for var in all_vars]


class Resource:
    resource: str = ""
    module: str = ""
    identifier: str = ""
    name: PrioritizedSetting[str, str]
    id: PrioritizedSetting[str, str]
    properties: Mapping[str, Any]
    component: Type
    attr: str
    defaults: Mapping[str, Any]

    def __init__(
            self,
            properties: Dict[str, Any],
            *,
            service_prefix: List[str],
            default: Optional[ClientType] = MISSING,
            default_factory: Optional[Callable[[Self], ClientType]] = MISSING,
            **kwargs
    ) -> None:
        self.properties = properties
        self._prefixes = service_prefix
        self._default = default
        self._default_factory = default_factory
        self._supports_managed_identity = False

        self._suffix = generate_suffix(5)
        self._component: Optional[Type] = None
        self._component_attr: Optional[str] = None
        self._apps: List[str] = []
        self._attrs: List[str] = []
        self._inferred_resource: Optional[str] = None
        self._inferred_obj: Optional[Resource] = None

        self._args = kwargs.pop('args', [])
        self._kwargs = kwargs.pop('kwargs', {})
        if kwargs:
            raise TypeError(f"Resource {self.__class__.__name__} got unexpected kwargs: {list(kwargs.keys())}")

        self.name = StoredPrioritizedSetting(
            'name',
            env_vars=_build_envs(self._prefixes, ['NAME']),
            convert=str,
        )
        self.id = StoredPrioritizedSetting(
            name='resource_id',
            env_vars=_build_envs(self._prefixes, ['ID', 'RESOURCE_ID']),
            convert=_convert_str_from_setting,
        )
        self._settings: Dict[str, StoredPrioritizedSetting] = {
            "name": self.name,
            "id": self.id
        }

    @classmethod
    def _from_inferred_resource(cls, *args, **kwargs):
        return cls(
            {},
            service_prefix=[],
            args=args,
            kwargs=kwargs,
        )

    def __set_name__(self, owner: Type, name: str) -> None:
        self.attr = name
        if self._component is None:
            if not self.resource:
                from .resources import INFERRED_RESOURCE
                try:
                    annotation = get_annotations(owner)[name]
                except KeyError:
                    raise RuntimeError(f"Resource '{name}' is missing type hint or resource identifier.") from None
                self._inferred_resource = INFERRED_RESOURCE[annotation.__name__].identifier
        self.component = owner

    def __get__(self, *args) -> Self:
        if self._inferred_obj:
            return self._inferred_obj
        if self._inferred_resource:
            from ._component import resource
            inferred_resource = resource(
                self._inferred_resource,
                *self._args,
                **self._kwargs
            )
            inferred_resource._component = self._component
            inferred_resource._component_attr = self._component_attr
            inferred_resource._apps = self._apps
            inferred_resource._attrs = self._attrs
            inferred_resource._suffix = self._suffix
            self._inferred_obj = inferred_resource
            return inferred_resource
        return self

    def __set__(self, obj, value):
        raise NotImplementedError()

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
        if not self._component_attr:
            self._component_attr = value

    def __copy(self, **kwargs) -> Self:
        # TODO: Allow overwriting without mutating
        raise NotImplementedError

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

    def _symbol(self) -> ResourceSymbol:
        if not self.resource:
            raise TypeError("Empty Resource object cannot be provisioned.")
        resource_ref = self.resource.split("/")[0].split(".")[1]
        symbol = f"{resource_ref.lower()}_{self._suffix}"
        pid = None
        if self.module:
            if self.properties.get('managedIdentities', {}).get('systemAssigned', False):
                pid = "outputs.systemAssignedMIPrincipalId"
            return ModuleSymbol(symbol, principal_id=pid)
        if self.properties.get('identity', {}).get('type', "").startswith('SystemAssigned'):
            pid = "principalId"
        return ResourceSymbol(symbol, principal_id=pid)
    
    def _merge_params(
            self,
            params: Dict[str, Any],
            *,
            symbol: ResourceSymbol,
            attrname: Optional[str] = None,
            **kwargs
        ) -> Dict[str, Output]:
        params.update(self.properties)
        suffix = (attrname or self._suffix).upper()
        self._append_suffix(suffix)
        return {
            f"AZURE_{self._prefixes[0].upper()}_ID_{suffix}": Output(
                "outputs.resourceId" if self.module else "id",
                symbol
            ),
            f"AZURE_{self._prefixes[0].upper()}_NAME_{suffix}": Output(
                "outputs.name" if self.module else "name",
                symbol
            )
        }

    def _find_field(self, resource: str, fields: FieldsType, index: int = 0) -> Optional[FieldType]:
        try:
            return [tuple(f[1:]) for f in reversed(fields) if f[0].startswith(resource)][index]
        except IndexError:
            return None

    def _find_resource_group(self, fields: FieldsType, index: int = 0) -> ResourceGroupSymbol:
        return self._find_field("br/public:avm/res/resources/resource-group", fields, index)[1]

    def _find_identity(self, fields: FieldsType, index: int = 0) -> Optional[ModuleSymbol]:
        try:
            return self._find_field("br/public:avm/res/managed-identity/user-assigned-identity", fields, index)[1]
        except TypeError:
            return None

    def _find_resource_match(
            self,
            fields: FieldsType,
            rg: ResourceGroupSymbol,
            name: Optional[Union[str, Expression]] = None,
    ) -> Optional[FieldType]:
        for field in [tuple(f[1:]) for f in reversed(fields) if f[0].startswith(self.module)]:
            if name:
                if field[0]['name'] == name and field[-1] == rg:
                    return field
            else:
                if field[-1] == rg:
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
                            'name': Guid(symbol._value, principal_id, role),
                            'principalId': principal_id,
                            'principalType': 'ServicePrincipal',
                            'roleDefinitionIdOrName': role
                    }
                    if user_principal:
                        key = (user_principal, role)
                        if key in updated_roles:
                            continue
                        updated_roles[key] = {
                            'name': Guid(symbol._value, user_principal, role),
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
            resources: ResourcesType,
            *,
            parameters: Dict[str, Parameter],
            app_component: Type,
            attrname: Optional[str] = None
    ) -> Optional[FieldType]:
        reference = self.module or self.resource
        if not reference:
            raise TypeError("Empty Resource object cannot be provisioned.")
        rg_name = self._find_resource_group(fields)
        new_field = None
        resource_name = self.properties.get('name')
        existing_field = self._find_resource_match(fields, rg_name, resource_name)
        if existing_field:
            resource_name = existing_field[0]['name']
        else:
            resource_name = resource_name or parameters['cloudmachineId']

        resource_id = (reference, resource_name)
        if existing_field:
            params, symbol, outputs, _ = existing_field
        else:
            params = dict(self.defaults)
            params['name'] = resource_name
            symbol = self._symbol()
            outputs = {}
            new_field = (params, symbol, outputs, rg_name)
            fields.append((reference, *new_field))
        
        identity = self._find_identity(fields)
        managed_identities = params.pop("managedIdentities", {})
        role_assignments = params.pop("roleAssignments", [])
        resource_outputs = self._merge_params(
            params,
            fields=fields,
            parameters=parameters,
            identity=identity,
            symbol=symbol,
            attrname=attrname,
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
        if app_component in self._apps and attrname in self._attrs:
            outputs.update(resource_outputs)
        resources[rg_name][resource_id] = existing_field or new_field
        return new_field


    @overload
    def __call__(
        self,
        cls: Callable[..., ClientType],
        /,
        *,
        options: Optional[Dict[str, Any]] = None,
    ) -> ClientType:
        ...
    @overload
    def __call__(self, cls: Optional[Type[Resource]] = None, /) -> Self:
        ...
    def __call__(self, cls=None, /, *, options=None, **kwargs):
        if self._default:
            return self._default
        if self._default_factory:
            return self._default_factory(self)
        if cls is None or cls is self.__class__ or cls in self.__class__.__mro__:
            return self
        elif hasattr(cls, 'from_resource'):
            return cls.from_resource(self, **options or {})
        elif hasattr(cls, '_from_resource'):
            return cls._from_resource(self, **options or {})
        raise TypeError(f"Unsupport type '{cls.__name__}' for resource '{self.__class__.__name__}'.")



class _ClientResource(Resource):
    endpoint: PrioritizedSetting[str, str]
    client_options: PrioritizedSetting[Dict[str, Any], Dict[str, Any]]
    audience: PrioritizedSetting[str, str]
    credential: PrioritizedSetting[Union[SyncCredentialInputTypes, AsyncCredentialInputTypes], Union[SupportsTokenInfo, AsyncSupportsTokenInfo]]
    api_version: PrioritizedSetting[str, str]

    def __init__(
            self,
            properties: Dict[str, Any],
            *,
            service_prefix: List[str],
            default: Optional[ClientType] = MISSING,
            default_factory: Optional[Callable[[Self], ClientType]] = MISSING,
            **kwargs
    ) -> None:
        super().__init__(
            properties=properties,
            service_prefix=service_prefix,
            default=default,
            default_factory=default_factory,
            **kwargs
        )
        self.audience = StoredPrioritizedSetting(
            name='audience',
            env_vars=_build_envs(self._prefixes, ['AUDIENCE']),
            convert=_convert_str_from_setting,
            to_str=_convert_to_str,
        )
        self._settings['audience'] = self.audience
        self.endpoint = StoredPrioritizedSetting(
            name='endpoint',
            env_vars=_build_envs(self._prefixes, ['ENDPOINT']),
            convert=str,
        )
        self._settings['endpoint'] = self.endpoint
        self.api_version = StoredPrioritizedSetting(
            name='api_version',
            env_vars=_build_envs(self._prefixes, ['API_VERSION']),
            convert=_convert_str_from_setting,
            to_str=_convert_to_str,
        )
        self._settings['api_version'] = self.api_version
        self.client_options = StoredPrioritizedSetting(
            name='client_options',
            convert=_convert_dict,
            to_str=_convert_to_str,
            default={},
        )
        self._settings['client_options'] = self.client_options
        self.credential = StoredPrioritizedSetting(
            name='credential',
            default='default',
            convert=self._build_credential,
            to_str=_convert_to_str,
        )
        self._settings['credential'] = self.credential


    def _build_credential(self, value: SyncCredentialInputTypes) -> SupportsTokenInfo:
        try:
            value = value.lower()
            if value == 'default':
                from azure.identity import DefaultAzureCredential
                credential = DefaultAzureCredential()
                self.credential.set_value(credential)
                return credential
            if value == 'managedidentity':
                from azure.identity import ManagedIdentityCredential
                credential = ManagedIdentityCredential()
                self.credential.set_value(credential)
                return credential
        except AttributeError:
            if isinstance(value, SupportsTokenInfo):
                return value
        try:
            return value()
        except TypeError:
            pass
        raise ValueError(f'Cannot convert {value} to credential type.')
