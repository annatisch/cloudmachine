
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# pylint: disable=line-too-long

from typing import Any, ClassVar, Literal, TypedDict, List
from typing_extensions import Required
from dataclasses import field, dataclass

from ._resource import (
    Resource,
    generate_symbol,
    BicepStr,
    BicepBool,
    BicepInt,
)


class RetentionPolicy(TypedDict):
    days: BicepInt
    enabled: BicepBool


class LogSettings(TypedDict, total=False):
    category: BicepStr
    categoryGroup: BicepStr
    enabled: Required[BicepBool]
    retentionPolicy: RetentionPolicy


class MetricSettings(TypedDict, total=False):
    category: BicepStr
    enabled: Required[BicepBool]
    retentionPolicy: RetentionPolicy
    timeGrain: BicepStr


class DiagnosticProperties(TypedDict, total=False):
    eventHubAuthorizationRuleId: BicepStr
    eventHubName: BicepStr
    logAnalyticsDestinationType: BicepStr
    logs: List[LogSettings]
    marketplacePartnerId: BicepStr
    metrics: List[MetricSettings]
    serviceBusRuleId: BicepStr
    storageAccountId: BicepStr
    workspaceId: BicepStr


@dataclass(kw_only=True)
class DiagnosticSettings(Resource):
    _resource: ClassVar[Literal['Microsoft.Insights/diagnosticSettings']] = 'Microsoft.Insights/diagnosticSettings'
    _version: ClassVar[str] = '2021-05-01-preview'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("diagnostics"), init=False, repr=False)
    name: BicepStr = field(init=False, default="", metadata={'rest': 'name'})
    properties: DiagnosticProperties = field(metadata={'rest': 'properties'})
