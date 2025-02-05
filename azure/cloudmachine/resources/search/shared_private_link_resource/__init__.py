from typing import TypedDict
from typing_extensions import Required


class SharedPrivateLinkResource(TypedDict, total=False):
    """"""
    groupId: Required[str]
    """The group ID from the provider of resource the shared private link resource is for."""
    name: Required[str]
    """The name of the shared private link resource managed by the Azure Cognitive Search service within the specified resource group."""
    privateLinkResourceId: Required[str]
    """The resource ID of the resource the shared private link resource is for."""
    requestMessage: Required[str]
    """The request message for requesting approval of the shared private link resource."""
    resourceRegion: str
    """Can be used to specify the Azure Resource Manager location of the resource to which a shared private link is to be created. This is only required for those resources whose DNS configuration are regional (such as Azure Kubernetes Service)."""
