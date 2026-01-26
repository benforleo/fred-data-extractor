from aws_cdk import BundlingOptions, DockerImage, Duration
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_s3 as s3
from constructs import Construct


class LambdaConstruct(Construct):
    """Construct for creating FRED data extractor Lambda function and dependencies."""

    PYTHON_RUNTIME = lambda_.Runtime.PYTHON_3_14
    FUNCTION_TIMEOUT = Duration.seconds(45)
    FUNCTION_MEMORY_SIZE = 256
    LAMBDA_FUNCTION_NAME = "fred-extractor"
    LAMBDA_ROLE_NAME = "fred-extractor-execution-role"
    LAYER_NAME = "fred-dependencies-layer"

    def __init__(self, scope: Construct, id: str, bucket: s3.Bucket, account_id: str, region: str = "us-east-1"):
        super().__init__(scope, id)
        self.bucket = bucket
        self.account_id = account_id
        self.region = region

    def python_lambda_generator(self):
        """Creates the main Lambda function with proper configuration and dependencies."""
        func = lambda_.Function(
            self,
            "fred-extract-function",
            function_name=self.LAMBDA_FUNCTION_NAME,
            runtime=self.PYTHON_RUNTIME,
            code=lambda_.Code.from_asset("./src"),
            handler="index.handler",
            role=self.python_lambda_role(),
            layers=[self.python_lambda_layer()],
            environment={
                "FRED_BUCKET_NAME": self.bucket.bucket_name,
            },
            timeout=self.FUNCTION_TIMEOUT,
            memory_size=self.FUNCTION_MEMORY_SIZE,
            retry_attempts=2,
            description="Extracts data from FRED API and stores in S3",
        )
        return func

    def python_lambda_role(self):
        """Creates IAM role with least-privilege permissions for Lambda execution."""
        lambda_role = iam.Role(
            self,
            "fred-lambda-role",
            role_name=self.LAMBDA_ROLE_NAME,
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ],
            description="Execution role for FRED data extractor Lambda",
        )

        s3_policy = iam.PolicyStatement(
            actions=["s3:PutObject", "s3:GetObject"],
            effect=iam.Effect.ALLOW,
            resources=[
                self.bucket.bucket_arn,
                self.bucket.arn_for_objects("*"),
            ],
        )

        secrets_policy = iam.PolicyStatement(
            actions=["secretsmanager:GetSecretValue"],
            effect=iam.Effect.ALLOW,
            resources=[f"arn:aws:secretsmanager:{self.region}:{self.account_id}:secret:dev/FredExtractor/APIKey-*"],
        )

        policy = iam.Policy(
            self,
            "lambda-writer-policy",
            policy_name="fred-extractor-execution-policy",
            statements=[s3_policy, secrets_policy],
        )
        lambda_role.attach_inline_policy(policy)
        return lambda_role

    def python_lambda_layer(self):
        """Creates Lambda layer with Python dependencies from requirements.txt."""
        lambda_layer = lambda_.LayerVersion(
            self,
            "requests-layer",
            layer_version_name=self.LAYER_NAME,
            code=lambda_.Code.from_asset(
                "./src",
                bundling=BundlingOptions(
                    image=self._get_build_image(),
                    command=[
                        "bash",
                        "-c",
                        "pip install --target /asset-output/python -r requirements.txt --upgrade --no-cache-dir",
                    ],
                    user="root",
                    working_directory="/asset-input",
                ),
            ),
            compatible_architectures=[lambda_.Architecture.X86_64],
            compatible_runtimes=[self.PYTHON_RUNTIME],
            description="Python dependencies for FRED data extractor (requests, etc.)",
        )
        return lambda_layer

    def _get_build_image(self) -> DockerImage:
        """Returns the appropriate SAM build image based on the Python runtime version."""
        runtime_version = self.PYTHON_RUNTIME.name.lower().replace("_", "")
        return DockerImage(f"public.ecr.aws/sam/build-{runtime_version}:latest")
