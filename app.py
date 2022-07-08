#!/usr/bin/env python3
import os
import aws_cdk as cdk
from stacks.fred_stack import FredStack
from stacks.configuration.stack_configuration import stack_config

bucket_name = os.getenv("FRED_BUCKET_NAME")

app = cdk.App()
FredStack(app, "FredStack", bucket_name=bucket_name, properties=stack_config)
app.synth()
