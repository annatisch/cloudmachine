# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from typing import IO, Any, ClassVar, List, Mapping, Optional, Dict, Literal, Set, Union, overload
from dataclasses import InitVar, dataclass, field

from ._identity import UserAssignedIdentities
from ._resource import (
    Resource,
    LocatedResource,
    dataclass_model,
    generate_symbol,
    _UNSET,
)

@dataclass_model
class EventSubscriptionIdentity:
    type: Literal['SystemAssigned', 'UserAssigned'] = field(metadata={'rest': 'type'})
    user_assigned_identity: Optional[Union[str, LocatedResource]] = field(default=_UNSET, metadata={'rest': 'userAssignedIdentity'})


@dataclass_model
class StorageBlobDeadLetterDestinationProperties:
    blob_container_name: str = field(metadata={'rest': 'blobContainerName'})
    resource_id: Union[str, Resource] = field(metadata={'rest': 'resourceId'})


@dataclass_model
class StorageBlobDeadLetterDestination:
    endpoint_type: Literal['StorageBlob'] = field(default='StorageBlob', init=False, metadata={'rest': 'endpointType'})
    properties: StorageBlobDeadLetterDestinationProperties = field(metadata={'rest': 'properties'})


@dataclass_model
class DeadLetterWithResourceIdentity:
    dead_letter_destination: StorageBlobDeadLetterDestination = field(metadata={'rest': 'deadLetterDestination'})
    identity: EventSubscriptionIdentity = field(metadata={'rest': 'identity'})


@dataclass_model
class DynamicDeliveryAttributeMappingProperties:
    source_field: str = field(metadata={'rest': 'sourceField'})


@dataclass_model
class DynamicDeliveryAttributeMapping:
    type: Literal['Dynamic'] = field(default='Dynamic', init=False, metadata={'rest': 'type'})
    properties: DynamicDeliveryAttributeMappingProperties = field(metadata={'rest': 'properties'})


@dataclass_model
class StaticDeliveryAttributeMappingProperties:
    is_secret: bool = field(metadata={'rest': 'isSecret'})
    value: str = field(metadata={'rest': 'value'})


@dataclass_model
class StaticDeliveryAttributeMapping:
    type: Literal['Static'] = field(default='Static', init=False, metadata={'rest': 'type'})
    properties: StaticDeliveryAttributeMappingProperties = field(metadata={'rest': 'properties'})


@dataclass_model
class AzureFunctionEventSubscriptionDestinationProperties:
    delivery_attribute_mappings: Optional[List[Union[DynamicDeliveryAttributeMapping, StaticDeliveryAttributeMapping]]] = field(default=_UNSET, metadata={'rest': 'deliveryAttributeMappings'})
    max_events_per_batch: Optional[int] = field(default=_UNSET, metadata={'rest': 'maxEventsPerBatch'})
    preferred_batch_size_in_kilobytes: Optional[int] = field(default=_UNSET, metadata={'rest': 'preferredBatchSizeInKilobytes'})
    resource_id: Union[str, LocatedResource] = field(metadata={'rest': 'resourceId'})


@dataclass_model
class AzureFunctionEventSubscriptionDestination:
    endpoint_type: Literal['AzureFunction'] = field(default='AzureFunction', init=False, metadata={'rest': 'endpointType'})
    properties: AzureFunctionEventSubscriptionDestinationProperties = field(metadata={'rest': 'properties'})


@dataclass_model
class EventHubEventSubscriptionDestinationProperties:
    delivery_attribute_mappings: Optional[List[Union[DynamicDeliveryAttributeMapping, StaticDeliveryAttributeMapping]]] = field(default=_UNSET, metadata={'rest': 'deliveryAttributeMappings'})
    resource_id: Union[str, LocatedResource] = field(metadata={'rest': 'resourceId'})


@dataclass_model
class EventHubEventSubscriptionDestination:
    endpoint_type: Literal['EventHub'] = field(default='EventHub', init=False, metadata={'rest': 'endpointType'})
    properties: EventHubEventSubscriptionDestinationProperties = field(metadata={'rest': 'properties'})


@dataclass_model
class HybridConnectionEventSubscriptionDestinationProperties:
    delivery_attribute_mappings: Optional[List[Union[DynamicDeliveryAttributeMapping, StaticDeliveryAttributeMapping]]] = field(default=_UNSET, metadata={'rest': 'deliveryAttributeMappings'})
    resource_id: Union[str, LocatedResource] = field(metadata={'rest': 'resourceId'})


@dataclass_model
class HybridConnectionEventSubscriptionDestination:
    endpoint_type: Literal['HybridConnection'] = field(default='HybridConnection', init=False, metadata={'rest': 'endpointType'})
    properties: HybridConnectionEventSubscriptionDestinationProperties = field(metadata={'rest': 'properties'})


