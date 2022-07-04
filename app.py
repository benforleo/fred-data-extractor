#!/usr/bin/env python3
import os
import aws_cdk as cdk
from stacks.fred_stack import FredStack


app = cdk.App()
FredStack(app, "FredStack")
app.synth()
