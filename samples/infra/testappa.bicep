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

module resources_6x7p9 'br/public:avm/res/resources/resource-group:0.4.0' = {
  name: '${deployment().name}_resources_6x7p9'
  params: {
    name: resourcegroup_default_name
    location: location
    tags: tags
  }
}

module managedidentity_i1sdu 'br/public:avm/res/managed-identity/user-assigned-identity:0.4.0' = {
  name: '${deployment().name}_managedidentity_i1sdu'
  scope: resourceGroup(resourcegroup_default_name)
  params: {
    name: cloudmachineId
    location: location
    tags: tags
  }
}
output AZURE_IDENTITY_ID_I1SDU string = managedidentity_i1sdu.outputs.resourceId
output AZURE_IDENTITY_NAME_I1SDU string = managedidentity_i1sdu.outputs.name
output AZURE_CLIENT_ID string = managedidentity_i1sdu.outputs.clientId

module storage_i3fcz 'br/public:avm/res/storage/storage-account:0.14.0' = {
  name: '${deployment().name}_storage_i3fcz'
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
    managedIdentities: {
      userAssignedResourceIds: [
        managedidentity_i1sdu.outputs.resourceId
      ]
    }
  }
}
output AZURE_BLOBS_ID__BLOBS_ONE string = storage_i3fcz.outputs.resourceId
output AZURE_BLOBS_NAME__BLOBS_ONE string = storage_i3fcz.outputs.name
output AZURE_BLOBS_ENDPOINT__BLOBS_ONE string = storage_i3fcz.outputs.primaryBlobEndpoint
output AZURE_BLOBS_ID_IMAGES_ONE string = storage_i3fcz.outputs.resourceId
output AZURE_BLOBS_NAME_IMAGES_ONE string = storage_i3fcz.outputs.name
output AZURE_BLOBS_ENDPOINT_IMAGES_ONE string = storage_i3fcz.outputs.primaryBlobEndpoint
output AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_ONE string = '${storage_i3fcz.outputs.primaryBlobEndpoint}/images'
output AZURE_BLOBS_CONTAINER_NAME_IMAGES_ONE string = 'images'

module storage_zipbs 'br/public:avm/res/storage/storage-account:0.14.0' = {
  name: '${deployment().name}_storage_zipbs'
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
        managedidentity_i1sdu.outputs.resourceId
      ]
    }
  }
}
output AZURE_BLOBS_ID__BLOBS_TWO string = storage_zipbs.outputs.resourceId
output AZURE_BLOBS_NAME__BLOBS_TWO string = storage_zipbs.outputs.name
output AZURE_BLOBS_ENDPOINT__BLOBS_TWO string = storage_zipbs.outputs.primaryBlobEndpoint
output AZURE_BLOBS_ID_IMAGES_TWO string = storage_zipbs.outputs.resourceId
output AZURE_BLOBS_NAME_IMAGES_TWO string = storage_zipbs.outputs.name
output AZURE_BLOBS_ENDPOINT_IMAGES_TWO string = storage_zipbs.outputs.primaryBlobEndpoint
output AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_TWO string = '${storage_zipbs.outputs.primaryBlobEndpoint}/images'
output AZURE_BLOBS_CONTAINER_NAME_IMAGES_TWO string = 'images'

