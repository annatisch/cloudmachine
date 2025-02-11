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


