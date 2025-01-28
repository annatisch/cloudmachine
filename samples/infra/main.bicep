targetScope = 'subscription'

@sys.description('Primary location for all resources')
@sys.minLength(1)
param location string

@sys.description('AZD environment name')
@sys.maxLength(64)
@sys.minLength(1)
param environmentName string

@sys.description('Id of the user or app to assign application roles')
param principalId string

module module_bd70d 'testappa.bicep' = {
  name: '${deployment().name}_module_bd70d'
  params: {
    location: location
    environmentName: environmentName
    principalId: principalId
  }
}
output AZURE_IDENTITY_ID_SBF1L string = module_bd70d.outputs.AZURE_IDENTITY_ID_SBF1L
output AZURE_IDENTITY_NAME_SBF1L string = module_bd70d.outputs.AZURE_IDENTITY_NAME_SBF1L
output AZURE_CLIENT_ID string = module_bd70d.outputs.AZURE_CLIENT_ID
output AZURE_BLOBS_ID__BLOBS_ONE string = module_bd70d.outputs.AZURE_BLOBS_ID__BLOBS_ONE
output AZURE_BLOBS_NAME__BLOBS_ONE string = module_bd70d.outputs.AZURE_BLOBS_NAME__BLOBS_ONE
output AZURE_BLOBS_ENDPOINT__BLOBS_ONE string = module_bd70d.outputs.AZURE_BLOBS_ENDPOINT__BLOBS_ONE
output AZURE_BLOBS_ID_IMAGES_ONE string = module_bd70d.outputs.AZURE_BLOBS_ID_IMAGES_ONE
output AZURE_BLOBS_NAME_IMAGES_ONE string = module_bd70d.outputs.AZURE_BLOBS_NAME_IMAGES_ONE
output AZURE_BLOBS_ENDPOINT_IMAGES_ONE string = module_bd70d.outputs.AZURE_BLOBS_ENDPOINT_IMAGES_ONE
output AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_ONE string = module_bd70d.outputs.AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_ONE
output AZURE_BLOBS_CONTAINER_NAME_IMAGES_ONE string = module_bd70d.outputs.AZURE_BLOBS_CONTAINER_NAME_IMAGES_ONE
output AZURE_TABLES_ID_IMAGES_ONE string = module_bd70d.outputs.AZURE_TABLES_ID_IMAGES_ONE
output AZURE_TABLES_NAME_IMAGES_ONE string = module_bd70d.outputs.AZURE_TABLES_NAME_IMAGES_ONE
output AZURE_TABLES_ENDPOINT_IMAGES_ONE string = module_bd70d.outputs.AZURE_TABLES_ENDPOINT_IMAGES_ONE
output AZURE_BLOBS_ID__BLOBS_TWO string = module_bd70d.outputs.AZURE_BLOBS_ID__BLOBS_TWO
output AZURE_BLOBS_NAME__BLOBS_TWO string = module_bd70d.outputs.AZURE_BLOBS_NAME__BLOBS_TWO
output AZURE_BLOBS_ENDPOINT__BLOBS_TWO string = module_bd70d.outputs.AZURE_BLOBS_ENDPOINT__BLOBS_TWO
output AZURE_BLOBS_ID_IMAGES_TWO string = module_bd70d.outputs.AZURE_BLOBS_ID_IMAGES_TWO
output AZURE_BLOBS_NAME_IMAGES_TWO string = module_bd70d.outputs.AZURE_BLOBS_NAME_IMAGES_TWO
output AZURE_BLOBS_ENDPOINT_IMAGES_TWO string = module_bd70d.outputs.AZURE_BLOBS_ENDPOINT_IMAGES_TWO
output AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_TWO string = module_bd70d.outputs.AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_TWO
output AZURE_BLOBS_CONTAINER_NAME_IMAGES_TWO string = module_bd70d.outputs.AZURE_BLOBS_CONTAINER_NAME_IMAGES_TWO
output AZURE_TABLES_ID_IMAGES_TWO string = module_bd70d.outputs.AZURE_TABLES_ID_IMAGES_TWO
output AZURE_TABLES_NAME_IMAGES_TWO string = module_bd70d.outputs.AZURE_TABLES_NAME_IMAGES_TWO
output AZURE_TABLES_ENDPOINT_IMAGES_TWO string = module_bd70d.outputs.AZURE_TABLES_ENDPOINT_IMAGES_TWO
output AZURE_BLOBS_ID_USERS string = module_bd70d.outputs.AZURE_BLOBS_ID_USERS
output AZURE_BLOBS_NAME_USERS string = module_bd70d.outputs.AZURE_BLOBS_NAME_USERS
output AZURE_BLOBS_ENDPOINT_USERS string = module_bd70d.outputs.AZURE_BLOBS_ENDPOINT_USERS
output AZURE_BLOBS_CONTAINER_ENDPOINT_USERS string = module_bd70d.outputs.AZURE_BLOBS_CONTAINER_ENDPOINT_USERS
output AZURE_BLOBS_CONTAINER_NAME_USERS string = module_bd70d.outputs.AZURE_BLOBS_CONTAINER_NAME_USERS
output AZURE_TABLES_ID_USERS string = module_bd70d.outputs.AZURE_TABLES_ID_USERS
output AZURE_TABLES_NAME_USERS string = module_bd70d.outputs.AZURE_TABLES_NAME_USERS
output AZURE_TABLES_ENDPOINT_USERS string = module_bd70d.outputs.AZURE_TABLES_ENDPOINT_USERS

