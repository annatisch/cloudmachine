# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

import json
import os
import shutil
import copy
from typing import IO, Literal, Dict, Any, Optional, Union, Unpack, overload, List

from ._resource import ResourceGroup, SubscriptionResourceId, PrincipalId
from ._roles import RoleAssignment, RoleAssignmentProperties
from ._servicebus import (
    ServiceBusNamespace,
    ServiceBusSku,
    ServiceBusRoleAssignments,
    AuthorizationRule,
    AuthorizationRuleProperties,
    ServiceBusTopic,
    TopicProperties
)
from ._storage import (
    Container,
    StorageAccount,
    Sku,
    BlobServices,
    Properties,
    Identity,
    StorageRoleAssignments,
    Table,
    TableServices
)


# @dataclass
# class BlobStorage(Resource):
#     access_ties: Literal["Hot", "Cool", "Premium"] = "Hot"
#     allow_blob_public_acess: bool = True
#     allow_cross_tenant_replication: bool = True
#     allow_shared_key_access: bool = True
#     default_container: str = "default"
#     default_to_oauth_authentication: bool = True
#     delete_retention_policy: Dict[str, str] = {}
#     dns_endpoint_type: Literal["Standard", "AzureDnsZone"] = "Standard"
#     is_hns_enabled: bool = False
#     kind: str = "StorageV2"
#     minimum_tls_version: str = "TLS1_2"
#     supports_https_traffic_only: bool = True
#     public_network_access: Literal["Enabled", "Disabled"] = "Enabled"
#     sku: Dict[str, str] = {"name": "Standard_LRS"}
#     bypass: Optional[Literal["AzureServices"]] = "AzureServices"

DEFAULT_PARAMS = {
    "$schema": "https://schema.management.azure.com/schemas/2019-04-01/deploymentParameters.json#",
    "contentVersion": "1.0.0.0",
    "parameters": {
        "environmentName": {
            "value": "${AZURE_ENV_NAME}"
        },
        "principalId": {
            "value": "${AZURE_PRINCIPAL_ID}"
        },
        "cloudmachineName": {
            "value": None
        },
        "location": {
            "value": "${AZURE_LOCATION}"
        }
    }
}

def get_empty_directory(root_path: str, name: str) -> str:
    new_dir = os.path.join(root_path, name)
    try:
        shutil.rmtree(new_dir)
    except FileNotFoundError:
        pass
    os.makedirs(new_dir)

    return new_dir


