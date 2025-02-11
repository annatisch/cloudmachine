param location string
param environmentName string
param defaultName string
param azdTags object

resource userassignedidentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2024-11-30' = {
  name: defaultName
  location: location
  tags: azdTags
}

output AZURE_CLIENT_ID string = userassignedidentity.properties.clientId


resource storageaccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  properties: {
    accessTier: 'Hot'
    allowCrossTenantReplication: false
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
  kind: 'StorageV2'
  sku: {
    name: 'Standard_GRS'
  }
}

output AZURE_STORAGE_ID string = storageaccount.id
output AZURE_STORAGE_NAME string = storageaccount.name
output AZURE_STORAGE_RESOURCE_GROUP string = resourceGroup().name


resource roleassignment_ejfkmzentxmijshppxfjtemgmsnifztgifsmgensmskpsqmkjpkpizemgentxmijsggzxxgsitigewjsmeme 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('StorageAccount', defaultName, 'ServicePrincipal', 'Storage Blob Data Owner')
  properties: {
    principalId: userassignedidentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'b7e6dc6d-f1e8-4753-8033-0f276bb0955b'
    )

  }
  scope: storageaccount
}



