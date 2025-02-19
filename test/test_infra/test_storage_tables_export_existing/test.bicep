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


resource tableservice_storagetest 'Microsoft.Storage/storageAccounts/tableServices@2024-01-01' existing = {
  name: 'default'
  parent: storageaccount_storagetest
}

output AZURE_TABLES_ID_STORAGETEST string = tableservice_storagetest.id
output AZURE_TABLES_NAME_STORAGETEST string = tableservice_storagetest.name
output AZURE_TABLES_RESOURCE_GROUP_STORAGETEST string = 'testrg'
output AZURE_TABLES_ENDPOINT_STORAGETEST string = storageaccount_storagetest.properties.primaryEndpoints.table


