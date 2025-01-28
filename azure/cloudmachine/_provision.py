from inspect import get_annotations
from typing import IO, Any, Callable, Iterable, List, Literal, Optional, Type, Dict, Tuple, TYPE_CHECKING, TypeVar, Union
import os
import json
from collections import defaultdict

from ._bicep.utils import generate_name, resolve_value, serialize_dict, generate_suffix, serialize_list
from ._bicep.expressions import Expression, ModuleSymbol, Output, Parameter, ResourceGroupSymbol, Subscription, UniqueString, Variable
from ._resource import Resource, ResourcesType, FieldType, FieldsType
from .resources import UserAssignedIdentity, ResourceGroup, INFERRED_RESOURCE

_BICEP_PARAMS = {
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {}
}


def _get_component_resources(component: Type[Resource]) -> Dict[str, Resource]:
    return {k: getattr(component, k) for k, v in component.__dict__.items() if isinstance(v, Resource)}


AppType = TypeVar("AppType")
def provision(
        *__r: Type[AppType],
        infra_dir: str = "./infra",
        add_user_principal: bool = True,
        location: Optional[str] = None,
) -> AppType:
    export(
        *__r,
        infra_dir=infra_dir,
        add_user_principal=add_user_principal,
        location=location
    )
    # TODO: Run azd provision command.
    return __r()


def export(
        *__r: Type,
        infra_dir: str = "./infra",
        add_user_principal: bool = True,
        location: Optional[str] = None,
) -> None:
    print("Building bicep...")
    infra_dir = os.path.abspath(infra_dir)
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
        )
    try:
        os.makedirs(infra_dir)
    except FileExistsError:
        pass
    all_outputs = []
    bicep_main = os.path.join(infra_dir, "main.bicep")
    with open(bicep_main, 'w') as main:
        main.write("targetScope = 'subscription'\n\n")
        for parameter in parameters.values():
            main.write(parameter.main_declare())

        for app in __r:
            module_parameters = dict(parameters)
            module_name = app.__name__.lower()
            default_resource_group = ResourceGroup()
            default_resource_group.component = app
            default_identity = UserAssignedIdentity()
            default_identity.component = app
            resources: ResourcesType = defaultdict(dict)

            tags = Variable('tags', 'object', { 'azd-env-name': module_parameters['environmentName'] })
            cloudmachine_id = Variable(
                'cloudmachineId',
                'string',
                UniqueString(Subscription().subscription_id, module_name, module_parameters["location"]),
                description="Unique identifier for creating default resource names"
            )
            symbol = Expression(f"module_{generate_suffix()}")
            main.write(f"module {symbol.resolve()} '{module_name}.bicep' = {{\n")
            main.write(f"  name: '${{deployment().name}}_{symbol.resolve()}'\n")
            main.write("  params: {\n")
            main.write(serialize_dict(module_parameters, "    "))
            main.write("  }\n")
            main.write("}\n")
            bicep_module = os.path.join(infra_dir, f"{module_name}.bicep")
            with open(bicep_module, 'w') as module:
                module.write("targetScope = 'subscription'\n\n")
                for parameter in module_parameters.values():
                    module.write(parameter.module_declare())
                module.write(tags.main_declare())
                module.write(cloudmachine_id.main_declare())
                module_parameters['tags'] = tags
                module_parameters['cloudmachineId'] = cloudmachine_id

                fields: FieldsType = []
                default_resource_group.__bicep__(
                    fields,
                    resources,
                    parameters=module_parameters,
                    app_component=app
                )
                default_identity.__bicep__(
                    fields,
                    resources,
                    parameters=module_parameters,
                    app_component=app
                )
                _parse_module(
                    resources=resources,
                    parameters=module_parameters,
                    component=app,
                    parent_component=app,
                    component_resources=_get_component_resources(app),
                    fields=fields,
                )
                module_outputs = _write_resources(
                    bicep=module,
                    resources=resources,
                    parameters=module_parameters
                )
            for output in module_outputs:
                if output in all_outputs:
                    # TODO: This will mostly happen with identity and AZURE_CLIENT_ID, so need
                    # a solution for this.
                    main.write("// Error - duplicate output\n")
                    main.write(f"// output {output} string = {symbol.resolve()}.outputs.{output}\n")
                else:
                    all_outputs.append(output)
                    main.write(f"output {output} string = {symbol.resolve()}.outputs.{output}\n")
            main.write("\n")

    main_parameters = os.path.join(infra_dir, "main.parameters.json")
    params_content = dict(_BICEP_PARAMS)
    for parameter in parameters.values():
        if isinstance(parameter, Parameter):
            params_content["parameters"].update(parameter.parameter())
    with open(main_parameters, 'w') as params_json:
        json.dump(params_content, params_json, indent=4)


