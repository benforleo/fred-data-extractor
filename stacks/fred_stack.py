from aws_cdk import (
    Stack
)
from constructs import Construct
from stacks.s3.s3_construct import S3Construct
from stacks.lambda_.lambda_ import LambdaConstruct
from stacks.scheduler.scheduler import FredSchedulerConstruct


class FredStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, bucket_name, properties: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, env=properties['ENV'], **kwargs)

        bucket = S3Construct(self, 's3-bucket') \
            .create_bucket(
            bucket_name=bucket_name,
        )

        lambda_ = LambdaConstruct(self, 'my-lambda', bucket) \
            .python_lambda_generator()

        FredSchedulerConstruct(self, 'fred-scheduler', lambda_).apply_schedule("cron(0 8 ? * TUE-SAT *)")
