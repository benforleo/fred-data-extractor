import aws_cdk as cdk
from aws_cdk import (
    aws_lambda as lambda_,
    aws_iam as iam
)
from constructs import Construct


class LambdaConstruct(Construct):
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

    def python_lambda_generator(self, bucket_name, aws_account_id):

        func = lambda_.Function(
            self,
            'fred-extract-function',
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset('../lambda'),
            handler='index.handler'
        )
        return func

    def python_lambda_role(self, bucket_name, aws_account_id):

        policy = iam.Policy(

        )

        lambda_role = iam.Role(
            self,
            'fred-lambda-role',
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole')
            ]
        )
        return lambda_role
