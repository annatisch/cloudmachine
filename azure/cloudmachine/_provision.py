from inspect import get_annotations
import inspect
from typing import IO, Any, Callable, Iterable, List, Literal, Optional, Type, Dict, Tuple, TYPE_CHECKING, TypeVar, Union, Unpack, overload
import os
import json
import subprocess
from collections import defaultdict

from dotenv import dotenv_values

from ._version import VERSION
from ._component import CloudMachine
from ._bicep.utils import generate_name, resolve_value, serialize_dict, generate_suffix, serialize_list
from ._bicep.expressions import Expression, Output, Parameter, Subscription, UniqueString, Variable
from ._resource import Resource, FieldsType, _load_dev_environment
from .resources.resourcegroup import ResourceGroup
from .resources.managedidentity import UserAssignedIdentity

_BICEP_PARAMS = {
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {}
}

def _provision_project(name: str, label: Optional[str] = None) -> None:
    project_name = name + (f"-{label}" if label else "")
    args = ['azd', 'provision', '-e', project_name]
    print("Running: ", args)
    output = subprocess.run(args)
    print(output)
    return output.returncode

def _init_project(
        *,
        root_path: str,
        name: str,
        infra_dir: str,
        main_bicep: str,
        location: Optional[str] = None,
        label: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
) -> None:
    azure_dir = os.path.join(root_path, ".azure")
    azure_yaml = os.path.join(root_path, "azure.yaml")
    project_name = name + (f"-{label}" if label else "")
    project_dir = os.path.join(azure_dir, project_name)
    # TODO proper yaml parsing
    # Needs to properly set code root
    # Shouldn't overwrite on every run
    if not os.path.isfile(azure_yaml):
        with open(azure_yaml, 'w') as config:
            config.write("# yaml-language-server: $schema=https://raw.githubusercontent.com/Azure/azure-dev/main/schemas/v1.0/azure.yaml.json\n\n")
            config.write(f"name: {project_name}\n")
            config.write("metadata:\n")
            config.write(f"  cloudmachine: {VERSION}\n")
            if metadata:
                for key, value in metadata.items():
                    config.write(f"  {key}: {value}\n")
            config.write("infra:\n")
            config.write(f"  path: {infra_dir}\n")
            config.write(f"  module: {main_bicep}\n")

    returncode = 0
    if not os.path.isdir(azure_dir) or not os.path.isdir(project_dir):
        print(f"Adding environment: {project_name}.")
        output = subprocess.run(['azd', 'env', 'new', project_name])
        print(output)
        returncode = output.returncode
    if location:
        output = subprocess.run(['azd', 'env', 'set', 'AZURE_LOCATION', location, '-e', project_name])
        print(output)
        returncode = output.returncode
    print("Finished environment setup.")
    return returncode


def _get_component_resources(component: Type[Resource]) -> Dict[str, Resource]:
    return {k: getattr(component, k) for k, v in component.__dict__.items() if isinstance(v, Resource)}

def _get_filename() -> str:
    frame = inspect.stack()[2]
    return os.path.splitext(os.path.basename(frame[0].f_code.co_filename))[0]
    # module = inspect.getmodule(frame[0])
    # filename = module.__file__

AppType = TypeVar("AppType")
ResourceType = TypeVar("ResourceType")
@overload
def provision(
        __r: Type[AppType],
        infra_dir: str = "infra",
        main_bicep: str = "main",
        output_dir: str = ".",
        add_user_principal: bool = True,
        location: Optional[str] = None,
        name: Optional[str] = None,
) -> AppType:
    ...
@overload
def provision(
        __r: ResourceType,
        infra_dir: str = "infra",
        main_bicep: str = "main",
        output_dir: str = ".",
        add_user_principal: bool = True,
        location: Optional[str] = None,
        name: Optional[str] = None,
) -> ResourceType:
    ...
@overload
def provision(
        *__r: Union[ResourceType, Type[AppType]],
        infra_dir: str = "infra",
        main_bicep: str = "main",
        output_dir: str = ".",
        add_user_principal: bool = True,
        location: Optional[str] = None,
        name: Optional[str] = None,
) -> Tuple[Union[ResourceType, AppType]]:
    ...
def provision(
        *__r,
        infra_dir: str = "infra",
        main_bicep: str = "main",
        output_dir: str = ".",
        add_user_principal: bool = True,
        location: Optional[str] = None,
        name: Optional[str] = None,
):
    deployment_name = name or _get_filename()
    working_dir = os.path.abspath(output_dir)
    export(
        *__r,
        infra_dir=infra_dir,
        main_bicep=main_bicep,
        output_dir=output_dir,
        add_user_principal=add_user_principal,
        location=location,
        name=deployment_name,
    )
    returncode = _init_project(
        root_path=working_dir,
        name=deployment_name,
        infra_dir=infra_dir,
        main_bicep=main_bicep,
        location=location
    )
    if returncode != 0:
        raise RuntimeError()
    returncode = _provision_project(deployment_name)
    if returncode != 0:
        raise RuntimeError()
    # TODO: Run azd provision command.
    config = _load_dev_environment(deployment_name)
    if len(__r) == 1:
        return __r[0](env_name=deployment_name)
    return (r(env_name=deployment_name) for r in __r)


