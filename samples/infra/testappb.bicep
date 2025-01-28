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

module resources_ucoxo 'br/public:avm/res/resources/resource-group:0.4.0' = {
  name: '${deployment().name}_resources_ucoxo'
  params: {
    name: resourcegroup_default_name
    location: location
    tags: tags
  }
}

module managedidentity_p88wx 'br/public:avm/res/managed-identity/user-assigned-identity:0.4.0' = {
  name: '${deployment().name}_managedidentity_p88wx'
  scope: resourceGroup(resourcegroup_default_name)
  params: {
    name: cloudmachineId
    location: location
    tags: tags
  }
}
output AZURE_IDENTITY_ID_P88WX string = managedidentity_p88wx.outputs.resourceId
output AZURE_IDENTITY_NAME_P88WX string = managedidentity_p88wx.outputs.name
output AZURE_CLIENT_ID string = managedidentity_p88wx.outputs.clientId

module storage_m1gxe 'br/public:avm/res/storage/storage-account:0.14.0' = {
  name: '${deployment().name}_storage_m1gxe'
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
              name: guid('storage_m1gxe', managedidentity_p88wx.outputs.principalId, 'Storage Blob Data Contributor')
              principalId: managedidentity_p88wx.outputs.principalId
              principalType: 'ServicePrincipal'
              roleDefinitionIdOrName: 'Storage Blob Data Contributor'
            }
            {
              name: guid('storage_m1gxe', principalId, 'Storage Blob Data Contributor')
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
        name: guid('storage_m1gxe', managedidentity_p88wx.outputs.principalId, 'Storage Blob Data Contributor')
        principalId: managedidentity_p88wx.outputs.principalId
        principalType: 'ServicePrincipal'
        roleDefinitionIdOrName: 'Storage Blob Data Contributor'
      }
      {
        name: guid('storage_m1gxe', principalId, 'Storage Blob Data Contributor')
        principalId: principalId
        principalType: 'User'
        roleDefinitionIdOrName: 'Storage Blob Data Contributor'
      }
      {
        name: guid('storage_m1gxe', managedidentity_p88wx.outputs.principalId, 'Storage Table Data Contributor')
        principalId: managedidentity_p88wx.outputs.principalId
        principalType: 'ServicePrincipal'
        roleDefinitionIdOrName: 'Storage Table Data Contributor'
      }
      {
        name: guid('storage_m1gxe', principalId, 'Storage Table Data Contributor')
        principalId: principalId
        principalType: 'User'
        roleDefinitionIdOrName: 'Storage Table Data Contributor'
      }
    ]
    managedIdentities: {
      userAssignedResourceIds: [
        managedidentity_p88wx.outputs.resourceId
      ]
    }
  }
}
output AZURE_BLOBS_ID__BLOBS_THREE string = storage_m1gxe.outputs.resourceId
output AZURE_BLOBS_NAME__BLOBS_THREE string = storage_m1gxe.outputs.name
output AZURE_BLOBS_ENDPOINT__BLOBS_THREE string = storage_m1gxe.outputs.primaryBlobEndpoint
output AZURE_BLOBS_ID_IMAGES_THREE string = storage_m1gxe.outputs.resourceId
output AZURE_BLOBS_NAME_IMAGES_THREE string = storage_m1gxe.outputs.name
output AZURE_BLOBS_ENDPOINT_IMAGES_THREE string = storage_m1gxe.outputs.primaryBlobEndpoint
output AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_THREE string = '${storage_m1gxe.outputs.primaryBlobEndpoint}/images'
output AZURE_BLOBS_CONTAINER_NAME_IMAGES_THREE string = 'images'

module storage_7ziwy 'br/public:avm/res/storage/storage-account:0.14.0' = {
  name: '${deployment().name}_storage_7ziwy'
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
              name: guid('storage_7ziwy', managedidentity_p88wx.outputs.principalId, 'Storage Blob Data Contributor')
              principalId: managedidentity_p88wx.outputs.principalId
              principalType: 'ServicePrincipal'
              roleDefinitionIdOrName: 'Storage Blob Data Contributor'
            }
            {
              name: guid('storage_7ziwy', principalId, 'Storage Blob Data Contributor')
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
        name: guid('storage_7ziwy', managedidentity_p88wx.outputs.principalId, 'Storage Table Data Contributor')
        principalId: managedidentity_p88wx.outputs.principalId
        principalType: 'ServicePrincipal'
        roleDefinitionIdOrName: 'Storage Table Data Contributor'
      }
      {
        name: guid('storage_7ziwy', principalId, 'Storage Table Data Contributor')
        principalId: principalId
        principalType: 'User'
        roleDefinitionIdOrName: 'Storage Table Data Contributor'
      }
    ]
    managedIdentities: {
      userAssignedResourceIds: [
        managedidentity_p88wx.outputs.resourceId
      ]
    }
  }
}
output AZURE_BLOBS_ID__BLOBS_FOUR string = storage_7ziwy.outputs.resourceId
output AZURE_BLOBS_NAME__BLOBS_FOUR string = storage_7ziwy.outputs.name
output AZURE_BLOBS_ENDPOINT__BLOBS_FOUR string = storage_7ziwy.outputs.primaryBlobEndpoint
output AZURE_BLOBS_ID_IMAGES_FOUR string = storage_7ziwy.outputs.resourceId
output AZURE_BLOBS_NAME_IMAGES_FOUR string = storage_7ziwy.outputs.name
output AZURE_BLOBS_ENDPOINT_IMAGES_FOUR string = storage_7ziwy.outputs.primaryBlobEndpoint
output AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_FOUR string = '${storage_7ziwy.outputs.primaryBlobEndpoint}/images'
output AZURE_BLOBS_CONTAINER_NAME_IMAGES_FOUR string = 'images'

