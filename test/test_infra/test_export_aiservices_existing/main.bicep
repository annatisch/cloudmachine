targetScope = 'subscription'

@sys.description('Primary location for all resources')
@sys.minLength(1)
param location string

@sys.description('AZD environment name')
@sys.maxLength(64)
@sys.minLength(1)
param environmentName string

param defaultName string = uniqueString(subscription().subscriptionId, environmentName, location)

@sys.description('ID of the user or app to assign application roles')
param principalId string

@sys.description('Tags to apply to all resources in AZD envrionment.')
var azdTags = {
  'azd-env-name': environmentName
}

@sys.description('ID of the managed identity to assign application roles')
param managedIdentityId string = ''

@sys.description('Principal ID of the managed identity to assign application roles')
param managedIdentityPrincipalId string = ''

resource resourcegroup_aitest 'Microsoft.Resources/resourceGroups@2021-04-01' existing = {
  name: 'aitest'
}

module test_module 'test.bicep' = {
  name: '${deployment().name}_test'
  scope: resourcegroup_aitest
  params: {
    location: location
    environmentName: environmentName
    defaultName: defaultName
    principalId: principalId
    azdTags: azdTags
    managedIdentityId: managedIdentityId
    managedIdentityPrincipalId: managedIdentityPrincipalId
  }
}
output AZURE_AI_ID_AITEST string = test_module.outputs.AZURE_AI_ID_AITEST
output AZURE_AI_NAME_AITEST string = test_module.outputs.AZURE_AI_NAME_AITEST
output AZURE_AI_RESOURCE_GROUP_AITEST string = test_module.outputs.AZURE_AI_RESOURCE_GROUP_AITEST
output AZURE_AI_ENDPOINT_AITEST string = test_module.outputs.AZURE_AI_ENDPOINT_AITEST


