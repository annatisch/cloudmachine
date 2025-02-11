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

resource resourcegroup_rgexists 'Microsoft.Resources/resourceGroups@2021-04-01' existing = {
  name: 'rgexists'
  scope: subscription('6e441d6a-23ce-4450-a4a6-78f8d4f45ce9')
}

module test_module 'test.bicep' = {
  name: '${deployment().name}_test'
  scope: resourcegroup_rgexists
  params: {
    location: location
    environmentName: environmentName
    defaultName: defaultName
    principalId: principalId
    azdTags: azdTags
  }
}
output AZURE_CLIENT_ID string = test_module.outputs.AZURE_CLIENT_ID


