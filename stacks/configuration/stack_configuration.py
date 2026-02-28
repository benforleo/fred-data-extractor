import os

stack_config = {"ENV": {"region": os.getenv("CDK_DEFAULT_REGION", "us-east-1"), "account": os.getenv("AWS_ACCOUNT_ID")}}
