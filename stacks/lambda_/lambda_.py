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
            code=lambda_.Code.from_asset("./lambda_"),
            handler='index.handler',
            role=self.python_lambda_role(bucket_name, aws_account_id)
        )
        return func

    def python_lambda_role(self, bucket_name, aws_account_id):

        lambda_role = iam.Role(
            self,
            'fred-lambda_-role',
            assumed_by=iam.ServicePrincipal('lambda_.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole')
            ]
        )

        policy = iam.Policy(
            self,
            'lambda_-writer-policy',
            statements=[
                iam.PolicyStatement(
                    actions=[
                        's3:put*',
                        's3:get*'
                    ],
                    effect=iam.Effect.ALLOW,
                    resources=[
                        f'arn:aws:s3:::{bucket_name}-{aws_account_id}/*',
                        f'arn:aws:s3:::{bucket_name}-{aws_account_id}'
                    ]
                )
            ]
        )

        lambda_role.attach_inline_policy(policy)

        return lambda_role
