param location string
param environmentName string
param defaultName string
param principalId string
param azdTags object
param testLocation string
var managedIdentityId = userassignedidentity.id
var managedIdentityPrincipalId = userassignedidentity.properties.principalId

resource userassignedidentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2024-11-30' = {
  location: testLocation
  tags: azdTags
  name: defaultName
}



