# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import os
import random
import string
import itertools
from typing import IO, Any, List, Optional, Dict, Literal, Self, Union, ClassVar
from dataclasses import InitVar, dataclass, asdict, field, fields, is_dataclass

dataclass_model = dataclass(kw_only=True)


def generate_symbol(prefix: str, n=itertools.count()) -> str:
    # return prefix + ''.join(
    #     random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(n)
    # ).lower()
    return f"{prefix}{next(n):03}"

def generate_name(n=itertools.count()) -> str:
    # return prefix + ''.join(
    #     random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(n)
    # ).lower()
    return f"cm-${{resourceToken}}{next(n):03}"


def _serialize_resource(bicep: IO[str], model_val: 'Resource') -> None:
    indent: str = '  '
    bicep.write(f"resource {model_val._symbolicname} '{model_val._resource}@{model_val._version}' = {{\n")
    if model_val._parent:
        bicep.write(f"{indent}parent: {model_val._parent._symbolicname}\n")
    #else:
    #    bicep.write(f"{indent}scope: {model_val._rg._symbolicname}\n")
    _serialize_dataclass(bicep, model_val, indent)
    bicep.write("}\n\n")


def _serialize_dataclass(bicep: IO[str], data_val: dataclass, indent: str) -> None:
    for field in fields(data_val):
        client_name = field.name
        if client_name.startswith('_'):
            continue
        value = getattr(data_val, client_name)
        if value is _UNSET:
            continue
        try:
            rest_name = field.metadata['rest']
        except KeyError:
            continue
        if is_dataclass(value):
            bicep.write(f"{indent}{rest_name}: {{\n")
            _serialize_dataclass(bicep, value, indent + '  ')
            bicep.write(f"{indent}}}\n")
        elif isinstance(value, dict):
            if rest_name == 'tags':
                bicep.write(f"{indent}{rest_name}: union(\n")
                bicep.write(f"{indent}  tags, {{\n")
                _serialize_dict(bicep, value, indent + '    ')
                bicep.write(f"{indent}  }}\n")
                bicep.write(f"{indent})\n")
            else:
                if not value:
                    continue
                bicep.write(f"{indent}{rest_name}: {{\n")
                _serialize_dict(bicep, value, indent + '  ')
                bicep.write(f"{indent}}}\n")
        elif isinstance(value, list):
            if not value:
                continue
            bicep.write(f"{indent}{rest_name}: [\n")
            _serialize_list(bicep, value, indent + '  ')
            bicep.write(f"{indent}]\n")
        else:
            if rest_name == 'location' and isinstance(value, _DEFAULT_LOCATION):
                bicep.write(f"{indent}{rest_name}: location\n")
            else:
                bicep.write(f"{indent}{rest_name}: '{value}'\n") 


def _serialize_dict(bicep: IO[str], dict_val: Dict[str, Any], indent: str) -> None:
    for key, value in dict_val.items():
        if isinstance(value, dict) and value:
            bicep.write(f"{indent}{key}: {{\n")
            _serialize_dict(bicep, value, indent + '  ')
            bicep.write(f"{indent}}}\n")
        elif isinstance(value, list) and value:
            bicep.write(f"{indent}{key}: [\n")
            _serialize_list(bicep, value, indent + '  ')
            bicep.write(f"{indent}]\n")
        else:
            bicep.write(f"{indent}{key}: '{value}'\n")


def _serialize_list(bicep: IO[str], list_val: List[Any], indent: str) -> None:
    for item in list_val:
        if isinstance(item, dict):
            bicep.write(f"{indent} {{\n")
            _serialize_dict(bicep, item, indent + '  ')
            bicep.write(f"{indent} }}\n")
        elif isinstance(item, list):
            bicep.write(f"{indent} [\n")
            _serialize_list(bicep, item, indent + '  ')
            bicep.write(f"{indent} ]\n")
        else:
            bicep.write(f"{indent}'{item}'\n")
    
    return bicep


