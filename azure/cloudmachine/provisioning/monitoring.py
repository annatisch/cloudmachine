# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

# pylint: disable=line-too-long, protected-access

from enum import Enum
from typing import IO, ClassVar, Dict, List, Optional, Literal, TypedDict
from typing_extensions import Required
from dataclasses import field, dataclass
from ._roles import RoleAssignment
from ._identity import UserAssignedIdentities
from ._resource import (
    Output,
    PrincipalId,
    ResourceName,
    _serialize_resource,
    Resource,
    LocatedResource,
    generate_symbol,
    _UNSET,
    _SKIP,
    GuidName,
    resolve_value,
    BicepBool,
    BicepInt,
    BicepStr
)

# class StorageRoleAssignments(Enum):
#     BLOB_DATA_CONTRIBUTOR = "ba92f5b4-2d11-453d-a403-e96b0029c9fe"
#     BLOB_DATA_READER = "2a2b9908-6ea1-4ae2-8e65-a410df84e7d1"
#     TABLE_DATA_CONTRIBUTOR = "0a9a7e1f-b9d0-4cc4-a60d-0319b160aaa3"


PrincipalType = Literal['User', 'Group', 'ServicePrincipal', 'Unknown', 'DirectoryRoleTemplate', 'ForeignGroup', 'Application', 'MSI', 'DirectoryObjectOrGroup', 'Everyone']


class Identity(TypedDict, total=False):
    type: Required[Literal['None', 'SystemAssigned', 'SystemAssigned,UserAssigned','UserAssigned']]
    userAssignedIdentities: UserAssignedIdentities


class WorkspaceSku(TypedDict, total=False):
    name: Required[Literal['CapacityReservation', 'Free', 'LACluster', 'PerGB2018', 'PerNode', 'Premium', 'Standalone', 'Standard']]
    capacityReservationLevel: BicepInt


class WorkspaceCapping(TypedDict):
    dailyQuotaGb: BicepInt


class WorkspaceFeatures(TypedDict, total=False):
    clusterResourceId: BicepStr
    disableLocalAuth: BicepBool
    enableDataExport: BicepBool
    enableLogAccessUsingOnlyResourcePermissions: BicepBool
    immediatePurgeDataOn30Days: BicepBool
    searchVersion: BicepInt


class WorkspaceProperties(TypedDict, total=False):
    defaultDataCollectionRuleResourceId: BicepStr
    features: WorkspaceFeatures
    forceCmkForQuery: BicepBool
    publicNetworkAccessForIngestion: Literal['Disabled', 'Enabled']
    publicNetworkAccessForQuery: Literal['Disabled', 'Enabled']
    retentionInDays: BicepInt
    sku: WorkspaceSku
    workspaceCapping: WorkspaceCapping


@dataclass(kw_only=True)
class LogAnalyticsWorkspace(LocatedResource):
    etag: Optional[BicepStr] = field(default=_UNSET, metadata={'rest': 'etag'})
    identity: Optional[Identity] = field(default=_UNSET, metadata={'rest': 'identity'})
    properties: Optional[WorkspaceProperties] = field(default=_UNSET, metadata={'rest': 'properties'})
    _resource: ClassVar[Literal['Microsoft.OperationalInsights/workspaces']] = 'Microsoft.OperationalInsights/workspaces'
    _version: ClassVar[str] = '2023-09-01'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("workspace"), init=False, repr=False)


class ApplicationInsightProperties(TypedDict, total=False):
    Application_Type: Required[Literal['other', 'web']]
    DisableIpMasking: BicepBool
    DisableLocalAuth: BicepBool
    Flow_Type: Literal['Bluefield']
    ForceCustomerStorageForProfiler: BicepBool
    HockeyAppId: BicepStr
    ImmediatePurgeDataOn30Days: BicepBool
    IngestionMode: Literal['ApplicationInsights', 'ApplicationInsightsWithDiagnosticSettings', 'LogAnalytics']
    publicNetworkAccessForIngestion: Literal['Disabled', 'Enabled']
    publicNetworkAccessForQuery: Literal['Disabled', 'Enabled']
    Request_Source: Literal['rest']
    RetentionInDays: BicepInt
    SamplingPercentage: BicepInt
    WorkspaceResourceId: BicepStr


@dataclass(kw_only=True)
class ApplicationInsights(LocatedResource):
    etag: Optional[BicepStr] = field(default=_UNSET, metadata={'rest': 'etag'})
    kind: Optional[BicepStr] = field(default=_UNSET, metadata={'rest': 'kind'})
    properties: Optional[WorkspaceProperties] = field(default=_UNSET, metadata={'rest': 'properties'})
    _resource: ClassVar[Literal['Microsoft.Insights/components']] = 'Microsoft.Insights/components'
    _version: ClassVar[str] = '2020-02-02'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("appinsights"), init=False, repr=False)

    def write(self, bicep: IO[str]) -> Dict[str, str]:
        _serialize_resource(bicep, self)
        output_prefix = "Applicationinsights"
        self._outputs[output_prefix + "ConnectionString"] = Output(
            f"{self._symbolicname}.properties.ConnectionString",
            needs_prefix=False
        )
        for key, value in self._outputs.items():
            bicep.write(f"output {key} string = {resolve_value(value)}\n")
        output_name = Output(f"{self._symbolicname}.name")
        bicep.write("\n")
        bicep.write("module applicationInsightsDashboard 'monitor-dashboard.bicep' = {\n")
        bicep.write(f"  name: {ResourceName(suffix='-dashboard').resolve()}\n")
        bicep.write("  params: {\n")
        bicep.write(f"    name: {ResourceName(suffix='-dashboard').resolve()}\n")
        bicep.write("    location: location\n")
        bicep.write(f"    applicationInsightsName: {output_name.resolve()}\n")
        bicep.write("  }\n")
        bicep.write("}\n")
        bicep.write("\n")
        return self._outputs