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

from ._resource import ResourceGroup, SubscriptionResourceId, PrincipalId, ResourceId
from ._roles import RoleAssignment, RoleAssignmentProperties
from ._identity import ManagedIdentity, UserAssignedIdentities
from ._servicebus import (
    ServiceBusNamespace,
    ServiceBusSku,
    ServiceBusRoleAssignments,
    AuthorizationRule,
    AuthorizationRuleProperties,
    ServiceBusTopic,
    TopicProperties,
    TopicSubsciprtion,
    SubscriptionProperties
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
from ._eventgrid import (
    EventSubscription,
    SystemTopics,
    SystemTopicProperties,
    EventSubscriptionProperties,
    EventSubscriptionIdentity,
    EventSubscriptionFilter,
    IdentityInfo,
    DeliveryWithResourceIdentity,
    ServiceBusTopicEventSubscriptionDestination,
    ServiceBusTopicEventSubscriptionDestinationProperties,
    RetryPolicy
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
        host: Literal['local', 'appservice'] = 'appservice',  # Union[Literal['appservice', 'container'], AppService, ContainerService]
        storage: Union[bool, StorageAccount] = True,
        fs: bool = False,  # Union[bool, DatalakeStorage]
        db: Union[bool, Literal['tables']] = 'tables', # Union[bool, Literal['tables', 'cosmos'], Tables, Cosmos]
        telemetry: bool = False,
        vault: bool = False,  # Union[bool, KeyVault]
        events: bool = True,
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
            self._identity = ManagedIdentity()
            rg.add(self._identity)
            self._storage = self._define_storage(kwargs)
            rg.add(self._storage)
            self._messaging = self._define_messaging(kwargs)
            rg.add(self._messaging)
            rg.add(self._define_events(kwargs))

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
                            role_definition_id=SubscriptionResourceId('Microsoft.Authorization/roleDefinitions', ServiceBusRoleAssignments.DATA_OWNER),
                            principal_id=PrincipalId(),
                            principal_type="User"
                        )
                    ),
                    RoleAssignment(
                        properties=RoleAssignmentProperties(
                            role_definition_id=SubscriptionResourceId('Microsoft.Authorization/roleDefinitions', ServiceBusRoleAssignments.DATA_SENDER),
                            principal_id=PrincipalId(self._identity),
                            principal_type="ServicePrincipal"
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
                        name="cm_internal_topic",
                        properties=TopicProperties(
                            default_message_time_to_live='P14D',
                            enable_batched_operations=True,
                            max_message_size_in_kilobytes=256,
                            requires_duplicate_detection=False,
                            status='Active',
                            support_ordering=True
                        ),
                        subscriptions=[
                            TopicSubsciprtion(
                                properties=SubscriptionProperties(
                                    dead_lettering_on_filter_evaluation_exceptions=True,
                                    dead_lettering_on_message_expiration=True,
                                    default_message_time_to_live='P14D',
                                    enable_batched_operations=True,
                                    is_client_affine=False,
                                    lock_duration='PT30S',
                                    max_delivery_count=10,
                                    requires_session=False,
                                    status='Active'
                                )
                            )
                        ]
                    ),
                    ServiceBusTopic(
                        name="cm_default_topic",
                        properties=TopicProperties(
                            default_message_time_to_live='P14D',
                            enable_batched_operations=True,
                            max_message_size_in_kilobytes=256,
                            requires_duplicate_detection=False,
                            status='Active',
                            support_ordering=True
                        ),
                        subscriptions=[
                            TopicSubsciprtion(
                                name="cm_default_subscription",
                                properties=SubscriptionProperties(
                                    dead_lettering_on_filter_evaluation_exceptions=True,
                                    dead_lettering_on_message_expiration=True,
                                    default_message_time_to_live='P14D',
                                    enable_batched_operations=True,
                                    is_client_affine=False,
                                    lock_duration='PT30S',
                                    max_delivery_count=10,
                                    requires_session=False,
                                    status='Active'
                                )
                            )
                        ]
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
                properties=Properties(
                    access_tier="Hot",
                    allow_blob_public_access=False,
                    is_hns_enabled=True
                ),
                identity=Identity(
                    type='UserAssigned',
                    user_assigned_identities=UserAssignedIdentities((self._identity, {}))),
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

    def _define_events(self, kwargs: Dict[str,Any]) -> Optional[ServiceBusNamespace]:
        events = kwargs.pop('events', True)
        if events is True:
            return SystemTopics(
                identity=IdentityInfo(
                    type="UserAssigned",
                    user_assigned_identities=UserAssignedIdentities((self._identity, {}))
                ),
                properties=SystemTopicProperties(
                    source=ResourceId(self._storage),
                    topic_type='Microsoft.Storage.StorageAccounts'
                ),
                subscriptions=[
                    EventSubscription(
                        properties=EventSubscriptionProperties(
                            delivery_with_resource_identity=DeliveryWithResourceIdentity(
                                identity=EventSubscriptionIdentity(
                                    type="UserAssigned",
                                    user_assigned_identity=ResourceId(self._identity)
                                ),
                                destination=ServiceBusTopicEventSubscriptionDestination(
                                    properties=ServiceBusTopicEventSubscriptionDestinationProperties(
                                        resource_id=ResourceId(self._messaging.topics[0])
                                    )
                                )
                            ),
                            event_delivery_schema='EventGridSchema',
                            filter=EventSubscriptionFilter(
                                included_event_types=[
                                    'Microsoft.Storage.BlobCreated',
                                    'Microsoft.Storage.BlobDeleted',
                                    'Microsoft.Storage.BlobRenamed',
                                ],
                                enable_advanced_filtering_on_arrays=True
                            ),
                            retry_policy=RetryPolicy(
                                max_delivery_attempts=30,
                                event_time_to_live_in_minutes=1440
                            )
                        )
                    )
                ]
            )

    def write(self, root_path: str):
        infra_dir = get_empty_directory(root_path, "infra")
        main_bicep = os.path.join(infra_dir, "main.bicep")
        with open(main_bicep, 'w') as main:
            main.write("targetScope = 'subscription'\n\n")
            main.write("@minLength(1)\n")
            main.write("@maxLength(64)\n")
            main.write("@description('AZD environment name')\n")
            main.write("param environmentName string\n\n")
            main.write("@description('Id of the user or app to assign application roles')\n")
            main.write("param principalId string\n\n")
            main.write("@minLength(1)\n")
            main.write("@description('Primary location for all resources')\n")
            main.write("param location string\n\n")
            main.write("var tags = { 'azd-env-name': environmentName }\n")
            main.write("var cloudmachineId = uniqueString(subscription().subscriptionId, environmentName, location)\n\n")

            for rg in self.groups:
                rg.write(main)
        params_json = os.path.join(infra_dir, "main.parameters.json")
        with open(params_json, 'w') as params:
            json.dump(self._params, params, indent=4)