class CloudMachineDeployment:

    id: str
    name: str
    groups: List[ResourceGroup]

    @overload
    def __init__(
        self,
        *,
        name: str,
        location: Optional[str] = None,
        host: Literal['appservice'] = 'appservice',  # Union[Literal['appservice', 'container'], AppService, ContainerService]
        storage: Union[bool, StorageAccount] = True,
        fs: bool = False,  # Union[bool, DatalakeStorage]
        db: Union[bool, Literal['tables']] = 'tables', # Union[bool, Literal['tables', 'cosmos'], Tables, Cosmos]
        telemetry: bool = False,
        vault: bool = False,  # Union[bool, KeyVault]
        events: bool = False,
        messaging: Union[bool, ServiceBusNamespace] = True,
    ) -> None:
        ...

    @overload
    def __init__(self, resources: List[ResourceGroup], /, *, name: str) -> None:
        ...
    
    def __init__(self, *args, **kwargs) -> None:
        self._name = kwargs['name']
        self._params = copy.deepcopy(DEFAULT_PARAMS)
        if args:
            self.groups = args[0]
        else:
            rg = ResourceGroup(
                friendly_name=self._name,
                tags={"abc": "def"},
            )
            rg.add(self._define_storage(kwargs))
            rg.add(self._define_messaging(kwargs))
            self.groups = [rg]

    def _define_messaging(self, kwargs: Dict[str,Any]) -> Optional[ServiceBusNamespace]:
        sb = kwargs.pop('messaging', True)
        if sb is True:
            return ServiceBusNamespace(
                sku=ServiceBusSku(
                    name='Standard',
                    tier='Standard'
                ),
                roles=[
                    RoleAssignment(
                        properties=RoleAssignmentProperties(
                            role_definition_id=SubscriptionResourceId('Microsoft.Authorization/roleDefinitions', StorageRoleAssignments.BLOB_DATA_CONTRIBUTOR),
                            principal_id=PrincipalId(),
                            principal_type="User"
                        )
                    )
                ],
                auth_rules=[
                    AuthorizationRule(
                        properties=AuthorizationRuleProperties(
                            rights=['Listen', 'Send', 'Manage']
                        )
                    )
                ],
                topics=[
                    ServiceBusTopic(
                        properties=TopicProperties(
                            default_message_time_to_live='P14D',
                            enable_batched_operations=True,
                            max_message_size_in_kilobytes=256,
                            requires_duplicate_detection=False,
                            status='Active',
                            support_ordering=True
                        )
                    )
                ]
            )

    def _define_storage(self, kwargs: Dict[str, Any]) -> Optional[StorageAccount]:
        storage = kwargs.pop('storage', True)
        if storage is True:
            return StorageAccount(
                friendly_name="anna",
                kind='StorageV2',
                sku=Sku(name='Standard_LRS'),
                blobs=BlobServices(
                    containers=[
                        Container(name="default")
                    ]
                ),
                tables=TableServices(
                    tables=[
                        Table(name="default")
                    ]
                ),
                properties=Properties(access_tier="Hot"),
                identity=Identity(type='SystemAssigned'),
                roles=[
                    RoleAssignment(
                        properties=RoleAssignmentProperties(
                            role_definition_id=SubscriptionResourceId('Microsoft.Authorization/roleDefinitions', StorageRoleAssignments.BLOB_DATA_CONTRIBUTOR),
                            principal_id=PrincipalId(),
                            principal_type="User"
                        )
                    ),
                    RoleAssignment(
                        properties=RoleAssignmentProperties(
                            role_definition_id=SubscriptionResourceId('Microsoft.Authorization/roleDefinitions', StorageRoleAssignments.TABLE_DATA_CONTRIBUTOR),
                            principal_id=PrincipalId(),
                            principal_type="User"
                        )
                    )
                ]
            )
        elif isinstance(storage, StorageAccount):
            return storage
        elif storage is False:
            return None
        else:
            raise TypeError(f"Unexpected type for 'storage' param: '{storage}'.")

    def write(self, root_path: str):
        infra_dir = get_empty_directory(root_path, "infra")
        main_bicep = os.path.join(infra_dir, "main.bicep")
        get_empty_directory(infra_dir, "core")
        with open(main_bicep, 'w') as main:
            main.write("targetScope = 'subscription'\n\n")
            main.write("@minLength(1)\n")
            main.write("@maxLength(64)\n")
            main.write("@description('AZD environment name')\n")
            main.write("param environmentName string\n\n")
            main.write("@description('Id of the user or app to assign application roles')\n")
            main.write("param principalId string\n\n")
            main.write("@minLength(1)\n")
            main.write("@maxLength(64)\n")
            main.write("@description('Cloud Machine name')\n")
            main.write("param cloudmachineName string\n\n")
            main.write("@minLength(1)\n")
            main.write("@description('Primary location for all resources')\n")
            main.write("param location string\n\n")
            main.write("var tags = { 'azd-env-name': environmentName, 'cloudmachine-name': cloudmachineName }\n")

            for rg in self.groups:
                rg.write(main)
        params_json = os.path.join(infra_dir, "main.parameters.json")
        with open(params_json, 'w') as params:
            self._params["parameters"]["cloudmachineName"]["value"] = self._name
            json.dump(self._params, params, indent=4)
