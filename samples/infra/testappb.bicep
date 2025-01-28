targetScope = 'subscription'

param location string
param environmentName string
param principalId string
var tags = {
  'azd-env-name': environmentName
}


@sys.description('Unique identifier for creating default resource names')
var cloudmachineId = uniqueString(subscription().subscriptionId, 'testappb', location)

var resourcegroup_default_name = cloudmachineId

module resources_2bhum 'br/public:avm/res/resources/resource-group:0.4.0' = {
  name: '${deployment().name}_resources_2bhum'
  params: {
    name: resourcegroup_default_name
    location: location
    tags: tags
  }
}

module managedidentity_xzt1e 'br/public:avm/res/managed-identity/user-assigned-identity:0.4.0' = {
  name: '${deployment().name}_managedidentity_xzt1e'
  scope: resourceGroup(resourcegroup_default_name)
  params: {
    name: cloudmachineId
    location: location
    tags: tags
  }
}

module storage_8vh3z 'br/public:avm/res/storage/storage-account:0.14.0' = {
  name: '${deployment().name}_storage_8vh3z'
  scope: resourceGroup(resourcegroup_default_name)
  params: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    enableHierarchicalNamespace: true
    kind: 'StorageV2'
    skuName: 'Standard_LRS'
    name: 'foo'
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
              name: guid('storage_8vh3z', managedidentity_xzt1e.outputs.principalId, 'Storage Blob Data Contributor')
              principalId: managedidentity_xzt1e.outputs.principalId
              principalType: 'ServicePrincipal'
              roleDefinitionIdOrName: 'Storage Blob Data Contributor'
            }
            {
              name: guid('storage_8vh3z', principalId, 'Storage Blob Data Contributor')
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
        name: guid('storage_8vh3z', managedidentity_xzt1e.outputs.principalId, 'Storage Blob Data Contributor')
        principalId: managedidentity_xzt1e.outputs.principalId
        principalType: 'ServicePrincipal'
        roleDefinitionIdOrName: 'Storage Blob Data Contributor'
      }
      {
        name: guid('storage_8vh3z', principalId, 'Storage Blob Data Contributor')
        principalId: principalId
        principalType: 'User'
        roleDefinitionIdOrName: 'Storage Blob Data Contributor'
      }
      {
        name: guid('storage_8vh3z', managedidentity_xzt1e.outputs.principalId, 'Storage Table Data Contributor')
        principalId: managedidentity_xzt1e.outputs.principalId
        principalType: 'ServicePrincipal'
        roleDefinitionIdOrName: 'Storage Table Data Contributor'
      }
      {
        name: guid('storage_8vh3z', principalId, 'Storage Table Data Contributor')
        principalId: principalId
        principalType: 'User'
        roleDefinitionIdOrName: 'Storage Table Data Contributor'
      }
    ]
    managedIdentities: {
      userAssignedResourceIds: [
        managedidentity_xzt1e.outputs.resourceId
      ]
    }
  }
}
output AZURE_BLOBS_ID__BLOBS_THREE string = storage_8vh3z.outputs.resourceId
output AZURE_BLOBS_NAME__BLOBS_THREE string = storage_8vh3z.outputs.name
output AZURE_BLOBS_ENDPOINT__BLOBS_THREE string = storage_8vh3z.outputs.primaryBlobEndpoint
output AZURE_BLOBS_ID_IMAGES_THREE string = storage_8vh3z.outputs.resourceId
output AZURE_BLOBS_NAME_IMAGES_THREE string = storage_8vh3z.outputs.name
output AZURE_BLOBS_ENDPOINT_IMAGES_THREE string = storage_8vh3z.outputs.primaryBlobEndpoint
output AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_THREE string = '${storage_8vh3z.outputs.primaryBlobEndpoint}/images'
output AZURE_BLOBS_CONTAINER_NAME_IMAGES_THREE string = 'images'

module storage_a7w96 'br/public:avm/res/storage/storage-account:0.14.0' = {
  name: '${deployment().name}_storage_a7w96'
  scope: resourceGroup(resourcegroup_default_name)
  params: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    enableHierarchicalNamespace: false
    kind: 'StorageV2'
    skuName: 'Standard_LRS'
    name: 'bar'
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
              name: guid('storage_a7w96', managedidentity_xzt1e.outputs.principalId, 'Storage Blob Data Contributor')
              principalId: managedidentity_xzt1e.outputs.principalId
              principalType: 'ServicePrincipal'
              roleDefinitionIdOrName: 'Storage Blob Data Contributor'
            }
            {
              name: guid('storage_a7w96', principalId, 'Storage Blob Data Contributor')
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
        name: guid('storage_a7w96', managedidentity_xzt1e.outputs.principalId, 'Storage Table Data Contributor')
        principalId: managedidentity_xzt1e.outputs.principalId
        principalType: 'ServicePrincipal'
        roleDefinitionIdOrName: 'Storage Table Data Contributor'
      }
      {
        name: guid('storage_a7w96', principalId, 'Storage Table Data Contributor')
        principalId: principalId
        principalType: 'User'
        roleDefinitionIdOrName: 'Storage Table Data Contributor'
      }
    ]
    managedIdentities: {
      userAssignedResourceIds: [
        managedidentity_xzt1e.outputs.resourceId
      ]
    }
  }
}
output AZURE_BLOBS_ID__BLOBS_FOUR string = storage_a7w96.outputs.resourceId
output AZURE_BLOBS_NAME__BLOBS_FOUR string = storage_a7w96.outputs.name
output AZURE_BLOBS_ENDPOINT__BLOBS_FOUR string = storage_a7w96.outputs.primaryBlobEndpoint
output AZURE_BLOBS_ID_IMAGES_FOUR string = storage_a7w96.outputs.resourceId
output AZURE_BLOBS_NAME_IMAGES_FOUR string = storage_a7w96.outputs.name
output AZURE_BLOBS_ENDPOINT_IMAGES_FOUR string = storage_a7w96.outputs.primaryBlobEndpoint
output AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_FOUR string = '${storage_a7w96.outputs.primaryBlobEndpoint}/images'
output AZURE_BLOBS_CONTAINER_NAME_IMAGES_FOUR string = 'images'

