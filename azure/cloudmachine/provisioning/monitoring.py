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
    ResourceId,
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

class MonitoringRoleAssignments(Enum):
    METRICS_PUBLISHER = '3913510d-42f4-4e42-8a64-420c390055eb'


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
    roles: Optional[List[RoleAssignment]] = field(default_factory=list, metadata={'rest': _SKIP})
    _resource: ClassVar[Literal['Microsoft.Insights/components']] = 'Microsoft.Insights/components'
    _version: ClassVar[str] = '2020-02-02'
    _symbolicname: str = field(default_factory=lambda: generate_symbol("appinsights"), init=False, repr=False)

    def write(self, bicep: IO[str]) -> Dict[str, str]:
        _serialize_resource(bicep, self)
        for role in self.roles:
            principal_id: PrincipalId = role.properties['principalId']
            if principal_id.resource:
                principal_id = ResourceId(principal_id.resource)
            role.name = GuidName(self, principal_id, role.properties['roleDefinitionId'])
            role.scope = self
            self._outputs.update(role.write(bicep))
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