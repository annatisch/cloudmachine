param location string
param environmentName string
param defaultName string
param principalId string
param azdTags object
var managedIdentityId = userassignedidentity_foo.id
var managedIdentityPrincipalId = userassignedidentity_foo.properties.principalId

resource userassignedidentity_foo 'Microsoft.ManagedIdentity/userAssignedIdentities@2024-11-30' = {
  name: 'foo'
  location: 'westus'
  tags: {
    key: 'value'
  }
}



