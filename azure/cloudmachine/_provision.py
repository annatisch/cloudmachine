from inspect import get_annotations
import inspect
from typing import IO, Any, Callable, Iterable, List, Literal, Optional, Type, Dict, Tuple, TYPE_CHECKING, TypeVar, Union, Unpack, overload
import os
import json
import subprocess
from collections import defaultdict

from dotenv import dotenv_values

from ._version import VERSION
from ._component import AzureInfrastructure, AnnotationResource
from ._parameters import GLOBAL_PARAMS
from ._bicep.utils import generate_name, resolve_value, serialize_dict, generate_suffix, serialize_list
from ._bicep.expressions import Expression, Output, Parameter, ResourceSymbol, Subscription, UniqueString, Variable
from ._resource import FieldType, Resource, FieldsType, _load_dev_environment
from .resources._extension import add_extensions


_BICEP_PARAMS = {
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
    "contentVersion": "1.0.0.0",
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
    return {k: getattr(component, k) for k, v in component.__dict__.items() if isinstance(v, (Resource, AnnotationResource))}

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
        user_access: bool = True,
        location: Optional[str] = None,
        name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
) -> AppType:
    ...
@overload
def provision(
        __r: ResourceType,
        infra_dir: str = "infra",
        main_bicep: str = "main",
        output_dir: str = ".",
        user_access: bool = True,
        location: Optional[str] = None,
        name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
) -> ResourceType:
    ...
@overload
def provision(
        *__r: Union[ResourceType, Type[AppType]],
        infra_dir: str = "infra",
        main_bicep: str = "main",
        output_dir: str = ".",
        user_access: bool = True,
        location: Optional[str] = None,
        name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
) -> Tuple[Union[ResourceType, AppType]]:
    ...
def provision(
        *__r,
        infra_dir: str = "infra",
        main_bicep: str = "main",
        output_dir: str = ".",
        user_access: bool = True,
        location: Optional[str] = None,
        name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
):
    deployment_name = name or _get_filename()
    working_dir = os.path.abspath(output_dir)
    export(
        *__r,
        infra_dir=infra_dir,
        main_bicep=main_bicep,
        output_dir=output_dir,
        user_access=user_access,
        location=location,
        name=deployment_name,
        config=config
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
        user_access: bool = True,
        location: Optional[str] = None,
        name: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
) -> None:
    if not __r:
        return
    deployment = list(__r)
    if not deployment:
        print("No resources to deploy.")
        return
    deployment_name = name or _get_filename()
    config = config or {}
    print("Building bicep...")
    working_dir = os.path.abspath(output_dir)
    infra_dir = os.path.join(working_dir, infra_dir)
    parameters: Dict[str, Parameter] = dict(GLOBAL_PARAMS)
    if not user_access:
        # If we don't want any local access, simply remove the parameter.
        parameters.pop('principalId')
    if location:
        parameters['location'].default = location

    fields: FieldsType = {}
    for resource in deployment:
        if isinstance(resource, Resource):
            resource.__bicep__(
                fields=fields,
                parameters=parameters,
                module_name=deployment_name
            )
        elif issubclass(resource, AzureInfrastructure):
            _parse_module(
                parameters=parameters,
                parent_component=resource,
                component=resource,
                component_resources=_get_component_resources(resource),
                component_fields=fields,
                module_name=deployment_name,
            )
    for field in fields.values():
        if field.add_defaults:
            field.add_defaults(field, parameters)
    add_extensions(fields, parameters)

    try:
        os.makedirs(infra_dir)
    except FileExistsError:
        pass
    bicep_main = os.path.join(infra_dir, f"{main_bicep}.bicep")
    with open(bicep_main, 'w') as main:
        main.write("targetScope = 'subscription'\n\n")
        module_params = {k: v for k,v in parameters.items() if v.module == 'main'}
        for parameter in module_params.values():
            main.write(parameter.__bicep__(config.get(parameter.name)))
        _write_resources(
            bicep=main,
            fields=list(fields.values()),
            parameters=parameters,
            module_parameters=module_params,
            deployment_name=deployment_name,
            infra_dir=infra_dir,
            config=config

        )
        main.write("\n")

    main_parameters = os.path.join(infra_dir, f"{main_bicep}.parameters.json")
    params_content = dict(_BICEP_PARAMS)
    params_content["parameters"] = {}
    for parameter in parameters.values():
        if isinstance(parameter, Parameter):
            params_content["parameters"].update(parameter.__obj__())
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
        module_name: str
) -> FieldsType:
    for name, r in component_resources.items():
        if r.infrastructure == component:
            r.__bicep__(
                component_fields,
                parameters=parameters,
                app_component=parent_component,
                attrname=attrname or name,
                module_name=module_name
            )
        else:
            _parse_module(
                parameters=parameters,
                parent_component=parent_component,
                component=r.infrastructure,
                component_resources=_get_component_resources(r.infrastructure),
                component_fields=component_fields,
                attrname=name,
                module_name=module_name
            )


