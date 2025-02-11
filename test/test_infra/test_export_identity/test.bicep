param location string
param environmentName string
param defaultName string
param principalId string
param azdTags object

resource userassignedidentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2024-11-30' = {
  name: defaultName
  location: location
  tags: azdTags
}

output AZURE_CLIENT_ID string = userassignedidentity.properties.clientId


