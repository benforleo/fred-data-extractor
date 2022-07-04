import aws_cdk as core
import aws_cdk.assertions as assertions
from stacks.configuration.stack_configuration import stack_config
from stacks.fred_stack import FredStack


def test_s3_bucket_blocks_public_access():
    app = core.App()
    stack = FredStack(app, "fred-stack", properties=stack_config)
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::S3::Bucket", {
        "PublicAccessBlockConfiguration": {
            "BlockPublicAcls": True,
            "BlockPublicPolicy": True,
            "IgnorePublicAcls": True,
            "RestrictPublicBuckets": True
        }
    })
