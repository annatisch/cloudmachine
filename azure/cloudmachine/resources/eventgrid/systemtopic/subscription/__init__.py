from typing import TypedDict, Literal, List, Dict, Union

MODULE = "br/public:avm/res/event-grid/system-topic"
MODULE_RESOURCE = "Microsoft.EventGrid/systemTopics/eventSubscriptions"
MODULE_VERSION = "2023-12-15-preview"
MODULE_TAG = "0.4.0"


class SystemTopicSubscriptionParams(TypedDict, total=False):
    """"""
    destination: Dict[str, object]
    """The destination for the event subscription. (See https://learn.microsoft.com/en-us/azure/templates/microsoft.eventgrid/eventsubscriptions?pivots=deployment-language-bicep#eventsubscriptiondestination-objects for more information)."""
    name: str
    """The name of the Event Subscription."""
    deadLetterDestination: Dict[str, object]
    """Dead Letter Destination. (See https://learn.microsoft.com/en-us/azure/templates/microsoft.eventgrid/eventsubscriptions?pivots=deployment-language-bicep#deadletterdestination-objects for more information)."""
    deadLetterWithResourceIdentity: Dict[str, object]
    """Dead Letter with Resource Identity Configuration. (See https://learn.microsoft.com/en-us/azure/templates/microsoft.eventgrid/eventsubscriptions?pivots=deployment-language-bicep#deadletterwithresourceidentity-objects for more information)."""
    deliveryWithResourceIdentity: Dict[str, object]
    """Delivery with Resource Identity Configuration. (See https://learn.microsoft.com/en-us/azure/templates/microsoft.eventgrid/eventsubscriptions?pivots=deployment-language-bicep#deliverywithresourceidentity-objects for more information)."""
    eventDeliverySchema: Literal['CloudEventSchemaV1_0', 'CustomInputSchema', 'EventGridEvent', 'EventGridSchema']
    """The event delivery schema for the event subscription."""
    expirationTimeUtc: str
    """The expiration time for the event subscription. Format is ISO-8601 (yyyy-MM-ddTHH:mm:ssZ)."""
    filter: Dict[str, object]
    """The filter for the event subscription. (See https://learn.microsoft.com/en-us/azure/templates/microsoft.eventgrid/eventsubscriptions?pivots=deployment-language-bicep#eventsubscriptionfilter for more information)."""
    labels: List[str]
    """The list of user defined labels."""
    retryPolicy: Dict[str, object]
    """The retry policy for events. This can be used to configure the TTL and maximum number of delivery attempts and time to live for events."""


class SystemTopicSubscriptionKwargs(TypedDict, total=False):
    """"""
    destination: Union[str, Dict[str, object]]
    """The destination for the event subscription. (See https://learn.microsoft.com/en-us/azure/templates/microsoft.eventgrid/eventsubscriptions?pivots=deployment-language-bicep#eventsubscriptiondestination-objects for more information)."""
    deadletter_destination: Union[str, Dict[str, object]]
    """Dead Letter Destination. (See https://learn.microsoft.com/en-us/azure/templates/microsoft.eventgrid/eventsubscriptions?pivots=deployment-language-bicep#deadletterdestination-objects for more information)."""
    deadletter_with_resource_identity: Dict[str, object]
    """Dead Letter with Resource Identity Configuration. (See https://learn.microsoft.com/en-us/azure/templates/microsoft.eventgrid/eventsubscriptions?pivots=deployment-language-bicep#deadletterwithresourceidentity-objects for more information)."""
    delivery_with_resource_identity: Dict[str, object]
    """Delivery with Resource Identity Configuration. (See https://learn.microsoft.com/en-us/azure/templates/microsoft.eventgrid/eventsubscriptions?pivots=deployment-language-bicep#deliverywithresourceidentity-objects for more information)."""
    schema: Literal['CloudEventSchemaV1_0', 'CustomInputSchema', 'EventGridEvent', 'EventGridSchema']
    """The event delivery schema for the event subscription."""
    expiration: str
    # TODO: support datetimes
    """The expiration time for the event subscription. Format is ISO-8601 (yyyy-MM-ddTHH:mm:ssZ)."""
    filter: Union[List[str], Dict[str, object]]
    """The filter for the event subscription. (See https://learn.microsoft.com/en-us/azure/templates/microsoft.eventgrid/eventsubscriptions?pivots=deployment-language-bicep#eventsubscriptionfilter for more information)."""
    labels: List[str]
    """The list of user defined labels."""
    retry_policy: Dict[str, object]
    """The retry policy for events. This can be used to configure the TTL and maximum number of delivery attempts and time to live for events."""
