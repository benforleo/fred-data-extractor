from aws_cdk import (
    Duration,
    Stack,
    aws_sqs as sqs,
)
from constructs import Construct


class FredStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stacks goes here

        # example resource
        # queue = sqs.Queue(
        #     self, "CdkInitQueue",
        #     visibility_timeout=Duration.seconds(300),
        # )
