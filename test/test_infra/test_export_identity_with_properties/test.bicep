param location string
param environmentName string
param defaultName string
param principalId string
param azdTags object

resource userassignedidentity_foo 'Microsoft.ManagedIdentity/userAssignedIdentities@2024-11-30' = {
  name: 'foo'
  location: 'westus'
  tags: {
    key: 'value'
  }
}

output AZURE_CLIENT_ID string = userassignedidentity_foo.properties.clientId


