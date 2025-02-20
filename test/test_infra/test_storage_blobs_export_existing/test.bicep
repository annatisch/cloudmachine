param location string
param environmentName string
param defaultName string
param principalId string
param azdTags object
param managedIdentityId string
param managedIdentityPrincipalId string

resource storageaccount_storagetest 'Microsoft.Storage/storageAccounts@2023-05-01' existing = {
  name: 'storagetest'
}

output AZURE_STORAGE_ID_STORAGETEST string = storageaccount_storagetest.id
output AZURE_STORAGE_NAME_STORAGETEST string = storageaccount_storagetest.name
output AZURE_STORAGE_RESOURCE_GROUP_STORAGETEST string = 'testrg'


resource blobservice_storagetest 'Microsoft.Storage/storageAccounts/blobServices@2024-01-01' existing = {
  name: 'default'
  parent: storageaccount_storagetest
}

output AZURE_BLOBS_ID_STORAGETEST string = blobservice_storagetest.id
output AZURE_BLOBS_NAME_STORAGETEST string = blobservice_storagetest.name
output AZURE_BLOBS_RESOURCE_GROUP_STORAGETEST string = 'testrg'
output AZURE_BLOBS_ENDPOINT_STORAGETEST string = storageaccount_storagetest.properties.primaryEndpoints.blob


