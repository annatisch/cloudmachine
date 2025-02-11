param location string
param environmentName string
param defaultName string
param principalId string
param azdTags object
param testLocation string

resource userassignedidentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2024-11-30' = {
  location: testLocation
  name: defaultName
  tags: azdTags
}

output AZURE_CLIENT_ID string = userassignedidentity.properties.clientId


