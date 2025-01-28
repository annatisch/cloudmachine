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

module resources_n8ekd 'br/public:avm/res/resources/resource-group:0.4.0' = {
  name: '${deployment().name}_resources_n8ekd'
  params: {
    name: resourcegroup_default_name
    location: location
    tags: tags
  }
}

module managedidentity_aoqk8 'br/public:avm/res/managed-identity/user-assigned-identity:0.4.0' = {
  name: '${deployment().name}_managedidentity_aoqk8'
  scope: resourceGroup(resourcegroup_default_name)
  params: {
    name: cloudmachineId
    location: location
    tags: tags
  }
}

module storage_sdk8r 'br/public:avm/res/storage/storage-account:0.14.0' = {
  name: '${deployment().name}_storage_sdk8r'
  scope: resourceGroup(resourcegroup_default_name)
  params: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    enableHierarchicalNamespace: true
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
              name: guid('storage_sdk8r', managedidentity_aoqk8.outputs.principalId, 'Storage Blob Data Contributor')
              principalId: managedidentity_aoqk8.outputs.principalId
              principalType: 'ServicePrincipal'
              roleDefinitionIdOrName: 'Storage Blob Data Contributor'
            }
            {
              name: guid('storage_sdk8r', principalId, 'Storage Blob Data Contributor')
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
        name: guid('storage_sdk8r', managedidentity_aoqk8.outputs.principalId, 'Storage Table Data Contributor')
        principalId: managedidentity_aoqk8.outputs.principalId
        principalType: 'ServicePrincipal'
        roleDefinitionIdOrName: 'Storage Table Data Contributor'
      }
      {
        name: guid('storage_sdk8r', principalId, 'Storage Table Data Contributor')
        principalId: principalId
        principalType: 'User'
        roleDefinitionIdOrName: 'Storage Table Data Contributor'
      }
    ]
    managedIdentities: {
      userAssignedResourceIds: [
        managedidentity_aoqk8.outputs.resourceId
      ]
    }
  }
}
output AZURE_BLOBS_ID_IMAGES_ONE string = storage_sdk8r.outputs.resourceId
output AZURE_BLOBS_NAME_IMAGES_ONE string = storage_sdk8r.outputs.name
output AZURE_BLOBS_ENDPOINT_IMAGES_ONE string = storage_sdk8r.outputs.primaryBlobEndpoint
output AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_ONE string = '${storage_sdk8r.outputs.primaryBlobEndpoint}/images'
output AZURE_BLOBS_CONTAINER_NAME_IMAGES_ONE string = 'images'
output AZURE_BLOBS_ID_IMAGES_TWO string = storage_sdk8r.outputs.resourceId
output AZURE_BLOBS_NAME_IMAGES_TWO string = storage_sdk8r.outputs.name
output AZURE_BLOBS_ENDPOINT_IMAGES_TWO string = storage_sdk8r.outputs.primaryBlobEndpoint
output AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_TWO string = '${storage_sdk8r.outputs.primaryBlobEndpoint}/images'
output AZURE_BLOBS_CONTAINER_NAME_IMAGES_TWO string = 'images'
output AZURE_TABLES_ID_USERS string = storage_sdk8r.outputs.resourceId
output AZURE_TABLES_NAME_USERS string = storage_sdk8r.outputs.name
output AZURE_TABLES_ENDPOINT_USERS string = storage_sdk8r.outputs.serviceEndpoints.table

