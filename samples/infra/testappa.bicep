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

module resources_mrp3d 'br/public:avm/res/resources/resource-group:0.4.0' = {
  name: '${deployment().name}_resources_mrp3d'
  params: {
    name: resourcegroup_default_name
    location: location
    tags: tags
  }
}

module managedidentity_sbf1l 'br/public:avm/res/managed-identity/user-assigned-identity:0.4.0' = {
  name: '${deployment().name}_managedidentity_sbf1l'
  scope: resourceGroup(resourcegroup_default_name)
  params: {
    name: cloudmachineId
    location: location
    tags: tags
  }
}
output AZURE_IDENTITY_ID_SBF1L string = managedidentity_sbf1l.outputs.resourceId
output AZURE_IDENTITY_NAME_SBF1L string = managedidentity_sbf1l.outputs.name
output AZURE_CLIENT_ID string = managedidentity_sbf1l.outputs.clientId

module storage_upmgb 'br/public:avm/res/storage/storage-account:0.14.0' = {
  name: '${deployment().name}_storage_upmgb'
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
              name: guid('storage_upmgb', managedidentity_sbf1l.outputs.principalId, 'Storage Blob Data Contributor')
              principalId: managedidentity_sbf1l.outputs.principalId
              principalType: 'ServicePrincipal'
              roleDefinitionIdOrName: 'Storage Blob Data Contributor'
            }
            {
              name: guid('storage_upmgb', principalId, 'Storage Blob Data Contributor')
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
        name: guid('storage_upmgb', managedidentity_sbf1l.outputs.principalId, 'Storage Blob Data Contributor')
        principalId: managedidentity_sbf1l.outputs.principalId
        principalType: 'ServicePrincipal'
        roleDefinitionIdOrName: 'Storage Blob Data Contributor'
      }
      {
        name: guid('storage_upmgb', principalId, 'Storage Blob Data Contributor')
        principalId: principalId
        principalType: 'User'
        roleDefinitionIdOrName: 'Storage Blob Data Contributor'
      }
      {
        name: guid('storage_upmgb', managedidentity_sbf1l.outputs.principalId, 'Storage Table Data Contributor')
        principalId: managedidentity_sbf1l.outputs.principalId
        principalType: 'ServicePrincipal'
        roleDefinitionIdOrName: 'Storage Table Data Contributor'
      }
      {
        name: guid('storage_upmgb', principalId, 'Storage Table Data Contributor')
        principalId: principalId
        principalType: 'User'
        roleDefinitionIdOrName: 'Storage Table Data Contributor'
      }
    ]
    managedIdentities: {
      userAssignedResourceIds: [
        managedidentity_sbf1l.outputs.resourceId
      ]
    }
  }
}
output AZURE_BLOBS_ID__BLOBS_ONE string = storage_upmgb.outputs.resourceId
output AZURE_BLOBS_NAME__BLOBS_ONE string = storage_upmgb.outputs.name
output AZURE_BLOBS_ENDPOINT__BLOBS_ONE string = storage_upmgb.outputs.primaryBlobEndpoint
output AZURE_BLOBS_ID_IMAGES_ONE string = storage_upmgb.outputs.resourceId
output AZURE_BLOBS_NAME_IMAGES_ONE string = storage_upmgb.outputs.name
output AZURE_BLOBS_ENDPOINT_IMAGES_ONE string = storage_upmgb.outputs.primaryBlobEndpoint
output AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_ONE string = '${storage_upmgb.outputs.primaryBlobEndpoint}/images'
output AZURE_BLOBS_CONTAINER_NAME_IMAGES_ONE string = 'images'
output AZURE_TABLES_ID_IMAGES_ONE string = storage_upmgb.outputs.resourceId
output AZURE_TABLES_NAME_IMAGES_ONE string = storage_upmgb.outputs.name
output AZURE_TABLES_ENDPOINT_IMAGES_ONE string = storage_upmgb.outputs.serviceEndpoints.table

module storage_o66wz 'br/public:avm/res/storage/storage-account:0.14.0' = {
  name: '${deployment().name}_storage_o66wz'
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
              name: guid('storage_o66wz', managedidentity_sbf1l.outputs.principalId, 'Storage Blob Data Contributor')
              principalId: managedidentity_sbf1l.outputs.principalId
              principalType: 'ServicePrincipal'
              roleDefinitionIdOrName: 'Storage Blob Data Contributor'
            }
            {
              name: guid('storage_o66wz', principalId, 'Storage Blob Data Contributor')
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
        name: guid('storage_o66wz', managedidentity_sbf1l.outputs.principalId, 'Storage Table Data Contributor')
        principalId: managedidentity_sbf1l.outputs.principalId
        principalType: 'ServicePrincipal'
        roleDefinitionIdOrName: 'Storage Table Data Contributor'
      }
      {
        name: guid('storage_o66wz', principalId, 'Storage Table Data Contributor')
        principalId: principalId
        principalType: 'User'
        roleDefinitionIdOrName: 'Storage Table Data Contributor'
      }
    ]
    managedIdentities: {
      userAssignedResourceIds: [
        managedidentity_sbf1l.outputs.resourceId
      ]
    }
  }
}
output AZURE_BLOBS_ID__BLOBS_TWO string = storage_o66wz.outputs.resourceId
output AZURE_BLOBS_NAME__BLOBS_TWO string = storage_o66wz.outputs.name
output AZURE_BLOBS_ENDPOINT__BLOBS_TWO string = storage_o66wz.outputs.primaryBlobEndpoint
output AZURE_BLOBS_ID_IMAGES_TWO string = storage_o66wz.outputs.resourceId
output AZURE_BLOBS_NAME_IMAGES_TWO string = storage_o66wz.outputs.name
output AZURE_BLOBS_ENDPOINT_IMAGES_TWO string = storage_o66wz.outputs.primaryBlobEndpoint
output AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_TWO string = '${storage_o66wz.outputs.primaryBlobEndpoint}/images'
output AZURE_BLOBS_CONTAINER_NAME_IMAGES_TWO string = 'images'
output AZURE_TABLES_ID_IMAGES_TWO string = storage_o66wz.outputs.resourceId
output AZURE_TABLES_NAME_IMAGES_TWO string = storage_o66wz.outputs.name
output AZURE_TABLES_ENDPOINT_IMAGES_TWO string = storage_o66wz.outputs.serviceEndpoints.table
output AZURE_BLOBS_ID_USERS string = storage_o66wz.outputs.resourceId
output AZURE_BLOBS_NAME_USERS string = storage_o66wz.outputs.name
output AZURE_BLOBS_ENDPOINT_USERS string = storage_o66wz.outputs.primaryBlobEndpoint
output AZURE_BLOBS_CONTAINER_ENDPOINT_USERS string = '${storage_o66wz.outputs.primaryBlobEndpoint}/images'
output AZURE_BLOBS_CONTAINER_NAME_USERS string = 'images'
output AZURE_TABLES_ID_USERS string = storage_o66wz.outputs.resourceId
output AZURE_TABLES_NAME_USERS string = storage_o66wz.outputs.name
output AZURE_TABLES_ENDPOINT_USERS string = storage_o66wz.outputs.serviceEndpoints.table

