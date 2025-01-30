from typing import TYPE_CHECKING, Callable, Dict, List, Literal, Self, Unpack, overload, Optional, Any, Type

from ....._bicep.expressions import ModuleSymbol, Output, Parameter
from ....._setting import StoredPrioritizedSetting
from ....._resource import (
    Resource,
    FieldsType,
    FieldType,
    _convert_str_from_setting,
    _build_envs,
    _convert_to_str
)
from .._resource import _DEFAULT_SYSTEM_TOPIC, _SUPPORTED_SYSTEM_TOPICS

if TYPE_CHECKING:
    from .. import SystemTopicParams
    from . import SystemTopicSubscriptionParams, SystemTopicSubscriptionKwargs

_DEFAULT_SUBSCRIPTION: 'SystemTopicSubscriptionParams' = {}
_SUPPORTED_SUBSCRIPTION_DESTINATIONS = {
    # 'AzureFunction',
    # 'EventHub',
    # 'HybridConnection',
    # 'MonitorAlert',
    # 'NamespaceTopic',
    # 'PartnerDestination',
    # 'ServiceBusQueue',
    # 'ServiceBusTopic',
    'br/public:avm/res/storage/storage-account': 'StorageQueue',
    # 'WebHook'
}
_SUPPORTED_DEADLETTER_DESTINATIONS = {
    'br/public:avm/res/storage/storage-account': 'StorageBlob'
}