module module_65jtj 'testappb.bicep' = {
  name: '${deployment().name}_module_65jtj'
  params: {
    location: location
    environmentName: environmentName
    principalId: principalId
  }
}
output AZURE_IDENTITY_ID_P88WX string = module_65jtj.outputs.AZURE_IDENTITY_ID_P88WX
output AZURE_IDENTITY_NAME_P88WX string = module_65jtj.outputs.AZURE_IDENTITY_NAME_P88WX
// Error - duplicate output
// output AZURE_CLIENT_ID string = module_65jtj.outputs.AZURE_CLIENT_ID
output AZURE_BLOBS_ID__BLOBS_THREE string = module_65jtj.outputs.AZURE_BLOBS_ID__BLOBS_THREE
output AZURE_BLOBS_NAME__BLOBS_THREE string = module_65jtj.outputs.AZURE_BLOBS_NAME__BLOBS_THREE
output AZURE_BLOBS_ENDPOINT__BLOBS_THREE string = module_65jtj.outputs.AZURE_BLOBS_ENDPOINT__BLOBS_THREE
output AZURE_BLOBS_ID_IMAGES_THREE string = module_65jtj.outputs.AZURE_BLOBS_ID_IMAGES_THREE
output AZURE_BLOBS_NAME_IMAGES_THREE string = module_65jtj.outputs.AZURE_BLOBS_NAME_IMAGES_THREE
output AZURE_BLOBS_ENDPOINT_IMAGES_THREE string = module_65jtj.outputs.AZURE_BLOBS_ENDPOINT_IMAGES_THREE
output AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_THREE string = module_65jtj.outputs.AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_THREE
output AZURE_BLOBS_CONTAINER_NAME_IMAGES_THREE string = module_65jtj.outputs.AZURE_BLOBS_CONTAINER_NAME_IMAGES_THREE
output AZURE_BLOBS_ID__BLOBS_FOUR string = module_65jtj.outputs.AZURE_BLOBS_ID__BLOBS_FOUR
output AZURE_BLOBS_NAME__BLOBS_FOUR string = module_65jtj.outputs.AZURE_BLOBS_NAME__BLOBS_FOUR
output AZURE_BLOBS_ENDPOINT__BLOBS_FOUR string = module_65jtj.outputs.AZURE_BLOBS_ENDPOINT__BLOBS_FOUR
output AZURE_BLOBS_ID_IMAGES_FOUR string = module_65jtj.outputs.AZURE_BLOBS_ID_IMAGES_FOUR
output AZURE_BLOBS_NAME_IMAGES_FOUR string = module_65jtj.outputs.AZURE_BLOBS_NAME_IMAGES_FOUR
output AZURE_BLOBS_ENDPOINT_IMAGES_FOUR string = module_65jtj.outputs.AZURE_BLOBS_ENDPOINT_IMAGES_FOUR
output AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_FOUR string = module_65jtj.outputs.AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_FOUR
output AZURE_BLOBS_CONTAINER_NAME_IMAGES_FOUR string = module_65jtj.outputs.AZURE_BLOBS_CONTAINER_NAME_IMAGES_FOUR