@dataclass_model
class BicepDefinition:
    _resource: ClassVar[str]
    _version: ClassVar[str]
    _symbolicname: str


class _UNSET:
    ...


class _DEFAULT_LOCATION(str):
    ...


@dataclass_model
class ResourceGroup(BicepDefinition):
    name: str = field(default_factory=lambda: generate_name(), init=False, metadata={'rest': 'name'})
    location: str = field(default_factory=_DEFAULT_LOCATION, metadata={'rest': 'location'})
    tags: Dict[str, str] = field(default_factory=dict, metadata={'rest': 'tags'})
    _resources: List['LocatedResource'] = field(default_factory=list, init=False, repr=False)
    _resource: ClassVar[Literal['Microsoft.Resources/resourceGroups']] = 'Microsoft.Resources/resourceGroups'
    _version: ClassVar[str] = '2021-04-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("resourceGroup"), init=False, repr=False)

    def add(self, resource: 'Resource') -> None:
        resource._rg = self
        self._resources.append(resource)

    def write(self, bicep: IO[str]) -> None:
        indent: str = '  '
        bicep.write(f"resource {self._symbolicname} '{self._resource}@{self._version}' = {{\n")
        _serialize_dataclass(bicep, self, indent)
        bicep.write("}\n\n")

        for resource in self._resources:
            resource_name = f"{resource._symbolicname}.bicep"
            resource_file = os.path.join(os.path.dirname(bicep.name), "core", resource_name)
            with open(resource_file, 'w') as resource_bicep:
                resource_bicep.write(f"metadata description = 'Creates an {resource._resource}.'\n\n")
                if isinstance(resource.location, _DEFAULT_LOCATION):
                    resource_bicep.write("param location string = resourceGroup().location\n")
                resource_bicep.write("param resourceToken string\n")
                resource_bicep.write("param tags object = {}\n\n")
                resource.write(resource_bicep)

            bicep.write(f"module {resource._symbolicname} 'core/{resource_name}' = {{\n")
            bicep.write(f"{indent}name: '{resource._symbolicname}'\n")
            bicep.write(f"{indent}scope: {resource._rg._symbolicname}\n")
            bicep.write(f"{indent}params: {{\n")
            if isinstance(resource.location, _DEFAULT_LOCATION):
                bicep.write(f"{indent}  location: location\n")
            bicep.write(f"{indent}  tags: tags\n")
            bicep.write(f"{indent}  resourceToken: resourceToken\n")
            bicep.write(f"{indent}}}\n")
            bicep.write(f"}}\n\n")


class _DEFAULT_RESOURCE_GROUP(ResourceGroup):
    ...


@dataclass_model
class Resource(BicepDefinition):
    parent: InitVar[Optional['Resource']] = None
    scope: InitVar[Optional[ResourceGroup]] = None
    name: str = field(default_factory=lambda: generate_name(), init=False, metadata={'rest': 'name'})
    _parent: Optional['Resource'] = field(init=False, default=None)
    _rg: ResourceGroup = field(init=False, default_factory=_DEFAULT_RESOURCE_GROUP)

    def __post_init__(self, parent: Optional['Resource'], scope: Optional['ResourceGroup']):
        if parent:
            self._parent = parent
            self._rg = parent._rg
        if scope:
            self._rg = scope

    def write(self, bicep: IO[str]) -> None:
        _serialize_resource(bicep, self)

    @classmethod
    def existing(self, scope: Optional['ResourceGroup'] = None) -> Self:
        raise NotImplementedError()

    def write(self, bicep: IO[str]) -> None:
        _serialize_resource(bicep, self)


@dataclass_model
class LocatedResource(Resource):
    location: str = field(default_factory=_DEFAULT_LOCATION, metadata={'rest': 'location'})
    tags: Dict[str, str] = field(default_factory=dict, metadata={'rest': 'tags'})
