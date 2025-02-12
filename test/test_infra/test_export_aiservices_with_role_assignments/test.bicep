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


resource roleassignment_ejfkmzehinsmskpspemgmsnifztgifsmgensmskpsqmkjpkpizemgecxjjktkssgnsmskpspgepsjhigcxjtmkxftxmeme 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('AIServices', defaultName, 'ServicePrincipal', 'Cognitive Services OpenAI Contributor')
  properties: {
    principalId: userassignedidentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: 'Cognitive Services OpenAI Contributor'
  }
  scope: account
}



resource roleassignment_ejfkmzehinsmskpspemgmsnifztgifsmgebpsmemgecxjjktkssgnsmskpspgepsjhigbpsmeme 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('AIServices', defaultName, 'User', 'Cognitive Services OpenAI User')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: 'Cognitive Services OpenAI User'
  }
  scope: account
}