@dataclass_model
class MonitorAlertEventSubscriptionDestinationProperties:
    action_groups: Optional[List[Union[str, LocatedResource]]] = field(default=_UNSET, metadata={'rest': 'actionGroups'})
    description: Optional[str] = field(default=_UNSET, metadata={'rest': 'description'})
    severity: Literal['Sev0', 'Sev1', 'Sev2', 'Sev3', 'Sev4'] = field(metadata={'rest': 'severity'})


@dataclass_model
class MonitorAlertEventSubscriptionDestination:
    endpoint_type: Literal['MonitorAlert'] = field(default='MonitorAlert', init=False, metadata={'rest': 'endpointType'})
    properties: MonitorAlertEventSubscriptionDestinationProperties = field(metadata={'rest': 'properties'})


@dataclass_model
class NamespaceTopicEventSubscriptionDestinationProperties:
    resource_id: Union[str, LocatedResource] = field(metadata={'rest': 'resourceId'})


@dataclass_model
class NamespaceTopicEventSubscriptionDestination:
    endpoint_type: Literal['NamespaceTopic'] = field(default='NamespaceTopic', init=False, metadata={'rest': 'endpointType'})
    properties: NamespaceTopicEventSubscriptionDestinationProperties = field(metadata={'rest': 'properties'})


@dataclass_model
class PartnerEventSubscriptionDestinationProperties:
    resource_id: Union[str, LocatedResource] = field(metadata={'rest': 'resourceId'})


@dataclass_model
class PartnerEventSubscriptionDestination:
    endpoint_type: Literal['PartnerDestination'] = field(default='PartnerDestination', init=False, metadata={'rest': 'endpointType'})
    properties: PartnerEventSubscriptionDestinationProperties = field(metadata={'rest': 'properties'})


@dataclass_model
class ServiceBusQueueEventSubscriptionDestinationProperties:
    delivery_attribute_mappings: Optional[List[Union[DynamicDeliveryAttributeMapping, StaticDeliveryAttributeMapping]]] = field(default=_UNSET, metadata={'rest': 'deliveryAttributeMappings'})
    resource_id: Union[str, LocatedResource] = field(metadata={'rest': 'resourceId'})


@dataclass_model
class ServiceBusQueueEventSubscriptionDestination:
    endpoint_type: Literal['ServiceBusQueue'] = field(default='ServiceBusQueue', init=False, metadata={'rest': 'endpointType'})
    properties: ServiceBusQueueEventSubscriptionDestinationProperties = field(metadata={'rest': 'properties'})


@dataclass_model
class ServiceBusTopicEventSubscriptionDestinationProperties:
    delivery_attribute_mappings: Optional[List[Union[DynamicDeliveryAttributeMapping, StaticDeliveryAttributeMapping]]] = field(default=_UNSET, metadata={'rest': 'deliveryAttributeMappings'})
    resource_id: Union[str, LocatedResource] = field(metadata={'rest': 'resourceId'})


@dataclass_model
class ServiceBusTopicEventSubscriptionDestination:
    endpoint_type: Literal['ServiceBusTopic'] = field(default='ServiceBusTopic', init=False, metadata={'rest': 'endpointType'})
    properties: ServiceBusTopicEventSubscriptionDestinationProperties = field(metadata={'rest': 'properties'})


@dataclass_model
class StorageQueueEventSubscriptionDestinationProperties:
    resource_id: Union[str, LocatedResource] = field(metadata={'rest': 'resourceId'})
    queue_name: str = field(metadata={'rest': 'queueName'})
    queue_message_time_to_live_in_seconds: Optional[int] = field(default=_UNSET, metadata={'rest': 'queueMessageTimeToLiveInSeconds'})


@dataclass_model
class StorageQueueEventSubscriptionDestination:
    endpoint_type: Literal['StorageQueue'] = field(default='StorageQueue', init=False, metadata={'rest': 'endpointType'})
    properties: StorageQueueEventSubscriptionDestinationProperties = field(metadata={'rest': 'properties'})


@dataclass_model
class WebHookEventSubscriptionDestinationProperties:
    azure_active_directory_application_id_or_uri: Optional[str] = field(metadata={'rest': 'azureActiveDirectoryApplicationIdOrUri'})
    azure_active_directory_tenant_id: Optional[str] = field(default=_UNSET, metadata={'rest': 'azureActiveDirectoryTenantId'})
    delivery_attribute_mappings: Optional[List[Union[DynamicDeliveryAttributeMapping, StaticDeliveryAttributeMapping]]] = field(default=_UNSET, metadata={'rest': 'deliveryAttributeMappings'})
    endpoint_url: Optional[str] = field(default=_UNSET, metadata={'rest': 'endpointUrl'})
    max_events_per_batch: Optional[int] = field(default=_UNSET, metadata={'rest': 'maxEventsPerBatch'})
    minimum_tls_version_allowed: Optional[Literal['1.0', '1.1', '1.2']] = field(default=_UNSET, metadata={'rest': 'minimumTlsVersionAllowed'})
    preferred_batch_size_in_kilobytes: Optional[int] = field(default=_UNSET, metadata={'rest': 'preferredBatchSizeInKilobytes'})

