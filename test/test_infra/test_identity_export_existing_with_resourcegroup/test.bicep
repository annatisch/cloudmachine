param location string
param environmentName string
param defaultName string
param principalId string
param azdTags object
var managedIdentityId = userassignedidentity_exists.id
var managedIdentityPrincipalId = userassignedidentity_exists.properties.principalId

resource userassignedidentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2024-11-30' = {
  location: location
  tags: azdTags
  name: defaultName
}



resource resourcegroup_rgexists 'Microsoft.Resources/resourceGroups@2021-04-01' existing = {
  name: 'rgexists'
  scope: subscription()
}

resource userassignedidentity_exists 'Microsoft.ManagedIdentity/userAssignedIdentities@2024-11-30' existing = {
  name: 'exists'
  scope: resourcegroup_rgexists
}



