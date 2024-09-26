# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import functools
from typing import IO, Any, ClassVar, List, Mapping, Optional, Dict, Literal, Set, overload
from dataclasses import InitVar, dataclass, field

from ._resource import (
    _serialize_resource,
    Resource,
    LocatedResource,
    ResourceGroup,
    dataclass_model,
    generate_symbol,
    _UNSET,
    GuidName
)
