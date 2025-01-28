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

module module_vfm0s 'testappb.bicep' = {
  name: '${deployment().name}_module_vfm0s'
  params: {
    location: location
    environmentName: environmentName
    principalId: principalId
  }
}
output AZURE_IDENTITY_ID_04CNB string = module_vfm0s.outputs.AZURE_IDENTITY_ID_04CNB
output AZURE_IDENTITY_NAME_04CNB string = module_vfm0s.outputs.AZURE_IDENTITY_NAME_04CNB
output AZURE_CLIENT_ID string = module_vfm0s.outputs.AZURE_CLIENT_ID
output AZURE_BLOBS_ID__BLOBS_THREE string = module_vfm0s.outputs.AZURE_BLOBS_ID__BLOBS_THREE
output AZURE_BLOBS_NAME__BLOBS_THREE string = module_vfm0s.outputs.AZURE_BLOBS_NAME__BLOBS_THREE
output AZURE_BLOBS_ENDPOINT__BLOBS_THREE string = module_vfm0s.outputs.AZURE_BLOBS_ENDPOINT__BLOBS_THREE
output AZURE_BLOBS_ID_IMAGES_THREE string = module_vfm0s.outputs.AZURE_BLOBS_ID_IMAGES_THREE
output AZURE_BLOBS_NAME_IMAGES_THREE string = module_vfm0s.outputs.AZURE_BLOBS_NAME_IMAGES_THREE
output AZURE_BLOBS_ENDPOINT_IMAGES_THREE string = module_vfm0s.outputs.AZURE_BLOBS_ENDPOINT_IMAGES_THREE
output AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_THREE string = module_vfm0s.outputs.AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_THREE
output AZURE_BLOBS_CONTAINER_NAME_IMAGES_THREE string = module_vfm0s.outputs.AZURE_BLOBS_CONTAINER_NAME_IMAGES_THREE
output AZURE_BLOBS_ID__BLOBS_FOUR string = module_vfm0s.outputs.AZURE_BLOBS_ID__BLOBS_FOUR
output AZURE_BLOBS_NAME__BLOBS_FOUR string = module_vfm0s.outputs.AZURE_BLOBS_NAME__BLOBS_FOUR
output AZURE_BLOBS_ENDPOINT__BLOBS_FOUR string = module_vfm0s.outputs.AZURE_BLOBS_ENDPOINT__BLOBS_FOUR
output AZURE_BLOBS_ID_IMAGES_FOUR string = module_vfm0s.outputs.AZURE_BLOBS_ID_IMAGES_FOUR
output AZURE_BLOBS_NAME_IMAGES_FOUR string = module_vfm0s.outputs.AZURE_BLOBS_NAME_IMAGES_FOUR
output AZURE_BLOBS_ENDPOINT_IMAGES_FOUR string = module_vfm0s.outputs.AZURE_BLOBS_ENDPOINT_IMAGES_FOUR
output AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_FOUR string = module_vfm0s.outputs.AZURE_BLOBS_CONTAINER_ENDPOINT_IMAGES_FOUR
output AZURE_BLOBS_CONTAINER_NAME_IMAGES_FOUR string = module_vfm0s.outputs.AZURE_BLOBS_CONTAINER_NAME_IMAGES_FOUR
