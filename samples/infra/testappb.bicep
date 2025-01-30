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

module resources_z7ljt 'br/public:avm/res/resources/resource-group:0.4.0' = {
  name: '${deployment().name}_resources_z7ljt'
  params: {
    name: resourcegroup_default_name
    location: location
    tags: tags
  }
}

module managedidentity_geloo 'br/public:avm/res/managed-identity/user-assigned-identity:0.4.0' = {
  name: '${deployment().name}_managedidentity_geloo'
  scope: resourceGroup(resourcegroup_default_name)
  params: {
    name: cloudmachineId
    location: location
    tags: tags
  }
}
output AZURE_CLIENT_ID string = managedidentity_geloo.outputs.clientId

module storage_5zkec 'br/public:avm/res/storage/storage-account:0.14.0' = {
  name: '${deployment().name}_storage_5zkec'
  scope: resourceGroup(resourcegroup_default_name)
  params: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
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
              name: guid('storage_5zkec', managedidentity_geloo.outputs.principalId, 'Storage Blob Data Contributor')
              principalId: managedidentity_geloo.outputs.principalId
              principalType: 'ServicePrincipal'
              roleDefinitionIdOrName: 'Storage Blob Data Contributor'
            }
            {
              name: guid('storage_5zkec', principalId, 'Storage Blob Data Contributor')
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
        name: guid('storage_5zkec', managedidentity_geloo.outputs.principalId, 'Storage Blob Data Contributor')
        principalId: managedidentity_geloo.outputs.principalId
        principalType: 'ServicePrincipal'
        roleDefinitionIdOrName: 'Storage Blob Data Contributor'
      }
      {
        name: guid('storage_5zkec', principalId, 'Storage Blob Data Contributor')
        principalId: principalId
        principalType: 'User'
        roleDefinitionIdOrName: 'Storage Blob Data Contributor'
      }
      {
        name: guid('storage_5zkec', managedidentity_geloo.outputs.principalId, 'Storage Table Data Contributor')
        principalId: managedidentity_geloo.outputs.principalId
        principalType: 'ServicePrincipal'
        roleDefinitionIdOrName: 'Storage Table Data Contributor'
      }
      {
        name: guid('storage_5zkec', principalId, 'Storage Table Data Contributor')
        principalId: principalId
        principalType: 'User'
        roleDefinitionIdOrName: 'Storage Table Data Contributor'
      }
    ]
    managedIdentities: {
      userAssignedResourceIds: [
        managedidentity_geloo.outputs.resourceId
      ]
    }
  }
}
output AZURE_BLOBS_ID__BLOBS_THREE string = storage_5zkec.outputs.resourceId
output AZURE_BLOBS_NAME__BLOBS_THREE string = storage_5zkec.outputs.name
output AZURE_BLOBS_ENDPOINT__BLOBS_THREE string = storage_5zkec.outputs.primaryBlobEndpoint
output AZURE_BLOBS_ID_IMAGES_THREE string = storage_5zkec.outputs.resourceId
output AZURE_BLOBS_NAME_IMAGES_THREE string = storage_5zkec.outputs.name
output AZURE_BLOBS_ENDPOINT_IMAGES_THREE string = storage_5zkec.outputs.primaryBlobEndpoint
output AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_THREE string = '${storage_5zkec.outputs.primaryBlobEndpoint}/images'
output AZURE_BLOBS_CONTAINER_NAME_IMAGES_THREE string = 'images'

module storage_xshr5 'br/public:avm/res/storage/storage-account:0.14.0' = {
  name: '${deployment().name}_storage_xshr5'
  scope: resourceGroup(resourcegroup_default_name)
  params: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    kind: 'StorageV2'
    skuName: 'Standard_LRS'
    name: 'bar'
    enableHierarchicalNamespace: false
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
              name: guid('storage_xshr5', managedidentity_geloo.outputs.principalId, 'Storage Blob Data Contributor')
              principalId: managedidentity_geloo.outputs.principalId
              principalType: 'ServicePrincipal'
              roleDefinitionIdOrName: 'Storage Blob Data Contributor'
            }
            {
              name: guid('storage_xshr5', principalId, 'Storage Blob Data Contributor')
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
        name: guid('storage_xshr5', managedidentity_geloo.outputs.principalId, 'Storage Table Data Contributor')
        principalId: managedidentity_geloo.outputs.principalId
        principalType: 'ServicePrincipal'
        roleDefinitionIdOrName: 'Storage Table Data Contributor'
      }
      {
        name: guid('storage_xshr5', principalId, 'Storage Table Data Contributor')
        principalId: principalId
        principalType: 'User'
        roleDefinitionIdOrName: 'Storage Table Data Contributor'
      }
    ]
    managedIdentities: {
      userAssignedResourceIds: [
        managedidentity_geloo.outputs.resourceId
      ]
    }
  }
}
output AZURE_BLOBS_ID__BLOBS_FOUR string = storage_xshr5.outputs.resourceId
output AZURE_BLOBS_NAME__BLOBS_FOUR string = storage_xshr5.outputs.name
output AZURE_BLOBS_ENDPOINT__BLOBS_FOUR string = storage_xshr5.outputs.primaryBlobEndpoint
output AZURE_BLOBS_ID_IMAGES_FOUR string = storage_xshr5.outputs.resourceId
output AZURE_BLOBS_NAME_IMAGES_FOUR string = storage_xshr5.outputs.name
output AZURE_BLOBS_ENDPOINT_IMAGES_FOUR string = storage_xshr5.outputs.primaryBlobEndpoint
output AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_FOUR string = '${storage_xshr5.outputs.primaryBlobEndpoint}/images'
output AZURE_BLOBS_CONTAINER_NAME_IMAGES_FOUR string = 'images'

