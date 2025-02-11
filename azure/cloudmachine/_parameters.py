
from typing import Dict
from ._bicep.expressions import Parameter, UniqueString, Subscription, Variable


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
AZD_TAGS: Parameter[Dict[str, str]] = Variable(
    'azdTags',
    value={'azd-env-name': ENV_NAME},
    description='Tags to apply to all resources in AZD envrionment.'
)

GLOBAL_PARAMS = {
    'location': LOCATION,
    'environmentName': ENV_NAME,
    'defaultName': DEFAULT_NAME,
    'principalId': LOCAL_PRINCIPAL,
    'azdTags': AZD_TAGS,
}
