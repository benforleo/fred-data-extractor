import os
import pytest
import aws_cdk as core
import aws_cdk.assertions as assertions
from stacks.configuration.stack_configuration import stack_config
from stacks.fred_stack import FredStack


@pytest.mark.slow
class TestCDKInfrastructure:
    def test_s3_bucket_blocks_public_access(self, stack_template):
        stack_template.has_resource_properties("AWS::S3::Bucket", {
            "PublicAccessBlockConfiguration": {
                "BlockPublicAcls": True,
                "BlockPublicPolicy": True,
                "IgnorePublicAcls": True,
                "RestrictPublicBuckets": True
            }
        })

    def test_bucket_removal_policy_is_destroy(self, stack_template):
        stack_template.has_resource("AWS::S3::Bucket", {
            "UpdateReplacePolicy": "Delete",
            "DeletionPolicy": "Delete"
        })
