# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import json
import os
import time
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

from . import CloudMachineMessaging, Message, LockedMessage
from .._httpclient._utils import deserialize_rfc


class CloudMachineServiceBus(CloudMachineMessaging):
    _id: Literal["servicebus"] = "servicebus"
    default_queue: str = "cm_default_topic/cm_default_subscription"

    def _get_queue_name(self, queue: Optional[str]) -> str:
        queue = queue or self.default_queue
        try:
            topic, subscription = queue.split('/')
            return f"{topic}/subscriptions/{subscription}"
        except ValueError:
            return queue

    def _load_response(self, response: HttpResponse) -> ET:
        return ET.fromstring(response.read().decode('utf-8'))

    def _renew_lock(self, message: LockedMessage, queue: str, **kwargs) -> None:
        while not message._stop_renew.is_set():
            time.sleep(message._renew_interval)
            if message._stop_renew.is_set():
                return

            request = build_message_process_request(
                "POST",
                queue,
                message.id,
                message.lock_token
            )
            try:
                self._send_request(request, **kwargs)
            except HttpResponseError as e:
                if e.status_code == 404:
                    return
                # log renewal exception
                print("Lock renew failed", e)
                return

    def full(self, **kwargs) -> Literal[False]:
        return False
    
    def empty(self, **kwargs) -> bool:
        return not self.qsize(**kwargs) > 0

    def join(self, **kwargs) -> None:
        while self.qsize(**kwargs) > 0:
            time.sleep(0.1)

    @overload
    def qsize(
            self,
            *,
            queue: Optional[str] = None,
            wait: Literal[True] = True,
            **kwargs
    ) -> int:
        ...
    @overload
    def qsize(
            self,
            *,
            queue: Optional[str] = None,
            wait: Literal[False],
            **kwargs
    ) -> Future[int]:
        ...
    @distributed_trace
    def qsize(
            self,
            *,
            queue: Optional[str] = None,
            wait: bool = True,  # TODO: implement
            **kwargs
    ) -> int:
        
        request = build_get_request(
            queue,
            topic or self.default_topic_name,
            subscription or self.default_subscription_name
        )
        response = self._send_request(request, **kwargs)
        details = self._load_response(response)
        if queue:
            # TODO: This is probably wrong for a queue
            return int(details[5][0][12][0].text)
        return int(details[5][0][12][0].text)

    def _get(
            self,
            block: bool = True,
            timeout: Optional[int] = None,
            *,
            queue: Optional[str] = None,
            lock: bool = True,
            renew_interval: int = 15,
            **kwargs
    ) -> Message:
        timeout = timeout if block else None
        queue = self._get_queue_name(queue)
        request = build_receive_request(
            "POST" if lock else "DELETE",
            queue,
            timeout=timeout
        )
        response = self._send_request(request, **kwargs)
        if response.status_code == 204:
            raise Empty()

        content = response.read()
        properties = json.loads(response.headers['BrokerProperties'])
        if lock:
            message = LockedMessage(
                id=properties['MessageId'],
                delivery_count=properties['DeliveryCount'],
                lock_token=properties['LockToken'],
                enqueued=deserialize_rfc(properties['EnqueuedTimeUtc']),
                locked_until_utc=deserialize_rfc(properties['LockedUntilUtc']),
                time_to_live=properties["TimeToLive"],
                content=content,
                _renew_interval=renew_interval
            )
            message._renew_lock = Thread(
                target=partial(self._renew_lock, message, queue),
                daemon=True
            )
            message._renew_lock.start()
            return message
        return Message(
            id=properties['MessageId'],
            delivery_count=properties['DeliveryCount'],
            enqueued=deserialize_rfc(properties['EnqueuedTimeUtc']),
            time_to_live=properties["TimeToLive"],
            content=content
        )
    @overload
    def get(
            self,
            timeout: Optional[int] = None,
            *,
            queue: Optional[str] = None,
            lock: Literal[True] = True,
            renew_interval: int = 15,
            wait: Literal[True] = True,
            **kwargs
    ) -> LockedMessage:
        ...
    @overload
    def get(
            self,
            timeout: Optional[int] = None,
            *,
            queue: Optional[str] = None,
            lock: Literal[False],
            wait: Literal[True] = True,
            **kwargs
    ) -> Message:
        ...
    @overload
    def get(
            self,
            timeout: Optional[int] = None,
            *,
            queue: Optional[str] = None,
            lock: Literal[True] = True,
            renew_interval: int = 15,
            wait: Literal[False],
            **kwargs
    ) -> Future[LockedMessage]:
        ...
    @overload
    def get(
            self,
            timeout: Optional[int] = None,
            *,
            queue: Optional[str] = None,
            lock: Literal[False],
            wait: Literal[False],
            **kwargs
    ) -> Future[Message]:
        ...
    @distributed_trace
    def get(
            self,
            timeout: Optional[int] = None,
            *,
            queue: Optional[str] = None,
            lock: bool = True,
            renew_interval: int = 15,
            wait: bool = True,
            **kwargs
    ) -> Message:
        if wait:
            return self._get(
                timeout=timeout,
                queue=queue,
                lock=lock,
                renew_interval=renew_interval,
                **kwargs
            )
        return self._executor.submit(
            self._get,
            timeout=timeout,
            queue=queue,
            lock=lock,
            renew_interval=renew_interval,
            **kwargs
        )

    def _put(
            self,
            message: bytes,
            /, *,
            queue: Optional[str] = None,
            **kwargs
    ) -> Message:
        raise NotImplementedError()
    @overload
    def put(
            self,
            message: bytes,
            /, *,
            queue: Optional[str] = None,
            wait: Literal[True] = True,
            **kwargs
    ) -> Message:
        ...
    @overload
    def put(
            self,
            message: bytes,
            /, *,
            queue: Optional[str] = None,
            wait: Literal[False],
            **kwargs
    ) -> Future[None]:
        ...
    @distributed_trace
    def put(
            self,
            message: bytes,
            /, *,
            queue: Optional[str] = None,
            wait: bool = True,
            **kwargs
    ) -> Message:
        if wait:
            return self._put(
                message,
                queue=queue,
                **kwargs
            )
        return self._executor.submit(
            self._put,
            message,
            queue=queue,
            **kwargs
        )

    def _task_done(
            self,
            message: LockedMessage,
            /, *,
            queue: Optional[str] = None,
            delete: bool = True,
            **kwargs
    ) -> None:
        queue = self._get_queue_name(queue)
        request = build_message_process_request(
            "DELETE" if delete else "PUT",
            queue,
            message.id,
            message.lock_token
        )
        self._send_request(request, **kwargs)
        message._stop_renew.set()

    @overload
    def task_done(
            self,
            message: LockedMessage,
            /, *,
            queue: Optional[str] = None,
            delete: bool = True,
            wait: Literal[True] = True,
            **kwargs
    ) -> None:
        ...
    @overload
    def task_done(
            self,
            message: LockedMessage,
            /, *,
            queue: Optional[str] = None,
            delete: bool = True,
            wait: Literal[False],
            **kwargs
    ) -> Future[None]:
        ...
    @distributed_trace
    def task_done(
            self,
            message: LockedMessage,
            /, *,
            queue: Optional[str] = None,
            delete: bool = True,
            wait: bool = True,
            **kwargs
    ) -> None:
        if wait:
            return self._task_done(
                message,
                queue=queue,
                delete=delete,
                **kwargs
            )
        return self._executor.submit(
            self._task_done,
            message,
            queue=queue,
            delete=delete,
            **kwargs
        )
        

