targetScope = 'subscription'

param location string
param environmentName string
param principalId string
var tags = {
  'azd-env-name': environmentName
}


@sys.description('Unique identifier for creating default resource names')
var cloudmachineId = uniqueString(subscription().subscriptionId, 'testappa', location)

var resourcegroup_default_name = cloudmachineId

module resources_rp6jz 'br/public:avm/res/resources/resource-group:0.4.0' = {
  name: '${deployment().name}_resources_rp6jz'
  params: {
    name: resourcegroup_default_name
    location: location
    tags: tags
  }
}

module managedidentity_15wtj 'br/public:avm/res/managed-identity/user-assigned-identity:0.4.0' = {
  name: '${deployment().name}_managedidentity_15wtj'
  scope: resourceGroup(resourcegroup_default_name)
  params: {
    name: cloudmachineId
    location: location
    tags: tags
  }
}
output AZURE_CLIENT_ID string = managedidentity_15wtj.outputs.clientId

module storage_gnt09 'br/public:avm/res/storage/storage-account:0.14.0' = {
  name: '${deployment().name}_storage_gnt09'
  scope: resourceGroup(resourcegroup_default_name)
  params: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    kind: 'StorageV2'
    skuName: 'Standard_LRS'
    name: cloudmachineId
    location: location
    tags: tags
    blobServices: {
      containers: [
        {
          name: 'images'
          metadata: {
            foo: 'bar'
          }
          roleAssignments: [
            {
              name: guid('storage_gnt09', managedidentity_15wtj.outputs.principalId, 'Storage Blob Data Contributor')
              principalId: managedidentity_15wtj.outputs.principalId
              principalType: 'ServicePrincipal'
              roleDefinitionIdOrName: 'Storage Blob Data Contributor'
            }
            {
              name: guid('storage_gnt09', principalId, 'Storage Blob Data Contributor')
              principalId: principalId
              principalType: 'User'
              roleDefinitionIdOrName: 'Storage Blob Data Contributor'
            }
          ]
        }
      ]
    }
    tableServices: {
      tables: [
        {
          name: 'users'
        }
      ]
    }
    roleAssignments: [
      {
        name: guid('storage_gnt09', managedidentity_15wtj.outputs.principalId, 'Storage Table Data Contributor')
        principalId: managedidentity_15wtj.outputs.principalId
        principalType: 'ServicePrincipal'
        roleDefinitionIdOrName: 'Storage Table Data Contributor'
      }
      {
        name: guid('storage_gnt09', principalId, 'Storage Table Data Contributor')
        principalId: principalId
        principalType: 'User'
        roleDefinitionIdOrName: 'Storage Table Data Contributor'
      }
    ]
    managedIdentities: {
      userAssignedResourceIds: [
        managedidentity_15wtj.outputs.resourceId
      ]
    }
  }
}
output AZURE_BLOBS_ID_IMAGES_ONE string = storage_gnt09.outputs.resourceId
output AZURE_BLOBS_NAME_IMAGES_ONE string = storage_gnt09.outputs.name
output AZURE_BLOBS_ENDPOINT_IMAGES_ONE string = storage_gnt09.outputs.primaryBlobEndpoint
output AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_ONE string = '${storage_gnt09.outputs.primaryBlobEndpoint}/images'
output AZURE_BLOBS_CONTAINER_NAME_IMAGES_ONE string = 'images'
output AZURE_BLOBS_ID_IMAGES_TWO string = storage_gnt09.outputs.resourceId
output AZURE_BLOBS_NAME_IMAGES_TWO string = storage_gnt09.outputs.name
output AZURE_BLOBS_ENDPOINT_IMAGES_TWO string = storage_gnt09.outputs.primaryBlobEndpoint
output AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_TWO string = '${storage_gnt09.outputs.primaryBlobEndpoint}/images'
output AZURE_BLOBS_CONTAINER_NAME_IMAGES_TWO string = 'images'
output AZURE_TABLES_ID_USERS string = storage_gnt09.outputs.resourceId
output AZURE_TABLES_NAME_USERS string = storage_gnt09.outputs.name
output AZURE_TABLES_ENDPOINT_USERS string = storage_gnt09.outputs.serviceEndpoints.table

