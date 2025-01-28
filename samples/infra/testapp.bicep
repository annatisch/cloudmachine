targetScope = 'subscription'

param location string
param environmentName string
param principalId string
var tags = {
  'azd-env-name': environmentName
}


@sys.description('Unique identifier for creating default resource names')
var cloudmachineId = uniqueString(subscription().subscriptionId, 'testapp', location)

var resourcegroup_default_name = cloudmachineId

module resources_w7v9j 'br/public:avm/res/resources/resource-group:0.4.0' = {
  name: '${deployment().name}_resources_w7v9j'
  params: {
    name: resourcegroup_default_name
    location: location
    tags: tags
  }
}

module managedidentity_3op8e 'br/public:avm/res/managed-identity/user-assigned-identity:0.4.0' = {
  name: '${deployment().name}_managedidentity_3op8e'
  scope: resourceGroup(resourcegroup_default_name)
  params: {
    name: cloudmachineId
    location: location
    tags: tags
  }
}
output AZURE_IDENTITY_ID_3OP8E string = managedidentity_3op8e.outputs.resourceId
output AZURE_IDENTITY_NAME_3OP8E string = managedidentity_3op8e.outputs.name
output AZURE_CLIENT_ID string = managedidentity_3op8e.outputs.clientId

module storage_ktux5 'br/public:avm/res/storage/storage-account:0.14.0' = {
  name: '${deployment().name}_storage_ktux5'
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
              name: guid('storage_ktux5', managedidentity_3op8e.outputs.principalId, 'Storage Blob Data Contributor')
              principalId: managedidentity_3op8e.outputs.principalId
              principalType: 'ServicePrincipal'
              roleDefinitionIdOrName: 'Storage Blob Data Contributor'
            }
            {
              name: guid('storage_ktux5', principalId, 'Storage Blob Data Contributor')
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
        name: guid('storage_ktux5', managedidentity_3op8e.outputs.principalId, 'Storage Blob Data Contributor')
        principalId: managedidentity_3op8e.outputs.principalId
        principalType: 'ServicePrincipal'
        roleDefinitionIdOrName: 'Storage Blob Data Contributor'
      }
      {
        name: guid('storage_ktux5', principalId, 'Storage Blob Data Contributor')
        principalId: principalId
        principalType: 'User'
        roleDefinitionIdOrName: 'Storage Blob Data Contributor'
      }
    ]
    managedIdentities: {
      userAssignedResourceIds: [
        managedidentity_3op8e.outputs.resourceId
      ]
    }
  }
}

module storage_6joxb 'br/public:avm/res/storage/storage-account:0.14.0' = {
  name: '${deployment().name}_storage_6joxb'
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
              name: guid('storage_6joxb', managedidentity_3op8e.outputs.principalId, 'Storage Blob Data Contributor')
              principalId: managedidentity_3op8e.outputs.principalId
              principalType: 'ServicePrincipal'
              roleDefinitionIdOrName: 'Storage Blob Data Contributor'
            }
            {
              name: guid('storage_6joxb', principalId, 'Storage Blob Data Contributor')
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
        managedidentity_3op8e.outputs.resourceId
      ]
    }
  }
}

