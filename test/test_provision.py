from unittest import mock
import os
import filecmp
import pytest
import difflib


from azure.cloudmachine import export, provision, Parameter
from azure.cloudmachine.resources.storage import StorageAccount
from azure.cloudmachine.resources.resourcegroup import ResourceGroup
from azure.cloudmachine.resources.managedidentity import UserAssignedIdentity
from azure.cloudmachine.resources.ai import AIServices
from azure.cloudmachine.resources.ai.deployment import AIDeployment, AIChat, AIEmbeddings




# def test_export_resource(export_dir):
    
#     test_param = Parameter('TestAccessTier', varname='STORAGE_ACCESS_TIER', default="Hot")
#     rg = ResourceGroup.reference(name='antisch-cmtest')
#     ua = UserAssignedIdentity.reference(name='uatest', resource_group='foo')
#     r = StorageAccount(user_role='Storage Blob Data Owner', access_tier=test_param)
#     export(
#         rg, ua, r,
#         config={'TestAccessTier': 'Cold'},
#         name="test",
#         output_dir=export_dir,
#     )

