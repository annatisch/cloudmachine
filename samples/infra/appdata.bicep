targetScope = 'subscription'

param location string
param environmentName string
param principalId string
var tags = {
  'azd-env-name': environmentName
}


@sys.description('Unique identifier for creating default resource names')
var cloudmachineId = uniqueString(subscription().subscriptionId, 'appdata', location)

var resourcegroup_default_name = cloudmachineId

module resources_uthat 'br/public:avm/res/resources/resource-group:0.4.0' = {
  name: '${deployment().name}_resources_uthat'
  params: {
    name: resourcegroup_default_name
    location: location
    tags: tags
  }
}

module managedidentity_y0fyb 'br/public:avm/res/managed-identity/user-assigned-identity:0.4.0' = {
  name: '${deployment().name}_managedidentity_y0fyb'
  scope: resourceGroup(resourcegroup_default_name)
  params: {
    name: cloudmachineId
    location: location
    tags: tags
  }
}
output AZURE_CLIENT_ID string = managedidentity_y0fyb.outputs.clientId

module storage_b28gu 'br/public:avm/res/storage/storage-account:0.14.0' = {
  name: '${deployment().name}_storage_b28gu'
  scope: resourceGroup(resourcegroup_default_name)
  params: {
    accessTier: 'Hot'
    allowBlobPublicAccess: false
    kind: 'StorageV2'
    skuName: 'Standard_LRS'
    name: cloudmachineId
    blobServices: {}
    location: location
    tags: tags
    queueServices: {
      queues: [
        {
          name: cloudmachineId
        }
      ]
    }
    roleAssignments: [
      {
        name: guid('storage_b28gu', managedidentity_y0fyb.outputs.principalId, 'Storage Blob Data Contributor')
        principalId: managedidentity_y0fyb.outputs.principalId
        principalType: 'ServicePrincipal'
        roleDefinitionIdOrName: 'Storage Blob Data Contributor'
      }
      {
        name: guid('storage_b28gu', principalId, 'Storage Blob Data Contributor')
        principalId: principalId
        principalType: 'User'
        roleDefinitionIdOrName: 'Storage Blob Data Contributor'
      }
      {
        name: guid('storage_b28gu', managedidentity_y0fyb.outputs.principalId, 'Storage Queue Data Contributor')
        principalId: managedidentity_y0fyb.outputs.principalId
        principalType: 'ServicePrincipal'
        roleDefinitionIdOrName: 'Storage Queue Data Contributor'
      }
      {
        name: guid('storage_b28gu', principalId, 'Storage Queue Data Contributor')
        principalId: principalId
        principalType: 'User'
        roleDefinitionIdOrName: 'Storage Queue Data Contributor'
      }
    ]
    managedIdentities: {
      userAssignedResourceIds: [
        managedidentity_y0fyb.outputs.resourceId
      ]
    }
  }
}
output AZURE_BLOBS_ID_DATA string = storage_b28gu.outputs.resourceId
output AZURE_BLOBS_NAME_DATA string = storage_b28gu.outputs.name
output AZURE_BLOBS_ENDPOINT_DATA string = storage_b28gu.outputs.primaryBlobEndpoint
output AZURE_QUEUES_ID_MESSAGES string = storage_b28gu.outputs.resourceId
output AZURE_QUEUES_NAME_MESSAGES string = storage_b28gu.outputs.name
output AZURE_QUEUES_ENDPOINT_MESSAGES string = storage_b28gu.outputs.serviceEndpoints.queue

module eventgrid_8le0h 'br/public:avm/res/event-grid/system-topic:0.4.0' = {
  name: '${deployment().name}_eventgrid_8le0h'
  scope: resourceGroup(resourcegroup_default_name)
  params: {
    name: cloudmachineId
    eventSubscriptions: [
      {
        filter: {
          includedEventTypes: [
            'Microsoft.Storage.BlobCreated'
          ]
        }
        deliveryWithResourceIdentity: {
          identity: {
            type: 'UserAssigned'
            userAssignedIdentity: managedidentity_y0fyb.outputs.resourceId
          }
          destination: {
            endpointType: 'StorageQueue'
            properties: {
              queueName: cloudmachineId
              queueMessageTimeToLiveInSeconds: -1
              resourceId: storage_b28gu.outputs.resourceId
            }
          }
        }
      }
    ]
    topicType: 'Microsoft.Storage.StorageAccounts'
    source: storage_b28gu.outputs.resourceId
    location: location
    tags: tags
    managedIdentities: {
      userAssignedResourcesIds: [
        managedidentity_y0fyb.outputs.resourceId
      ]
    }
  }
}

