from typing import TypedDict, Literal, List, Dict, Union
from typing_extensions import Required


class ManagedIdentity(TypedDict, total=False):
    """The managed identity definition for this resource."""
    systemAssigned: bool
    """Enables system assigned managed identity on the resource."""
    userAssignedResourceIds: List[object]
    """The resource ID(s) to assign to the resource. Required if a user assigned identity is used for encryption."""


class ComputeParams(TypedDict, total=False):
    """"""
    computeType: Required[Union[Literal['AKS', 'AmlCompute', 'ComputeInstance', 'Databricks', 'DataFactory', 'DataLakeAnalytics', 'HDInsight', 'Kubernetes', 'SynapseSpark', 'VirtualMachine']]]
    """Set the object type."""
    name: Required[str]
    """Name of the compute."""
    computeLocation: str
    """Location for the underlying compute. Ignored when attaching a compute resource, i.e. when you provide a resource ID."""
    deployCompute: bool
    """Flag to specify whether to deploy the compute. Required only for attach (i.e. providing a resource ID), as in this case the operation is not idempotent, i.e. a second deployment will fail. Therefore, this flag needs to be set to "false" as long as the compute resource exists."""
    description: str
    """The description of the Machine Learning compute."""
    disableLocalAuth: bool
    """Opt-out of local authentication and ensure customers can use only MSI and AAD exclusively for authentication."""
    location: str
    """Specifies the location of the resource."""
    managedIdentities: 'ManagedIdentity'
    """The managed identity definition for this resource."""
    properties: Dict[str, object]
    """The properties of the compute. Will be ignored in case "resourceId" is set."""
    resourceId: str
    """ARM resource ID of the underlying compute."""
    sku: Literal['Basic', 'Free', 'Premium', 'Standard']
    """Specifies the sku, also referred as "edition". Required for creating a compute resource."""
    tags: Dict[str, object]
    """Contains resource tags defined as key-value pairs. Ignored when attaching a compute resource, i.e. when you provide a resource ID."""


class ComputeKwargs(TypedDict, total=False):
    """"""
    compute_type: Union[Literal['AKS', 'AmlCompute', 'ComputeInstance', 'Databricks', 'DataFactory', 'DataLakeAnalytics', 'HDInsight', 'Kubernetes', 'SynapseSpark', 'VirtualMachine']]
    """Set the object type."""
    compute_location: str
    """Location for the underlying compute. Ignored when attaching a compute resource, i.e. when you provide a resource ID."""
    deploy_compute: bool
    """Flag to specify whether to deploy the compute. Required only for attach (i.e. providing a resource ID), as in this case the operation is not idempotent, i.e. a second deployment will fail. Therefore, this flag needs to be set to "false" as long as the compute resource exists."""
    description: str
    """The description of the Machine Learning compute."""
    disable_local_auth: bool
    """Opt-out of local authentication and ensure customers can use only MSI and AAD exclusively for authentication."""
    location: str
    """Specifies the location of the resource."""
    managed_dentities: 'ManagedIdentity'
    """The managed identity definition for this resource."""
    properties: Dict[str, object]
    """The properties of the compute. Will be ignored in case "resourceId" is set."""
    resource_Id: str
    """ARM resource ID of the underlying compute."""
    sku: Literal['Basic', 'Free', 'Premium', 'Standard']
    """Specifies the sku, also referred as "edition". Required for creating a compute resource."""
    tags: Dict[str, object]
    """Contains resource tags defined as key-value pairs. Ignored when attaching a compute resource, i.e. when you provide a resource ID."""
