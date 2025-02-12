param location string
param environmentName string
param defaultName string
param principalId string
param azdTags object

resource account_aitest 'Microsoft.CognitiveServices/accounts@2024-10-01' existing = {
  name: 'aitest'
}

output AZURE_AI_ID_AITEST string = account_aitest.id
output AZURE_AI_NAME_AITEST string = account_aitest.name
output AZURE_AI_RESOURCE_GROUP_AITEST string = 'aitest'
output AZURE_AI_ENDPOINT_AITEST string = account_aitest.properties.endpoint


