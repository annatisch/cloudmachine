param location string
param environmentName string
param defaultName string
param principalId string
param azdTags object
param aiEmbeddingsModel string
param aiEmbeddingsModelFormat string
param aiEmbeddingsModelVersion string
param aiEmbeddingsModelSku string
param aiEmbeddingsModelCapacity int
var managedIdentityId = userassignedidentity.id
var managedIdentityPrincipalId = userassignedidentity.properties.principalId

resource userassignedidentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2024-11-30' = {
  location: location
  tags: azdTags
  name: defaultName
}



resource aiservices_account 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  kind: 'AIServices'
  properties: {
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: true
  }
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

output AZURE_AI_AISERVICES_ID string = aiservices_account.id
output AZURE_AI_AISERVICES_NAME string = aiservices_account.name
output AZURE_AI_AISERVICES_RESOURCE_GROUP string = resourceGroup().name
output AZURE_AI_AISERVICES_ENDPOINT string = aiservices_account.properties.endpoint


resource embeddings_deployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: aiservices_account
  properties: {
    model: {
      name: aiEmbeddingsModel
      format: aiEmbeddingsModelFormat
      version: aiEmbeddingsModelVersion
    }
  }
  name: '${defaultName}-embeddings-deployment'
  sku: {
    name: aiEmbeddingsModelSku
    capacity: aiEmbeddingsModelCapacity
  }
}

output AZURE_AI_EMBEDDINGS_ID string = embeddings_deployment.id
output AZURE_AI_EMBEDDINGS_NAME string = embeddings_deployment.name
output AZURE_AI_EMBEDDINGS_RESOURCE_GROUP string = resourceGroup().name
output AZURE_AI_EMBEDDINGS_MODEL_NAME string = embeddings_deployment.properties.model.name
output AZURE_AI_EMBEDDINGS_MODEL_VERSION string = embeddings_deployment.properties.model.version
output AZURE_AI_EMBEDDINGS_ENDPOINT string = '${aiservices_account.properties.endpoint}openai/deployments/${embeddings_deployment.name}/embeddings'


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
  scope: aiservices_account
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
  scope: aiservices_account
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
  scope: aiservices_account
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
  scope: aiservices_account
}



