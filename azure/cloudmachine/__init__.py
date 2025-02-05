
from ._resource import Resource, DefaultAction
from ._provision import provision, export
from ._component import resource, reference, CloudMachine
from ._version import VERSION

MISSING = DefaultAction.MISSING
__version__ = VERSION
__all__ = [
    'provision',
    'export',
    'resource',
    'reference',
    'Resource',
    'CloudMachine',
]
