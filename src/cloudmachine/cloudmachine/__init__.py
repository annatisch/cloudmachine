# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License in the project root for
# license information.
# --------------------------------------------------------------------------

from ._version import VERSION

__version__ = VERSION

from ._client import CloudMachineStorage

__all__ = [
    "CloudMachineStorage"
]