def _write_resources(
        bicep: IO[str],
        fields: List[FieldType],
        parameters: Dict[str, Parameter],
        module_parameters: Dict[str, Parameter],
        infra_dir: str,
        deployment_name: str,
        config: Dict[str, Any],
        resource_group_scope: Optional[ResourceSymbol] = None,
) -> None:
    all_outputs = []
    for index, field in enumerate(fields):
        if field.resource == "Microsoft.Resources/resourceGroups":
            if field.existing:
                bicep.write(f"resource {field.symbol.value} '{field.resource}@{field.version}' existing = {{\n")
                bicep.write(f"  name: {resolve_value(field.properties['name'], **config)}\n")
                if 'scope' in field.properties:
                    bicep.write(f"  scope: {field.properties['scope'].value}\n")
                elif resource_group_scope:
                    bicep.write("  scope: subscription()\n")
                bicep.write("}\n\n")
                if resource_group_scope:
                    continue
            elif not resource_group_scope:
                bicep.write(f"resource {field.symbol.value} '{field.resource}@{field.version}' = {{\n")
                bicep.write(serialize_dict(field.properties, "  ", **config))
                bicep.write("}\n\n")
            else:
                # TODO Currently only supporting the creation of a single resource group,
                # however other existing resources may continue to reference other resource groups
                # by name
                raise ValueError("Cannot create additional resource group in deployment.")
            if fields[index + 1:]:
                bicep.write(f"module {deployment_name}_module '{deployment_name}.bicep' = {{\n")
                bicep.write(f"  name: '${{deployment().name}}_{deployment_name}'\n")
                bicep.write(f"  scope: {field.symbol.value}\n")
                bicep.write("  params: {\n")
                for parameter in module_parameters.values():
                    bicep.write(f"    {parameter.value}: {parameter.value}\n")
                bicep.write("  }\n")
                bicep.write("}\n")
                bicep_module = os.path.join(infra_dir, f"{deployment_name}.bicep")
                with open(bicep_module, 'w') as module:
                    for parameter in module_parameters.values():
                        module.write(f"param {parameter.name} {parameter.type}\n")
                    for name, parameter in parameters.items():
                        if name not in module_parameters:
                            module.write(parameter.__bicep__())
                            
                    module.write("\n")
                    outputs = _write_resources(
                        bicep=module,
                        fields=fields[index + 1:],
                        parameters=parameters,
                        infra_dir=infra_dir,
                        config=config,
                        module_parameters=module_parameters,
                        resource_group_scope=field.symbol,
                        deployment_name=None # TODO: support submodules/resource groups
                    )
                    for output, type in outputs:
                        bicep.write(f"output {output} {type} = {deployment_name}_module.outputs.{output}\n")
                    bicep.write("\n")
                break
        elif field.existing:
            bicep.write(f"resource {field.symbol.value} '{field.resource}@{field.version}' existing = {{\n")
            bicep.write(f"  name: {resolve_value(field.properties['name'], **config)}\n")
            if 'parent' in field.properties:
                bicep.write(f"  parent: {resolve_value(field.properties['parent'])}\n")
            elif field.resource_group != resource_group_scope:
                bicep.write(f"  scope: {field.resource_group.value}\n")
            bicep.write("}\n")
        else:
            bicep.write(f"resource {field.symbol.value} '{field.resource}@{field.version}' = {{\n")
            bicep.write(serialize_dict(field.properties, "  ", **config))
            bicep.write("}\n")
        bicep.write("\n")
        for output in field.outputs.values():
            all_outputs.append((output.name, output.type))
            bicep.write(output.__bicep__())
        bicep.write("\n\n")
    return all_outputs
