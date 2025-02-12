param location string
param environmentName string
param defaultName string
param principalId string
param azdTags object
param aiChatModel string
param aiChatModelFormat string
param aiChatModelVersion string
param aiChatModelSku string
param aiChatModelCapacity int
var managedIdentityId = userassignedidentity.id
var managedIdentityPrincipalId = userassignedidentity.properties.principalId

resource userassignedidentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2024-11-30' = {
  location: location
  tags: azdTags
  name: defaultName
}

output AZURE_CLIENT_ID string = userassignedidentity.properties.clientId


resource account 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  properties: {
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: true
  }
  kind: 'AIServices'
  name: '${defaultName}-aiservices'
  location: location
  tags: azdTags
  sku: {
    name: 'S0'
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityId}': {}
    }
  }
}

output AZURE_AI_ID string = account.id
output AZURE_AI_NAME string = account.name
output AZURE_AI_RESOURCE_GROUP string = resourceGroup().name
output AZURE_AI_ENDPOINT string = account.properties.endpoint


resource deployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: account
  properties: {
    model: {
      name: aiChatModel
      format: aiChatModelFormat
      version: aiChatModelVersion
    }
  }
  name: aiChatModel
  sku: {
    name: aiChatModelSku
    capacity: aiChatModelCapacity
  }
}

output AZURE_AI_CHAT_ID string = deployment.id
output AZURE_AI_CHAT_NAME string = deployment.name
output AZURE_AI_CHAT_RESOURCE_GROUP string = resourceGroup().name
output AZURE_AI_CHAT_MODEL_NAME string = deployment.properties.model.name
output AZURE_AI_CHAT_MODEL_VERSION string = deployment.properties.model.version
output AZURE_AI_CHAT_ENDPOINT string = '${account.properties.endpoint}openai/deployments/${deployment.name}/chat/completions'


resource roleassignment_prmcdnytekaxfpxlctiu 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', '${defaultName}-aiservices', 'ServicePrincipal', 'Cognitive Services OpenAI Contributor')
  properties: {
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'a001fd3d-188f-4b5d-821b-7da978bf7442'
    )

  }
  scope: account
}



resource roleassignment_iixyucpvhqitrkqrnbqa 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', '${defaultName}-aiservices', 'ServicePrincipal', 'Cognitive Services OpenAI User')
  properties: {
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
    )

  }
  scope: account
}



resource roleassignment_guvkdgrgirgwzahwnvou 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', '${defaultName}-aiservices', 'User', 'Cognitive Services OpenAI Contributor')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'a001fd3d-188f-4b5d-821b-7da978bf7442'
    )

  }
  scope: account
}



resource roleassignment_ddsjnquihdmohlbeapox 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', '${defaultName}-aiservices', 'User', 'Cognitive Services OpenAI User')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
    )

  }
  scope: account
}



