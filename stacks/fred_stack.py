import os
from aws_cdk import (
    Stack
)
from constructs import Construct
from .s3.s3 import S3Construct
from .lambda_.lambda_ import LambdaConstruct
from .configuration.stack_configuration import stack_config


class FredStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, bucket_name, properties: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, env=stack_config['ENV'], **kwargs)

        # S3 Bucket for storing data
        bucket = S3Construct(self, 's3-bucket') \
            .create_bucket(
            bucket_name=bucket_name,
        )

        lambda_ = LambdaConstruct(self, 'my-lambda', bucket) \
            .python_lambda_generator()