@dataclass_model
class WebHookEventSubscriptionDestination:
    endpoint_type: Literal['WebHook'] = field(default='WebHook', init=False, metadata={'rest': 'endpointType'})
    properties: WebHookEventSubscriptionDestinationProperties = field(metadata={'rest': 'properties'})

@dataclass_model
class DeliveryWithResourceIdentity:
    destination: Union[PartnerEventSubscriptionDestination, WebHookEventSubscriptionDestination, EventHubEventSubscriptionDestination, MonitorAlertEventSubscriptionDestination, StorageQueueEventSubscriptionDestination, AzureFunctionEventSubscriptionDestination, NamespaceTopicEventSubscriptionDestination, ServiceBusQueueEventSubscriptionDestination, ServiceBusTopicEventSubscriptionDestination, HybridConnectionEventSubscriptionDestination] = field(metadata={'rest': 'destination'})
    identity: EventSubscriptionIdentity = field(metadata={'rest': 'identity'})


@dataclass_model
class EventSubscriptionProperties:
    dead_letter_destination: Optional[StorageBlobDeadLetterDestination] = field(default=_UNSET, metadata={'rest': 'deadLetterDestination'})
    dead_letter_with_resource_identity: Optional[DeadLetterWithResourceIdentity] = field(default=_UNSET, metadata={'rest': 'deadLetterWithResourceIdentity'})
    delivery_with_resource_identity: Optional[DeliveryWithResourceIdentity] = field(default=_UNSET, metadata={'rest': 'deliveryWithResourceIdentity'})
    destination: Optional[Union[PartnerEventSubscriptionDestination, WebHookEventSubscriptionDestination, EventHubEventSubscriptionDestination, MonitorAlertEventSubscriptionDestination, StorageQueueEventSubscriptionDestination, AzureFunctionEventSubscriptionDestination, NamespaceTopicEventSubscriptionDestination, ServiceBusQueueEventSubscriptionDestination, ServiceBusTopicEventSubscriptionDestination, HybridConnectionEventSubscriptionDestination]] = field(default=_UNSET, metadata={'rest': 'destination'})
    event_delivery_schema: Literal['CloudEventSchemaV1_0', 'CustomInputSchema', 'EventGridSchema'] = field(metadata={'rest': 'eventDeliverySchema'})
    expiration_time_utc: Optional[str] = field(default=_UNSET, metadata={'rest': 'expirationTimeUtc'})
    filter = field(default=_UNSET, metadata={'rest': 'filter'})
    labels: Optional[List[str]] = field(default=_UNSET, metadata={'rest': 'labels'})
    retry_policy = field(default=_UNSET, metadata={'rest': 'retryPolicy'})


@dataclass_model
class EventSubscription(Resource):
    properties: Optional[EventSubscriptionProperties] = field(default=_UNSET, metadata={'rest': 'properties'})
    _resource: ClassVar[Literal['Microsoft.EventGrid/systemTopics/eventSubscriptions']] = 'Microsoft.EventGrid/systemTopics/eventSubscriptions'
    _version: ClassVar[str] = '2022-06-15'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("egsub"), init=False, repr=False)


@dataclass_model
class IdentityInfo:
    principal_id: str = field(default=_UNSET, metadata={'rest': 'identity'})
    tenant_id: str = field(default=_UNSET, metadata={'rest': 'tenantId'})
    type: Literal['None', 'SystemAssigned', 'SystemAssigned,UserAssigned', 'UserAssigned'] = field(metadata={'rest': 'type'})
    user_assigned_identities: Optional[UserAssignedIdentities] = field(default=_UNSET, metadata={'rest': 'userAssignedIdentities'})


@dataclass_model
class SystemTopicProperties:
    source: str = field(metadata={'rest': 'source'})
    topic_type: str = field(metadata={'rest': 'topicType'})


@dataclass_model
class SystemTopics(LocatedResource):
    identity: Optional[IdentityInfo] = field(default=_UNSET, metadata={'rest': 'identity'})
    properties: Optional[SystemTopicProperties] = field(default=_UNSET, metadata={'rest': 'properties'})
    #subscriptions: List[ServiceBusTopic] = field(default_factory=list, metadata={'rest': _SKIP})
    _resource: ClassVar[Literal['Microsoft.EventGrid/systemTopics']] = 'Microsoft.EventGrid/systemTopics'
    _version: ClassVar[str] = '2022-06-15'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("egst"), init=False, repr=False)
