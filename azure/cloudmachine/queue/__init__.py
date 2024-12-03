# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import json
import os
import time
from abc import ABC, abstractmethod
from urllib.parse import quote
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass, field
from queue import Empty
from threading import Thread, Event
from functools import partial
from concurrent.futures import Executor, Future
import xml.etree.ElementTree as ET
from typing import IO, Any, AnyStr, Dict, Generator, List, Literal, Mapping, Optional, Protocol, Type, Union, overload

from azure.core.rest import HttpRequest, HttpResponse
from azure.core.tracing.decorator import distributed_trace
from azure.core.utils import case_insensitive_dict
from azure.core.exceptions import HttpResponseError

from .._httpclient._base import CloudMachineClientlet
from .._httpclient._utils import deserialize_rfc


@dataclass
class Message:
    id: str
    delivery_count: int
    enqueued: datetime
    expiry: datetime
    time_to_live: int
    content: AnyStr

    def __repr__(self):
        return repr(self.content)

    def __str__(self) -> str:
        return str(self.content)


@dataclass
class LockedMessage(Message):
    lock_token: str
    locked_until_utc: datetime
    _renew_interval: int
    _renew_lock: Optional[Thread] = None
    _stop_renew: Event = field(default_factory=Event)


class CloudMachineMessaging(CloudMachineClientlet, ABC):
    _id: str
    default_queue: str

    @abstractmethod
    def _renew_lock(self, message: LockedMessage, queue: Optional[str], **kwargs) -> None:
        ...

    @abstractmethod
    def full(self, *, queue: Optional[str] = None, **kwargs) -> Literal[False]:
        ...
    
    @abstractmethod
    def empty(self, *, queue: Optional[str] = None, **kwargs) -> bool:
        ...

    @abstractmethod
    def join(self, *, queue: Optional[str] = None, **kwargs) -> None:
        ...

    @abstractmethod
    def qsize(self, *, queue: Optional[str] = None, **kwargs) -> int:
        ...

    @abstractmethod
    def get(
            self,
            timeout: Optional[int] = None,
            *,
            queue: Optional[str] = None,
            lock: bool = True,
            renew_interval: int = 15,
            **kwargs
    ) -> Message:
        ...

    @abstractmethod
    def put(
            self,
            message: AnyStr,
            /, *,
            queue: Optional[str] = None,
            **kwargs
    ) -> Message:
        ...


    @abstractmethod
    def task_done(
            self,
            message: LockedMessage,
            /, *,
            queue: Optional[str] = None,
            delete: bool = True,
            **kwargs
    ) -> None:
        ...
       