def export(
        *__r: Union[Resource, Type[AppType]],
        infra_dir: str = "infra",
        main_bicep: str = "main",
        output_dir: str = ".",
        add_user_principal: bool = True,
        location: Optional[str] = None,
        name: Optional[str] = None,
) -> None:
    if not __r:
        return
    deployment = list(__r)
    print("Building bicep...")
    working_dir = os.path.abspath(output_dir)
    infra_dir = os.path.join(working_dir, infra_dir)
    parameters: Dict[str, Parameter] = {}
    parameters['location'] = Parameter(
        'location',
        'string',
        default=location,
        description="Primary location for all resources",
        min_length=1,
        varname="AZURE_LOCATION"
    )
    parameters['environmentName'] = Parameter(
        'environmentName',
        'string',
        default=location,
        description="AZD environment name",
        min_length=1,
        max_length=64,
        varname="AZURE_ENV_NAME"
    )
    if add_user_principal:
        parameters['principalId'] = Parameter(
            'principalId',
            'string',
            description="Id of the user or app to assign application roles",
            varname="AZURE_PRINCIPAL_ID"
            ,
        )
    parameters['tags'] = Variable('tags', 'object', { 'azd-env-name': parameters['environmentName'] })
    deployment_name = name or _get_filename()
    parameters['defaultName'] = Variable(
        'defaultName',
        'string',
        UniqueString(Subscription().subscription_id,  deployment_name, parameters['location'])
    )
    try:
        os.makedirs(infra_dir)
    except FileExistsError:
        pass
    bicep_main = os.path.join(infra_dir, f"{main_bicep}.bicep")
    with open(bicep_main, 'w') as main:
        main.write("targetScope = 'subscription'\n\n")
        for parameter in parameters.values():
            main.write(parameter.main_declare())

        fields: FieldsType = {}
        for resource in deployment:
            if isinstance(resource, Resource):
                resource.__bicep__(
                    fields=fields,
                    parameters=parameters
                )
            elif issubclass(resource, CloudMachine):
                _parse_module(
                    parameters=parameters,
                    parent_component=resource,
                    component=resource,
                    component_resources=_get_component_resources(resource),
                    component_fields=fields,
                )
        _write_resources(
            bicep=main,
            fields=fields,
            parameters=parameters
        )
        main.write("\n")

    main_parameters = os.path.join(infra_dir, f"{main_bicep}.parameters.json")
    params_content = dict(_BICEP_PARAMS)
    for parameter in parameters.values():
        if isinstance(parameter, Parameter):
            params_content["parameters"].update(parameter.parameter())
    with open(main_parameters, 'w') as params_json:
        json.dump(params_content, params_json, indent=4)


def _parse_module(
        *,
        parameters: Dict[str, Parameter],
        parent_component: Type,
        component: Type,
        component_resources: Dict[str, Resource],
        component_fields: FieldsType,
        attrname: Optional[str] = None,
) -> FieldsType:
    for name, r in component_resources.items():
        if r.component == component:
            r.__bicep__(
                component_fields,
                parameters=parameters,
                app_component=parent_component,
                attrname=attrname or name
            )
        else:
            _parse_module(
                parameters=parameters,
                parent_component=parent_component,
                component=r.component,
                component_resources=_get_component_resources(r.component),
                component_fields=component_fields,
                attrname=name,
            )


def _write_resources(
        bicep: IO[str],
        fields: FieldsType,
        parameters: Dict[str, Parameter],
) -> None:
    all_outputs = []
    depends = None
    for key, (resource, params, symbol, outputs, resource_group, version) in fields.items():
        if resource.startswith('br/public:'):
            bicep.write(f"module {symbol.resolve()} '{resource}:{version}' = {{\n")
            bicep.write(f"  name: '${{deployment().name}}_{symbol.resolve()}'\n")
            if 'resources/resource-group' not in resource:
                bicep.write(f"  scope: {resource_group}\n")
            bicep.write("  params: {\n")
            bicep.write(serialize_dict(params, "    ", **parameters))
            bicep.write("  }\n")
            if depends:
                bicep.write("  dependsOn: [\n")
                bicep.write(serialize_list([depends], "    "))
                bicep.write("  ]\n")
            bicep.write("}\n")
            depends = symbol
        elif resource == "Microsoft.Resources/resourceGroups":
            bicep.write(f"resource {symbol.resolve()} '{resource}@{version}' existing = {{\n")
            bicep.write(f"  name: {resolve_value(params['name'], **parameters)}\n")
            if 'scope' in params:
                bicep.write(f"  scope: subscription('{params['scope']}')\n")
            bicep.write("}\n")
        elif resource.startswith('Microsoft.'):
            bicep.write(f"resource {symbol.resolve()} '{resource}@{version}' existing = {{\n")
            bicep.write(f"  name: {resolve_value(params['name'], **parameters)}\n")
            if 'parent' in params:
                bicep.write(f"  parent: {resolve_value(params['parent'])}\n")
            else:
                bicep.write(f"  scope: {resource_group}\n")
            bicep.write("}\n")
        for varname, output in outputs.items():
            all_outputs.append(varname)
            bicep.write(f"output {varname} string = {resolve_value(output)}\n")
        bicep.write("\n")
