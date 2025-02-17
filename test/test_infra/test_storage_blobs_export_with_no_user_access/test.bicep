param location string
param environmentName string
param defaultName string
param azdTags object
var managedIdentityId = userassignedidentity.id
var managedIdentityPrincipalId = userassignedidentity.properties.principalId

resource userassignedidentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2024-11-30' = {
  location: location
  tags: azdTags
  name: defaultName
}

output AZURE_CLIENT_ID string = userassignedidentity.properties.clientId


resource storageaccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  properties: {
    accessTier: 'Hot'
    allowCrossTenantReplication: false
  }
  name: defaultName
  location: location
  tags: azdTags
  kind: 'StorageV2'
  sku: {
    name: 'Standard_GRS'
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityId}': {}
    }
  }
}

output AZURE_STORAGE_ID string = storageaccount.id
output AZURE_STORAGE_NAME string = storageaccount.name
output AZURE_STORAGE_RESOURCE_GROUP string = resourceGroup().name


resource blobservice 'Microsoft.Storage/storageAccounts/blobServices@2022-09-01' = {
  parent: storageaccount
  properties: {}
  name: 'default'
}

output AZURE_BLOBS_ID string = blobservice.id
output AZURE_BLOBS_NAME string = blobservice.name
output AZURE_BLOBS_RESOURCE_GROUP string = resourceGroup().name
output AZURE_BLOBS_ENDPOINT string = storageaccount.properties.primaryEndpoints.blob


resource roleassignment_eqnucakyjztglyagdwqk 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftStoragestorageAccountsblobServices', 'default', 'ServicePrincipal', 'Storage Blob Data Owner')
  properties: {
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'b7e6dc6d-f1e8-4753-8033-0f276bb0955b'
    )

  }
  scope: blobservice
}



