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

resource resourcegroup_foo 'Microsoft.Resources/resourceGroups@2021-04-01' existing = {
  name: 'foo'
}





