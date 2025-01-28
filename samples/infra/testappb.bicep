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

module resources_t576l 'br/public:avm/res/resources/resource-group:0.4.0' = {
  name: '${deployment().name}_resources_t576l'
  params: {
    name: resourcegroup_default_name
    location: location
    tags: tags
  }
}

module managedidentity_04cnb 'br/public:avm/res/managed-identity/user-assigned-identity:0.4.0' = {
  name: '${deployment().name}_managedidentity_04cnb'
  scope: resourceGroup(resourcegroup_default_name)
  params: {
    name: cloudmachineId
    location: location
    tags: tags
  }
}
output AZURE_IDENTITY_ID_04CNB string = managedidentity_04cnb.outputs.resourceId
output AZURE_IDENTITY_NAME_04CNB string = managedidentity_04cnb.outputs.name
output AZURE_CLIENT_ID string = managedidentity_04cnb.outputs.clientId

module storage_u50mx 'br/public:avm/res/storage/storage-account:0.14.0' = {
  name: '${deployment().name}_storage_u50mx'
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
              name: guid('storage_i3fcz', managedidentity_i1sdu.outputs.principalId, 'Storage Blob Data Contributor')
              principalId: managedidentity_i1sdu.outputs.principalId
              principalType: 'ServicePrincipal'
              roleDefinitionIdOrName: 'Storage Blob Data Contributor'
            }
            {
              name: guid('storage_i3fcz', principalId, 'Storage Blob Data Contributor')
              principalId: principalId
              principalType: 'User'
              roleDefinitionIdOrName: 'Storage Blob Data Contributor'
            }
          ]
        }
      ]
    }
    roleAssignments: [
      {
        name: guid('storage_u50mx', managedidentity_04cnb.outputs.principalId, 'Storage Blob Data Contributor')
        principalId: managedidentity_04cnb.outputs.principalId
        principalType: 'ServicePrincipal'
        roleDefinitionIdOrName: 'Storage Blob Data Contributor'
      }
      {
        name: guid('storage_u50mx', principalId, 'Storage Blob Data Contributor')
        principalId: principalId
        principalType: 'User'
        roleDefinitionIdOrName: 'Storage Blob Data Contributor'
      }
    ]
    managedIdentities: {
      userAssignedResourceIds: [
        managedidentity_04cnb.outputs.resourceId
      ]
    }
  }
}
output AZURE_BLOBS_ID__BLOBS_THREE string = storage_u50mx.outputs.resourceId
output AZURE_BLOBS_NAME__BLOBS_THREE string = storage_u50mx.outputs.name
output AZURE_BLOBS_ENDPOINT__BLOBS_THREE string = storage_u50mx.outputs.primaryBlobEndpoint
output AZURE_BLOBS_ID_IMAGES_THREE string = storage_u50mx.outputs.resourceId
output AZURE_BLOBS_NAME_IMAGES_THREE string = storage_u50mx.outputs.name
output AZURE_BLOBS_ENDPOINT_IMAGES_THREE string = storage_u50mx.outputs.primaryBlobEndpoint
output AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_THREE string = '${storage_u50mx.outputs.primaryBlobEndpoint}/images'
output AZURE_BLOBS_CONTAINER_NAME_IMAGES_THREE string = 'images'

module storage_qv11t 'br/public:avm/res/storage/storage-account:0.14.0' = {
  name: '${deployment().name}_storage_qv11t'
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
              name: guid('storage_i3fcz', managedidentity_i1sdu.outputs.principalId, 'Storage Blob Data Contributor')
              principalId: managedidentity_i1sdu.outputs.principalId
              principalType: 'ServicePrincipal'
              roleDefinitionIdOrName: 'Storage Blob Data Contributor'
            }
            {
              name: guid('storage_i3fcz', principalId, 'Storage Blob Data Contributor')
              principalId: principalId
              principalType: 'User'
              roleDefinitionIdOrName: 'Storage Blob Data Contributor'
            }
          ]
        }
      ]
    }
    managedIdentities: {
      userAssignedResourceIds: [
        managedidentity_04cnb.outputs.resourceId
      ]
    }
  }
}
output AZURE_BLOBS_ID__BLOBS_FOUR string = storage_qv11t.outputs.resourceId
output AZURE_BLOBS_NAME__BLOBS_FOUR string = storage_qv11t.outputs.name
output AZURE_BLOBS_ENDPOINT__BLOBS_FOUR string = storage_qv11t.outputs.primaryBlobEndpoint
output AZURE_BLOBS_ID_IMAGES_FOUR string = storage_qv11t.outputs.resourceId
output AZURE_BLOBS_NAME_IMAGES_FOUR string = storage_qv11t.outputs.name
output AZURE_BLOBS_ENDPOINT_IMAGES_FOUR string = storage_qv11t.outputs.primaryBlobEndpoint
output AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_FOUR string = '${storage_qv11t.outputs.primaryBlobEndpoint}/images'
output AZURE_BLOBS_CONTAINER_NAME_IMAGES_FOUR string = 'images'

