import os
import pytest
import aws_cdk as core
import aws_cdk.assertions as assertions
from stacks.configuration.stack_configuration import stack_config
from stacks.fred_stack import FredStack


@pytest.fixture
def stack_template():
    app = core.App()
    stack = FredStack(app, "fred-stack", bucket_name='test-bucket', properties=stack_config)
    template = assertions.Template.from_stack(stack)
    return template


def test_s3_bucket_blocks_public_access(stack_template):
    stack_template.has_resource_properties("AWS::S3::Bucket", {
        "PublicAccessBlockConfiguration": {
            "BlockPublicAcls": True,
            "BlockPublicPolicy": True,
            "IgnorePublicAcls": True,
            "RestrictPublicBuckets": True
        }
    })


def test_bucket_removal_policy_is_destroy(stack_template):
    stack_template.has_resource("AWS::S3::Bucket", {
        "UpdateReplacePolicy": "Delete",
        "DeletionPolicy": "Delete"
    })
