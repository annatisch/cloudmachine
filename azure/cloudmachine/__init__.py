
from ._resource import Resource, DefaultAction
from ._provision import provision, export
from ._component import resource, AzureInfrastructure
from ._bicep.expressions import Parameter
from ._version import VERSION

MISSING = DefaultAction.MISSING

__version__ = VERSION
__all__ = [
    'provision',
    'export',
    'resource',
    'Resource',
    'AzureInfrastructure',
    'Parameter',
    'MISSING'
]
