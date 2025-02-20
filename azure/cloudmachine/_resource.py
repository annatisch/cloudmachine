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

from .resources._identifiers import ResourceIdentifiers
from ._parameters import DEFAULT_NAME, LOCATION, AZD_TAGS
from ._setting import StoredPrioritizedSetting
from ._bicep.expressions import Guid, Output, Expression, Parameter, ResourceSymbol, ResourceGroup, UniqueString, Variable
from ._bicep.utils import serialize, generate_suffix, resolve_value, serialize_dict, clean_name

if TYPE_CHECKING:
    from .resources.resourcegroup import ResourceGroup
    from .resources._extension import RoleAssignment
    from ._component import AzureInfrastructure



class DefaultResource(Enum):
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
    name: Union[str, Parameter[str]]
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
    identifier: ResourceIdentifiers
    infrastructure: Optional[AzureInfrastructure]
    resource: str
    version: str
    properties: ResourcePropertiesType
    extensions: ExtensionResources
    parent: Optional[Resource]

    def __init__(self, properties: Optional[Dict[str, Any]] = None, /, **kwargs) -> None:
        """This constructor should not be used directly."""
        self.properties: ResourcePropertiesType = properties or {}
        self.extensions: ExtensionResources = kwargs.pop('extensions', {})
        self.parent: Optional[Resource] = kwargs.pop('parent', None)
        self.identifier = kwargs.pop('identifier')
        self._resource: str = kwargs.pop('resource', "")
        self._subresource: Optional[str] = kwargs.pop('subresource', '')
        self._version: str = kwargs.pop('resource_version', "")
        self._existing: bool = kwargs.pop('existing', False)
        if self.parent and not self._subresource:
            raise ValueError('Parent must be specified with subresource.')

        # These properties are used to track whether this resource is part
        # of an AzureInfrastructure component and are set by the InfrastructureResource
        # field specifier.
        self._infra: Optional[AzureInfrastructure] = None
        self._infra_type: Optional[Type[AzureInfrastructure]] = None
        
        # Suffix and prefix are used to environment variable/config setting names
        # The prefix identifies the service/resource and the suffix is unique to this
        # specific resource (using either the name or name parameter if present).
        self._suffix: str = ""
        self._prefixes: List[str] = kwargs.pop('service_prefix', [])
    
        # These determine how resource properties are handled when building up the bicep
        # definitions for the same resource declared in multiple places. Anything in the
        # 'properties' field of a resource will error on conflict
        self._properties_to_merge = ['properties', 'tags']

        # TODO: Hopefully we can refactor away this property
        self._supports_managed_identity: bool = False
        if kwargs:
            raise TypeError(f"Resource {self.__class__.__name__} got unexpected kwargs: {list(kwargs.keys())}")

        self._name = StoredPrioritizedSetting(
            'name',
            env_vars=_build_envs(self._prefixes, ['NAME']),
            system_hook=self._get_name_if_known,
        )
        if 'name' in self.properties:
            self._name.set_value(properties['name'])
        self._resource_id = StoredPrioritizedSetting(
            name='resource_id',
            env_vars=_build_envs(self._prefixes, ['ID', 'RESOURCE_ID']),
            system_hook=self._build_resource_id
        )
        self._subscription = StoredPrioritizedSetting(
            name='subscription_id',
            env_var='AZURE_SUBSCRIPTION_ID',
            system_hook=self._existing_subscription_id
        )
        self._resource_group = StoredPrioritizedSetting(
            name='resource_group',
            env_vars=_build_envs(self._prefixes, ['RESOURCE_GROUP']),
        )
        self._settings: Dict[str, StoredPrioritizedSetting] = {
            "name": self._name,
            "resource_id": self._resource_id,
            "subscription_id": self._subscription,
            "resource_group": self._resource_group,
        }

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(\'{self.properties.get("name", "<default>")}\')'

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
    
    def name(self, *, config_store: Optional[Mapping[str, Any]] = None) -> str:
        if config_store:
            return self._name(config_store=config_store)
        if self._infra:
            return self._name(config_store=self._infra._config_store)
        return self._name()

    def resource_id(self, *, config_store: Optional[Mapping[str, Any]] = None) -> str:
        if config_store:
            return self._resource_id(config_store=config_store)
        if self._infra:
            return self._resource_id(config_store=self._infra._config_store)
        return self._resource_id()

    def resource_group(self, *, config_store: Optional[Mapping[str, Any]] = None) -> str:
        if config_store:
            return self._resource_group(config_store=config_store)
        if self._infra:
            return self._resource_group(config_store=self._infra._config_store)
        return self._resource_group()

    def subscription(self, *, config_store: Optional[Mapping[str, Any]] = None) -> str:
        if config_store:
            return self._subscription(config_store=config_store)
        if self._infra:
            return self._subscription(config_store=self._infra._config_store)
        return self._subscription()

    @classmethod
    def reference(
            cls,
            resource: str,
            *,
            name: Optional[Union[str, Parameter[str]]] = None,
            resource_group: Optional[Union[str, Parameter[str], 'ResourceGroup']] = None,
            subscription: Optional[Union[str, Parameter[str]]] = None,
            parent: Optional[Resource] = None,
    ) -> Self[ResourceReference]:
        if parent and resource_group:
            raise ValueError("Cannot specify both parent and resource_group.")
        resource_type, resource_version = resource.split('@')
        properties = ResourceReference(name=name) if name else {}
        if resource_group:
            if isinstance(resource_group, (str, Parameter)):
                from .resources.resourcegroup import ResourceGroup
                resource_group = ResourceGroup.reference(name=resource_group, subscription=subscription)
            properties['resource_group'] = resource_group
        elif subscription:
            # We're assuming 'subscription' will only be passed in in the case of rg-agnostic
            # resources, like a resourcegroup. Otherwise 'subscription' must be provided
            # on the 'resource_group' parameter.
            properties['subscription'] = subscription
        resource_ref = cls(
            properties,
            resource=resource_type,
            resource_version=resource_version,
            parent=parent,
            existing=True
        )
        resource_ref._set_suffix(name)
        if parent:
            try:
                resource_ref._resource_group.set_value(parent._resource_group._user_value)
            except RuntimeError:
                pass
            try:
                resource_ref._subscription.set_value(parent._subscription._user_value)
            except RuntimeError:
                pass
        else:
            if resource_group:
                resource_ref._resource_group.set_value(resource_group._name._user_value)
                resource_ref._subscription.set_value(resource_group._subscription._user_value)
            if subscription and isinstance(subscription, (str, Parameter)):
                resource_ref._subscription.set_value(subscription)
        return resource_ref

    def _set_infra(self, infra: AzureInfrastructure) -> None:
        self._infra = infra
        self._infra_type = infra.__class__
        if self.parent:
            self.parent._set_infra(infra)

    def _set_suffix(self, value: Union[str, Parameter] = None) -> None:
        if value:
            if isinstance(value, str):
                self._suffix = '_' + clean_name(value).upper()
            else:
                self._suffix = '_' + clean_name(value.value).upper()
            if self.parent:
                self._suffix = self.parent._suffix + self._suffix
            for setting in self._settings.values():
                setting.suffix = self._suffix
        elif self.parent:
            self._suffix = self.parent._suffix
            for setting in self._settings.values():
                setting.suffix = self._suffix

    def _existing_subscription_id(self, *, config_store: Mapping[str, Any]) -> str:
        if self._existing and 'resource_group' in self.properties:
            return self.properties['resource_group'].subscription(config_store=config_store)
        raise RuntimeError("Existing resource group reference has no subscription specified.")

    def _build_resource_id(self, *, config_store: Optional[Mapping[str, Any]]) -> str:
        if not self._resource:
            raise ValueError("No resource specified.")
        if self.parent:
            return f"{self.parent._build_resource_id(config_store=config_store)}/{self._subresource}/{self.name(config_store=config_store)}"
        prefix = f"/subscriptions/{self.subscription(config_store=config_store)}/resourceGroups/{self.resource_group(config_store=config_store)}/providers/"
        return prefix + f"{self._resource}/{self.name(config_store=config_store)}"

    def _get_name_if_known(self, *, config_store: Mapping[str, Any]) -> str:
        try:
            return self.properties['name']
        except KeyError:
            pass
        try:
            return self.DEFAULTS['name']
        except KeyError:
            pass
        raise RuntimeError("Resource name not known.")
   
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
             suffix: Optional[str] = None,
             **kwargs
    ) -> Dict[str, Output]:
        suffix = suffix or self._suffix
        outputs = {
            'resource_id': Output(f"AZURE_{self._prefixes[0].upper()}_ID{suffix}", "id", symbol),
            'name': Output(f"AZURE_{self._prefixes[0].upper()}_NAME{suffix}", "name", symbol),
        }
        rg_output = f"AZURE_{self._prefixes[0].upper()}_RESOURCE_GROUP{suffix}"
        outputs['resource_group'] = Output(rg_output, ResourceGroup().name)
        if self._existing:
            try:
                rg_name = self.resource_group()  # TODO: Is it a problem that there's no config?
                outputs['resource_group'] = Output(rg_output, rg_name)
            except RuntimeError:
                pass
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
            parent: Optional[ResourceSymbol] = None,
    ) -> Optional[FieldType]:
        resource = resource or self.resource
        for field in (f for f in reversed(list(fields.values())) if f.resource == resource):
            if name and resource_group:
                if field.properties.get('name') == name and field.resource_group == resource_group:
                    return field
            elif name and parent:
                if field.properties.get('name') == name and field.properties['parent'] == parent:
                    return field
            elif resource_group:
                if field.resource_group == resource_group:
                    return field
            elif parent:
                if field.properties['parent'] == parent:
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
            return existing_rg.__bicep__(fields, parameters=parameters, module_name=module_name)[0]
        default_rg = ResourceGroup()
        return default_rg.__bicep__(fields, parameters=parameters, module_name=module_name)[0]

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
        return new_identity.__bicep__(fields, parameters=parameters, module_name=module_name)[0]

    def _get_field_id(self, symbol: ResourceSymbol, parents: Tuple[ResourceSymbol, ...] = None) -> str:
        if parents:
            prefix = self.parent._get_field_id(parents[0], parents[1:])
            return f"{prefix}.{symbol.value}"
        return symbol.value

    def _add_parameters(self, obj: Dict[str, Any], parameters):
        for value in obj.values():
            if isinstance(value, Parameter) and value.name:
                parameters[value.name] = value
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, Parameter) and item.name:
                        parameters[item.name] = item
                    else:
                        try:
                            self._add_parameters(item, parameters)
                            continue
                        except (AttributeError, TypeError):
                            pass
            else:
                try:
                    self._add_parameters(value, parameters)
                    continue
                except (AttributeError, TypeError):
                    pass
                        
    def _add_defaults(self, field: FieldType, parameters: Dict[str, Parameter]):
        for key, value in self.DEFAULTS.items():
            if field.properties.get(key):
                if key in self._properties_to_merge:
                    try:
                        updated_default = value.copy()
                        updated_default.update(field.properties[key])
                        field.properties[key] = updated_default
                    except AttributeError:
                        # We probably got an Expression
                        # TODO: support union operation?
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
            module_name: Optional[str] = None,
    ) -> Tuple[ResourceSymbol, ...]:
        extensions = defaultdict(list)
        extensions.update(self.extensions)
        parents: Tuple[ResourceSymbol] = ()
        if self.parent:
            parents = self.parent.__bicep__(
                fields,
                parameters=parameters,
                app_component=app_component,
                module_name=module_name
            )
        self._set_suffix(self.properties.get('name', ''))

        # We only want to export the outputs if either this is a resource not nested inside an
        # infrastructure object, or if it's in the root infrastructure object.
        output_resource = False
        if not self._infra or app_component == self._infra:
            output_resource = True

        if self._existing:
            if 'name' not in self.properties and 'name' not in self.DEFAULTS:
                raise ValueError(f"Reference to existing resource {repr(self)} is missing 'name'.")
            properties = {'name': self.properties.get('name', self.DEFAULTS['name'])}
            if parents:
                properties['parent'] = parents[0]
                rg = None
            elif 'resource_group' in self.properties:
                rg = self.properties['resource_group'].__bicep__(fields, parameters=parameters, module_name=module_name)[0]
                properties['scope'] = rg
            else:
                rg = self._find_resource_group(fields, parameters, module_name=module_name)
                properties['scope'] = rg
            symbol = self._symbol()
            outputs = self._outputs(
                symbol=symbol,
                resource_group=rg,
                parents=parents,
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
            fields[self._get_field_id(symbol, parents)] = field
            return (symbol, *parents)


        identity = None
        # TODO: Should probably revise this logic - it was added because it creates
        # the initial managed identity if none is otherwise specified. Must be a cleaner
        # way to do that....
        if self._supports_managed_identity:
            identity = self._find_identity(fields, parameters, module_name=module_name)
        rg = self._find_resource_group(fields, parameters, module_name=module_name)
        if not parents:
            field = self._find_last_resource_match(fields, resource_group=rg, name=self.properties.get('name'))
        else:
            field = self._find_last_resource_match(fields, parent=parents[0], name=self.properties.get('name'))

        if field:
            params = field.properties
            symbol = field.symbol
            outputs = field.outputs
            if 'managed_identity_roles' in self.extensions:
                # We don't really care if this causes duplicate roles because they should be
                # cleaned up when exported to bicep.
                field.extensions['managed_identity_roles'].extend(extensions['managed_identity_roles'])
            if 'user_roles' in self.extensions:
                field.extensions['user_roles'].extend(extensions['user_roles'])
        else:
            params = {}
            if self.parent:
                params['parent'] = parents[0]
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
            fields[self._get_field_id(symbol, parents)] = field

        output_config = self._merge_properties(
            params,
            self.properties,
            fields=fields,
            parameters=parameters,
            symbol=symbol,
            resource_group=rg,
            identity=identity,
        )
        if not outputs and output_resource:
            resource_outputs = self._outputs(
                symbol=symbol,
                resource_group=rg,
                parents=parents,
                **output_config
            )
            outputs.update(resource_outputs)
        self._add_parameters(field.properties, parameters)
        # TODO: this wont really work yet
        # self._add_parameters(field.extensions, parameters)
        return (symbol, *parents)


    def get_client(
            self,
            cls: Callable[..., ClientType],
            /,
            *,
            options: Optional[Dict[str, Any]] = None,
            config_store: Optional[Mapping[str, Any]] = None,
            env_name: Optional[str] = None,
    ) -> ClientType:
        raise TypeError(f"Resource '{repr(self)}' has no compatible Client endpoint.")


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
        raise NotImplementedError("This must be implemented by child resources.")

    def _build_credential(self, use_async: bool, *, config_store: Mapping[str, Any]) -> Union[SupportsTokenInfo, AsyncSupportsTokenInfo]:
        value = self.credential(config_store=config_store)
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

    def get_client(
            self,
            cls: Callable[..., ClientType],
            /,
            *,
            transport: Any = None,
            api_version: Optional[str] = None,
            audience: Optional[str] = None,
            config_store: Optional[Mapping[str, Any]] = None,
            env_name: Optional[str] = None,
            use_async: Optional[bool] = None,
            **client_options,
    ) -> ClientType:
        self._set_suffix(self.properties.get('name', ''))
        if env_name:
           if config_store:
               raise ValueError("Cannot specify both 'config_store' and 'env_name'.")
           config_store = _load_dev_environment(env_name)
        elif not config_store:
            config_store = _load_dev_environment()

        if hasattr(cls, 'from_resource'):
            return cls.from_resource(self, config_store, transport=transport, **client_options)
        if hasattr(cls, '_from_resource'):
            return cls._from_resource(self, config_store, transport=transport, **client_options)

        endpoint = self.endpoint(config_store=config_store)
        client_kwargs = {}
        client_kwargs.update(self.client_options(config_store=config_store))
        client_kwargs.update(client_options)
        try:
            client_kwargs['api_version'] = self.api_version(api_version, config_store=config_store)
        except RuntimeError:
            pass
        try:
            client_kwargs['audience'] = self.audience(audience, config_store=config_store)
        except RuntimeError:
            pass
        if 'credential' not in client_kwargs:
            if use_async is None:
                try:
                    use_async = inspect.iscoroutinefunction(getattr(cls, 'close'))
                except AttributeError:
                    raise TypeError(f"Cannot determine whether cls type '{cls.__name__}' is async or not. Please specify 'use_async' keyword argument.")
            client_kwargs['credential'] = self._build_credential(use_async, config_store=config_store)
        client = cls(endpoint, **client_kwargs)
        client.__resource_settings__ = self
        return client
