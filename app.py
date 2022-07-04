#!/usr/bin/env python3
import os
import aws_cdk as cdk
from stacks.fred_stack import FredStack
from stacks.configuration.stack_configuration import stack_config


app = cdk.App()
FredStack(app, "FredStack", properties=stack_config)
app.synth()