########## Request Builders ##########

def build_receive_request(
    method: Literal["POST", "DELETE"],
    queue: Optional[str],
    *,
    timeout: Optional[int] = None,
    **kwargs: Any
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    # Construct URL
    if queue:
        _url = "{queue}/messages/head"
        path_format_arguments = {
            "queue": quote(queue),
        }
    else:
        _url = "{topic}/subscriptions/{subscription}/messages/head"
        path_format_arguments = {
            "topic": quote(topic),
            "subscription": quote(subscription),
        }
    _url: str = _url.format(**path_format_arguments)  # type: ignore
    # Construct parameters
    if timeout is not None:
        _params["timeout"] = timeout
    return HttpRequest(method=method, url=_url, params=_params, headers=_headers, **kwargs)


def build_message_process_request(
    method: Literal["PUT", "POST", "DELETE"],
    queue: Optional[str],
    topic: Optional[str],
    subscription: Optional[str],
    message_id: str,
    lock_token: str,
    **kwargs: Any
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    # Construct URL
    if queue:
        _url = "{queue}/messages/{message_id}/{lock_token}"
        path_format_arguments = {
            "queue": quote(queue),
            "message_id": quote(message_id),
            "lock_token": quote(lock_token)
        }
    else:
        _url = "{topic}/subscriptions/{subscription}/messages/{message_id}/{lock_token}"
        path_format_arguments = {
            "topic": quote(topic),
            "subscription": quote(subscription),
            "message_id": quote(message_id),
            "lock_token": quote(lock_token)
        }
    _url: str = _url.format(**path_format_arguments)  # type: ignore
    return HttpRequest(method=method, url=_url, params=_params, headers=_headers, **kwargs)


def build_get_request(
    queue: Optional[str],
    topic: Optional[str],
    subscription: Optional[str],
    *,
    enrich: bool = False,
    **kwargs: Any
) -> HttpRequest:
    _headers = case_insensitive_dict(kwargs.pop("headers", {}) or {})
    _params = case_insensitive_dict(kwargs.pop("params", {}) or {})

    api_version: str = kwargs.pop("api_version", _params.pop("api-version", "2021-05"))
    accept = _headers.pop("Accept", "application/xml, application/atom+xml")

    # Construct URL
    if queue:
        _url = "/{queue}"
        path_format_arguments = {
            "queue": quote(queue),
        }
    else:
        _url = "/{topic}/subscriptions/{subscription}"
        path_format_arguments = {
            "topic": quote(topic),
            "subscription": quote(subscription),
        }
    _url: str = _url.format(**path_format_arguments)  # type: ignore

    # Construct parameters
    if enrich is not None:
        _params["enrich"] = quote(json.dumps(enrich))
    _params["api-version"] = quote(api_version)

    # Construct headers
    _headers["Accept"] = accept

    return HttpRequest(method="GET", url=_url, params=_params, headers=_headers, **kwargs)