import pytest
import aws_cdk as core
import aws_cdk.assertions as assertions
from stacks.configuration.stack_configuration import stack_config
from stacks.fred_stack import FredStack


@pytest.fixture(scope='module')
def stack_template():
    app = core.App()
    stack = FredStack(app, "fred-stack", bucket_name='test-bucket', properties=stack_config)
    template = assertions.Template.from_stack(stack)
    return template
