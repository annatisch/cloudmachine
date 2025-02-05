from typing import TYPE_CHECKING, TypedDict, Literal, List, Dict, Union
from typing_extensions import Required

MODULE = "br/public:avm/res/cognitive-services/account"
MODULE_RESOURCE = "Microsoft.CognitiveServices/accounts/deployments"
MODULE_VERSION = "2023-05-01"
MODULE_TAG = "0.9.0"


class CustomerManagedKey(TypedDict, total=False):
    """The customer managed key definition."""
    keyName: Required[str]
    """The name of the customer managed key to use for encryption."""
    keyVaultResourceId: Required[str]
    """The resource ID of a key vault to reference a customer managed key for encryption from."""
    keyVersion: str
    """The version of the customer managed key to reference for encryption. If not provided, the deployment will use the latest version available at deployment time."""
    userAssignedIdentityResourceId: str
    """User assigned identity to use when fetching the customer managed key. Required if no system assigned identity is available for use."""


class Model(TypedDict, total=False):
    """Properties of Cognitive Services account deployment model."""
    format: Required[str]
    """The format of Cognitive Services account deployment model."""
    name: Required[str]
    """The name of Cognitive Services account deployment model."""
    version: Required[str]
    """The version of Cognitive Services account deployment model."""


class Sku(TypedDict, total=False):
    """The resource model definition representing SKU."""
    name: Required[str]
    """The name of the resource model definition representing SKU."""
    capacity: int
    """The capacity of the resource model definition representing SKU."""


class DeploymentParams(TypedDict, total=False):
    """Array of deployments about cognitive service accounts to create."""
    model: Required['Model']
    """Properties of Cognitive Services account deployment model."""
    name: str
    """Specify the name of cognitive service account deployment."""
    raiPolicyName: str
    """The name of RAI policy."""
    sku: 'Sku'
    """The resource model definition representing SKU."""
