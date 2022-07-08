import aws_cdk as cdk
from aws_cdk import (
    aws_lambda as lambda_,
    aws_iam as iam,
    aws_s3 as s3
)
from constructs import Construct


class LambdaConstruct(Construct):
    def __init__(self, scope: Construct, id: str, bucket: s3.Bucket, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.bucket = bucket

    def python_lambda_generator(self):

        func = lambda_.Function(
            self,
            'fred-extract-function',
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset("./lambda_"),
            handler='index.handler',
            role=self.python_lambda_role()
        )
        return func

    def python_lambda_role(self):

        lambda_role = iam.Role(
            self,
            'fred-lambda-role',
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSLambdaBasicExecutionRole')
            ]
        )

        policy = iam.Policy(
            self,
            'lambda-writer-policy',
            statements=[
                iam.PolicyStatement(
                    actions=[
                        's3:put*',
                        's3:get*'
                    ],
                    effect=iam.Effect.ALLOW,
                    resources=[
                        f'arn:aws:s3:::{self.bucket.bucket_name}/*',
                        f'arn:aws:s3:::{self.bucket.bucket_name}'
                    ]
                )
            ]
        )

        lambda_role.attach_inline_policy(policy)

        return lambda_role
