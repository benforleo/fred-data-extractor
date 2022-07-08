import aws_cdk as cdk
from aws_cdk import (
    aws_s3 as s3
)
from constructs import Construct


class S3Construct(Construct):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

    def create_bucket(self, bucket_name):

        return s3.Bucket(
            self,
            's3-bucket-constructor',
            bucket_name=bucket_name,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=cdk.RemovalPolicy.DESTROY
        )
