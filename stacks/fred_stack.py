from aws_cdk import Stack
from constructs import Construct

from stacks.lambda_.lambda_ import LambdaConstruct
from stacks.s3.s3_construct import S3Construct

# from stacks.scheduler.scheduler import FredSchedulerConstruct


class FredStack(Stack):
    """Cloudformation stack for FRED data extraction infrastructure.

    Creates and configures:
    - S3 bucket for data storage
    - Lambda function for data extraction
    - IAM roles and permissions
    """

    def __init__(self, scope: Construct, construct_id: str, bucket_name, properties: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, env=properties["ENV"], **kwargs)

        bucket = S3Construct(self, "S3Construct").create_bucket(
            bucket_name=bucket_name,
            enable_versioning=True,
            enable_lifecycle_rules=True,
            auto_delete_objects=True,
        )

        LambdaConstruct(self, "LambdaConstruct", bucket, self.env.account, self.env.region).python_lambda_generator()

        # FredSchedulerConstruct(self, "FredSchedulerConstruct", lambda_).apply_schedule("cron(0 8 ? * TUE-SAT *)")