def _find_resource(
        module: str,
        fields: FieldsType,
) -> Optional[FieldType]:
    try:
        return [f for f in reversed(fields) if f[0].startswith(module)][0]
    except IndexError:
        return None

def _parse_module(
        *,
        resources: ResourcesType,
        parameters: Dict[str, Parameter],
        component: Type,
        parent_component: Type,
        component_resources: Dict[str, Resource],
        fields: FieldsType,
        attrname: Optional[str] = None,
) -> Optional[FieldType]:
    component_fields = list(fields)
    attrs = {}
    for name, r in component_resources.items():
        if r.component == component:
            field = r.__bicep__(
                component_fields,
                resources,
                parameters=parameters,
                app_component=parent_component,
                attrname=attrname or name
            )
            if field:
                attrs[name] = field
        else:
            # Well make a copy of the initial fields so we can carry over the default
            # resource group and identity without modifying it for other components.
            new_fields = list(fields)

            # We'll check if the component has any parameters.
            # These will be fields that are type-annotated with a valid Resource type, but either not
            # in the class __dict__ or have a default of None.
            annotations = get_annotations(r.component)
            for attr, annotation in annotations.items():
                if annotation.__name__ in INFERRED_RESOURCE and r.component.__dict__.get(attr) is None:
                    # For each parameter field, we will attempt to populate it with a resource from elsewhere
                    # in the component, beased on inferring the resource type from the type hint.
                    # This check is based on matching module, not exact resource, so if the parameter is
                    # for a Blob Container, we will get a match with any Storage Account.
                    inferred_resource = INFERRED_RESOURCE[annotation.__name__]
                    resource_as_parameter = _find_resource(inferred_resource.module, component_fields)
                    if resource_as_parameter:
                        new_fields.append(resource_as_parameter)
                    elif attr in r.component.__dict__:
                        # Parameter field has a default of None, so it's not required.
                        continue
                    else:
                        raise ValueError(
                            "Unable to add component {}, missing input resource type: {}".format(
                                r.component.__name__,
                                inferred_resource.resource
                            )
                        )
                
            referenced_fields = _parse_module(
                resources=resources,
                parameters=parameters,
                component=r.component,
                parent_component=parent_component,
                component_resources=_get_component_resources(r.component),
                fields=new_fields,
                attrname=name,
            )
            if r.attr in referenced_fields:
                component_fields.append((r.module, *referenced_fields[r.attr]))
                attrs[name] = referenced_fields[r.attr]
    return attrs


def _write_resources(
        bicep: IO[str],
        resources: ResourcesType,
        parameters: Dict[str, Parameter],
) -> List[str]:
    all_outputs = []
    for rg_name, rg_contents in resources.items():
        bicep.write(rg_name.declare())
        for (resource, _), (params, symbol, outputs, _) in rg_contents.items():
            if resource.startswith('br/public:'):
                bicep.write(f"module {symbol.resolve()} '{resource}' = {{\n")
                bicep.write(f"  name: '${{deployment().name}}_{symbol.resolve()}'\n")
                if 'resources/resource-group' not in resource:
                    bicep.write(f"  scope: resourceGroup({rg_name.varname.resolve()})\n")
                bicep.write("  params: {\n")
                bicep.write(serialize_dict(params, "    ", **parameters))
                bicep.write("  }\n")
                bicep.write("}\n")
            elif resource.startswith('Microsoft.'):
                bicep.write(f"resource {symbol.resolve()} '{resource}' = {{\n")
                bicep.write(serialize_dict(params, "  ", **parameters))
                bicep.write("}\n")
            for varname, output in outputs.items():
                all_outputs.append(varname)
                bicep.write(f"output {varname} string = {resolve_value(output)}\n")
            bicep.write("\n")
    return all_outputs
