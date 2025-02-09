
from ._bicep.expressions import Parameter, UniqueString, Subscription


LOCATION: Parameter[str] = Parameter(
    'location',
    type=str,
    description="Primary location for all resources",
    min_length=1,
    varname="AZURE_LOCATION"
)
ENV_NAME: Parameter[str] = Parameter(
    'environmentName',
    type=str,
    description="AZD environment name",
    min_length=1,
    max_length=64,
    varname="AZURE_ENV_NAME"
)
DEFAULT_NAME: Parameter[str] = Parameter(
    'defaultName',
    type=str,
    default=UniqueString(Subscription().subscription_id,  ENV_NAME, LOCATION)
)
LOCAL_PRINCIPAL: Parameter[str] = Parameter(
    'principalId',
    type=str,
    description="ID of the user or app to assign application roles",
    varname="AZURE_PRINCIPAL_ID"
)
LOCAL_ACCESS: Parameter[str] = Parameter(
    'localAccess',
    type=str,
    default=True,
    allowed=['User', 'Application', 'None'],
    description='Whether to add application roles to the local user or app.'
)

GLOBAL_PARAMS = {
    'location': LOCATION,
    'environmentName': ENV_NAME,
    'defaultName': DEFAULT_NAME,
    'principalId': LOCAL_PRINCIPAL,
    'localAccess': LOCAL_ACCESS
}
