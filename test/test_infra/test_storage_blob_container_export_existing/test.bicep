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


resource blobservice_storagetest 'Microsoft.Storage/storageAccounts/blobServices@2022-09-01' existing = {
  name: 'default'
  parent: storageaccount_storagetest
}

output AZURE_BLOBS_ID_STORAGETEST string = blobservice_storagetest.id
output AZURE_BLOBS_NAME_STORAGETEST string = blobservice_storagetest.name
output AZURE_BLOBS_RESOURCE_GROUP_STORAGETEST string = 'testrg'
output AZURE_BLOBS_ENDPOINT_STORAGETEST string = storageaccount_storagetest.properties.primaryEndpoints.blob


resource container_storagetest_test 'Microsoft.Storage/storageAccounts/blobServices/containers@2022-09-01' existing = {
  name: 'test'
  parent: blobservice_storagetest
}

output AZURE_BLOB_CONTAINER_ID_STORAGETEST_TEST string = container_storagetest_test.id
output AZURE_BLOB_CONTAINER_NAME_STORAGETEST_TEST string = container_storagetest_test.name
output AZURE_BLOB_CONTAINER_RESOURCE_GROUP_STORAGETEST_TEST string = 'testrg'
output AZURE_BLOB_CONTAINER_ENDPOINT_STORAGETEST_TEST string = '${storageaccount_storagetest.properties.primaryEndpoints.blob}${container_storagetest_test.name}'


