
from ._resource import Resource, DefaultResource
from ._provision import provision, export
from ._component import resource, client, AzureInfrastructure, AzureApp
from ._bicep.expressions import Parameter
from ._version import VERSION

MISSING = DefaultResource.MISSING

__version__ = VERSION
__all__ = [
    'provision',
    'export',
    'resource',
    'client',
    'Resource',
    'AzureInfrastructure',
    'AzureApp',
    'Parameter',
    'MISSING'
]
