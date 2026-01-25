from aws_cdk import BundlingOptions, DockerImage, Duration
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_s3 as s3
from constructs import Construct


class LambdaConstruct(Construct):
    def __init__(self, scope: Construct, id: str, bucket: s3.Bucket, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.bucket = bucket

    def python_lambda_generator(self):
        func = lambda_.Function(
            self,
            "fred-extract-function",
            function_name="fred-extractor",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset("./lambda_"),
            handler="index.handler",
            role=self.python_lambda_role(),
            layers=[self.python_lambda_layer()],
            environment={"FRED_BUCKET_NAME": self.bucket.bucket_name},
            timeout=Duration.seconds(45),
        )
        return func

    def python_lambda_role(self):
        lambda_role = iam.Role(
            self,
            "fred-lambda-role",
            role_name="fred-extractor-execution-role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ],
        )

        policy = iam.Policy(
            self,
            "lambda-writer-policy",
            policy_name="fred-extractor-execution-policy",
            statements=[
                iam.PolicyStatement(
                    actions=["s3:put*", "s3:get*"],
                    effect=iam.Effect.ALLOW,
                    resources=[f"arn:aws:s3:::{self.bucket.bucket_name}/*", f"arn:aws:s3:::{self.bucket.bucket_name}"],
                ),
                iam.PolicyStatement(
                    actions=["secretsmanager:GetSecretValue"],
                    effect=iam.Effect.ALLOW,
                    resources=["arn:aws:secretsmanager:us-east-1:429414942599:secret:dev/FredExtractor/APIKey-ujB357"],
                ),
            ],
        )
        lambda_role.attach_inline_policy(policy)
        return lambda_role

    def python_lambda_layer(self):
        lambda_layer = lambda_.LayerVersion(
            self,
            "requests-layer",
            code=lambda_.Code.from_asset(
                "./lambda_",
                bundling=BundlingOptions(
                    image=DockerImage("public.ecr.aws/sam/build-python3.9:latest"),
                    command=["pip", "install", "--target", "/asset-output/python", "-r", "requirements.txt"],
                    user="root",
                    working_directory="/asset-input",
                ),
            ),
            compatible_architectures=[lambda_.Architecture.X86_64],
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_9],
        )
        return lambda_layer
