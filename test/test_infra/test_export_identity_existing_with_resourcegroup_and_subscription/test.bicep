param location string
param environmentName string
param defaultName string
param principalId string
param azdTags object

resource userassignedidentity_exists 'Microsoft.ManagedIdentity/userAssignedIdentities@2024-11-30' existing = {
  name: 'exists'
}

output AZURE_CLIENT_ID string = userassignedidentity_exists.properties.clientId


