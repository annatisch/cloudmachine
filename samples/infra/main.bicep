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

module module_nw7gt 'testappa.bicep' = {
  name: '${deployment().name}_module_nw7gt'
  params: {
    location: location
    environmentName: environmentName
    principalId: principalId
  }
}
output AZURE_CLIENT_ID string = module_nw7gt.outputs.AZURE_CLIENT_ID
output AZURE_BLOBS_ID_IMAGES_ONE string = module_nw7gt.outputs.AZURE_BLOBS_ID_IMAGES_ONE
output AZURE_BLOBS_NAME_IMAGES_ONE string = module_nw7gt.outputs.AZURE_BLOBS_NAME_IMAGES_ONE
output AZURE_BLOBS_ENDPOINT_IMAGES_ONE string = module_nw7gt.outputs.AZURE_BLOBS_ENDPOINT_IMAGES_ONE
output AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_ONE string = module_nw7gt.outputs.AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_ONE
output AZURE_BLOBS_CONTAINER_NAME_IMAGES_ONE string = module_nw7gt.outputs.AZURE_BLOBS_CONTAINER_NAME_IMAGES_ONE
output AZURE_BLOBS_ID_IMAGES_TWO string = module_nw7gt.outputs.AZURE_BLOBS_ID_IMAGES_TWO
output AZURE_BLOBS_NAME_IMAGES_TWO string = module_nw7gt.outputs.AZURE_BLOBS_NAME_IMAGES_TWO
output AZURE_BLOBS_ENDPOINT_IMAGES_TWO string = module_nw7gt.outputs.AZURE_BLOBS_ENDPOINT_IMAGES_TWO
output AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_TWO string = module_nw7gt.outputs.AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_TWO
output AZURE_BLOBS_CONTAINER_NAME_IMAGES_TWO string = module_nw7gt.outputs.AZURE_BLOBS_CONTAINER_NAME_IMAGES_TWO
output AZURE_TABLES_ID_USERS string = module_nw7gt.outputs.AZURE_TABLES_ID_USERS
output AZURE_TABLES_NAME_USERS string = module_nw7gt.outputs.AZURE_TABLES_NAME_USERS
output AZURE_TABLES_ENDPOINT_USERS string = module_nw7gt.outputs.AZURE_TABLES_ENDPOINT_USERS

module module_7xk1z 'testappb.bicep' = {
  name: '${deployment().name}_module_7xk1z'
  params: {
    location: location
    environmentName: environmentName
    principalId: principalId
  }
}
// Error - duplicate output
// output AZURE_CLIENT_ID string = module_7xk1z.outputs.AZURE_CLIENT_ID
output AZURE_BLOBS_ID__BLOBS_THREE string = module_7xk1z.outputs.AZURE_BLOBS_ID__BLOBS_THREE
output AZURE_BLOBS_NAME__BLOBS_THREE string = module_7xk1z.outputs.AZURE_BLOBS_NAME__BLOBS_THREE
output AZURE_BLOBS_ENDPOINT__BLOBS_THREE string = module_7xk1z.outputs.AZURE_BLOBS_ENDPOINT__BLOBS_THREE
output AZURE_BLOBS_ID_IMAGES_THREE string = module_7xk1z.outputs.AZURE_BLOBS_ID_IMAGES_THREE
output AZURE_BLOBS_NAME_IMAGES_THREE string = module_7xk1z.outputs.AZURE_BLOBS_NAME_IMAGES_THREE
output AZURE_BLOBS_ENDPOINT_IMAGES_THREE string = module_7xk1z.outputs.AZURE_BLOBS_ENDPOINT_IMAGES_THREE
output AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_THREE string = module_7xk1z.outputs.AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_THREE
output AZURE_BLOBS_CONTAINER_NAME_IMAGES_THREE string = module_7xk1z.outputs.AZURE_BLOBS_CONTAINER_NAME_IMAGES_THREE
output AZURE_BLOBS_ID__BLOBS_FOUR string = module_7xk1z.outputs.AZURE_BLOBS_ID__BLOBS_FOUR
output AZURE_BLOBS_NAME__BLOBS_FOUR string = module_7xk1z.outputs.AZURE_BLOBS_NAME__BLOBS_FOUR
output AZURE_BLOBS_ENDPOINT__BLOBS_FOUR string = module_7xk1z.outputs.AZURE_BLOBS_ENDPOINT__BLOBS_FOUR
output AZURE_BLOBS_ID_IMAGES_FOUR string = module_7xk1z.outputs.AZURE_BLOBS_ID_IMAGES_FOUR
output AZURE_BLOBS_NAME_IMAGES_FOUR string = module_7xk1z.outputs.AZURE_BLOBS_NAME_IMAGES_FOUR
output AZURE_BLOBS_ENDPOINT_IMAGES_FOUR string = module_7xk1z.outputs.AZURE_BLOBS_ENDPOINT_IMAGES_FOUR
output AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_FOUR string = module_7xk1z.outputs.AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_FOUR
output AZURE_BLOBS_CONTAINER_NAME_IMAGES_FOUR string = module_7xk1z.outputs.AZURE_BLOBS_CONTAINER_NAME_IMAGES_FOUR

