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


resource account 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  kind: 'AIServices'
  properties: {
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: true
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      userassignedidentity: {}
    }
  }
  name: defaultName
  location: location
  tags: azdTags
  sku: {
    name: 'S0'
  }
}

output AZURE_AI_ID string = account.id
output AZURE_AI_NAME string = account.name
output AZURE_AI_RESOURCE_GROUP string = resourceGroup().name
output AZURE_AI_ENDPOINT string = account.properties.endpoint