class SystemTopicSubscription(Resource):
    identifier: Literal["events:systemtopic:subscription"] = "events:systemtopic:subscription"
    module: Literal["br/public:avm/res/event-grid/system-topic"] = "br/public:avm/res/event-grid/system-topic"
    defaults: 'SystemTopicParams' = _DEFAULT_SYSTEM_TOPIC
    default_subscription: 'SystemTopicSubscriptionParams' = _DEFAULT_SUBSCRIPTION
    resource: Literal["Microsoft.EventGrid/systemTopics/eventSubscriptions"]
    properties: 'SystemTopicParams'

    def __init__(
            self,
            properties: Optional['SystemTopicSubscriptionParams'] = None,
            systemtopic_name: Optional[str] = None,
            subscription_name: Optional[str] = None,
            **kwargs: Unpack['SystemTopicSubscriptionKwargs']
    ) -> None:
        systemtopic_params: 'SystemTopicParams' = {}
        if systemtopic_name:
            systemtopic_params['name'] = systemtopic_name
        subscription_params: 'SystemTopicSubscriptionParams' = properties or {}
        if subscription_name:
            subscription_params['name'] = subscription_name
        if 'destination' in kwargs:
            subscription_params['destination'] = kwargs.pop('destination')
        if 'deadletter_destination' in kwargs:
            subscription_params['deadLetterDestination'] = kwargs.pop('deadletter_destination')
        if 'deadletter_with_resource_identity' in kwargs:
            subscription_params['deadLetterWithResourceIdentity'] = kwargs.pop('deadletter_with_resource_identity')
        if 'delivery_with_resource_identity' in kwargs:
            subscription_params['deliveryWithResourceIdentity'] = kwargs.pop('delivery_with_resource_identity')
        if 'schema' in kwargs:
            subscription_params['eventDeliverySchema'] = kwargs.pop('schema')
        if 'expiration' in kwargs:
            subscription_params['expirationTimeUtc'] = kwargs.pop('expiration')
        if 'filter' in kwargs:
            subscription_params['filter'] = kwargs.pop('filter')
        if 'labels' in kwargs:
            subscription_params['labels'] = kwargs.pop('labels')
        if 'retry_policy' in kwargs:
            subscription_params['retryPolicy'] = kwargs.pop('retry_policy')
        systemtopic_params["eventSubscriptions"] = [subscription_params]
        super().__init__(
            properties=systemtopic_params,
            service_prefix=["eventgrid_systemtopic"],
            **kwargs
        )
        self._supports_managed_identity = True
        self.subscription_name = StoredPrioritizedSetting(
            name='subscription_name',
            env_vars=_build_envs(self._prefixes, ['SUBSCRIPTION_NAME']),
            convert=_convert_str_from_setting,
            to_str=_convert_to_str,
        )
        self._settings['subscription_name'] = self.subscription_name

    @property
    def resource(self) -> str:
        from . import MODULE_RESOURCE
        return MODULE_RESOURCE

    @property
    def version(self) -> str:
        from . import MODULE_VERSION
        return MODULE_VERSION

    def _queue_destination(self, field: FieldType, parameters: Dict[str, Parameter]):
        destination = {}
        queues = field[1]['queueServices'].get('queues', [])
        if not queues:
            queues.append({'name': parameters['cloudmachineId']})
        destination['endpointType'] = _SUPPORTED_SUBSCRIPTION_DESTINATIONS[field[0]]
        destination['properties'] = {
            'queueName': queues[0]['name'],
            'queueMessageTimeToLiveInSeconds': -1,
            'resourceId': field[2].id
        }
        return destination

    def _merge_subscriptions(
            self,
            subscriptions: List['SystemTopicSubscriptionParams'],
            new_subscription: 'SystemTopicSubscriptionParams',
            *,
            fields: FieldsType,
            identity: Optional[ModuleSymbol],
            parameters: Dict[str, Parameter],
    ) -> List['SystemTopicSubscriptionParams']:
        subscription_name = new_subscription.get('name') or parameters['cloudmachineId']
        existing = False
        for subscription in subscriptions:
            if subscription['name'] == subscription_name:
                existing = True
                subscription.update(new_subscription)
                break
        if not existing:
            subscription = dict(self.default_subscription)
            subscription.update(new_subscription)
            subscriptions.append(subscription)

        # TODO: support deadletter destination + with identity
        if not subscription.get('deliveryWithResourceIdentity') and not subscription.get('destination'):
            destination = {}
            for resource in reversed(list(fields.values())):
                if resource[0] in _SUPPORTED_SUBSCRIPTION_DESTINATIONS:
                    # TODO: Assuming StorageQueue for now as it's the only supported
                    # this will need to be refactored once other destinations supported.
                    if 'queueServices' not in resource[1]:
                        continue
                    destination = self._queue_destination(resource, parameters)
                    if identity:
                        subscription['deliveryWithResourceIdentity'] = {
                            'identity': {
                                'type': 'UserAssigned',
                                'userAssignedIdentity': identity.id
                            },
                            'destination': destination
                        }
                    else:
                        subscription['destination'] = destination
                    break
            if not destination:
                raise ValueError(
                    "No resources found in component the can be destination for the system topic subscription."
                )
        elif isinstance(subscription['destination'], str):
            # TODO: Not sure if we should automation transfer "destination" to "destinationWithIdentity"
            try:
                field = fields[subscription['destination']]
                field[1]['queueServices']
                destination = self._queue_destination(field, parameters)
                if identity:
                    subscription['deliveryWithResourceIdentity'] = {
                        'identity': {
                            'type': 'UserAssigned',
                            'userAssignedIdentity': identity.id
                        },
                        'destination': destination
                    }
                else:
                    subscription['destination'] = destination
            except KeyError as e:
                raise ValueError(
                    "Cannot assign System Topic subscription destination to resource with "
                    f"attribute name: '{subscription['destination']}'"
                ) from e
        if isinstance(subscription.get('filter'), list):
            subscription['filter'] = {
                'includedEventTypes': subscription['filter']
            }
        return subscriptions

    def _merge_params(
            self,
            params: 'SystemTopicParams',
            *,
            symbol: ModuleSymbol,
            identity: Optional[ModuleSymbol],
            fields: FieldsType,
            attrname: Optional[str] = None,
            parameters: Dict[str, Parameter],
            **kwargs
    ) -> Dict[str, Output]:
        new_subscription = self.properties['eventSubscriptions'][0]
        subscriptions = self._merge_subscriptions(
            params.pop('eventSubscriptions', []),
            new_subscription,
            fields=fields,
            identity=identity,
            parameters=parameters

        )
        outputs = super()._merge_params(params, symbol=symbol, attrname=attrname, **kwargs)
        source = params.pop('source', None)
        if isinstance(source, str) and not source.startswith("/subscriptions/"):
            try:
                field = fields[source]
                source = field[2].id
                if 'topicType' not in params:
                    params['topicType'] = _SUPPORTED_SYSTEM_TOPICS[field[0]]
            except KeyError as e:
                raise ValueError("Cannot assign System Topic to resource with attribute name: '{source}'")
        elif not source:
            for resource in reversed(list(fields.values())):
                if resource[0] in _SUPPORTED_SYSTEM_TOPICS:
                    source = resource[2].id
                    if 'topicType' not in params:
                        params['topicType'] = _SUPPORTED_SYSTEM_TOPICS[resource[0]]
                    break
            if not source:
                raise ValueError("No resources found in component the can be sources for the system topic.")
        params['source'] = source
        params['eventSubscriptions'] = subscriptions
        return outputs

    def _update_managed_identities(
            self,
            params: Dict[str, Any],
            updated_params: Optional[Dict[str, Any]] = None,
            *,
            identity: Optional[ModuleSymbol] = None
    ) -> None:
        if updated_params:
            managed_identities = params.pop("managedIdentities", {})
            user_assigned_identities = managed_identities.pop("userAssignedResourcesIds", [])
            user_assigned_identities.extend(updated_params.get('userAssignedResourcesIds', []))
            managed_identities.update(updated_params)
            managed_identities["userAssignedResourcesIds"] = user_assigned_identities
            params['managedIdentities'] = managed_identities
        if identity and self._supports_managed_identity:
            if 'managedIdentities' not in params:
                params['managedIdentities'] = {
                    'userAssignedResourcesIds': [identity.id]
                }
            else:
                identities = params['managedIdentities'].get('userAssignedResourcesIds', [])
                existing = [i for i in identities if (hasattr(i, 'symbol') and i.symbol == identity) or i == identity]
                if not existing:
                    identities.append(identity.id)
                    params['managedIdentities']['userAssignedResourcesIds'] = identities
