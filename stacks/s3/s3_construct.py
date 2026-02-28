import aws_cdk as cdk
from aws_cdk import aws_s3 as s3
from constructs import Construct


class S3Construct(Construct):
    """Construct for creating and configuring S3 buckets with security best practices."""

    VERSIONING_ENABLED = True
    ENCRYPTION_TYPE = s3.BucketEncryption.S3_MANAGED
    LIFECYCLE_TRANSITION_DAYS = 90
    LIFECYCLE_EXPIRATION_DAYS = 365

    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

    def create_bucket(
        self,
        bucket_name: str,
        enable_versioning: bool = True,
        enable_lifecycle_rules: bool = True,
        auto_delete_objects: bool = False,
    ) -> s3.Bucket:
        """
        Creates an S3 bucket with security best practices and optional lifecycle management.

        Args:
            bucket_name: The name of the S3 bucket
            enable_versioning: Enable versioning for the bucket (default: True)
            enable_lifecycle_rules: Enable lifecycle rules for cost optimization (default: True)
            auto_delete_objects: Automatically delete objects when stack is destroyed (default: False)

        Returns:
            s3.Bucket: The created S3 bucket
        """
        bucket = s3.Bucket(
            self,
            "s3-bucket-constructor",
            bucket_name=bucket_name,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=self.ENCRYPTION_TYPE,
            enforce_ssl=True,
            versioned=enable_versioning,
            lifecycle_rules=self._get_lifecycle_rules() if enable_lifecycle_rules else None,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            auto_delete_objects=auto_delete_objects,
            object_ownership=s3.ObjectOwnership.BUCKET_OWNER_ENFORCED,
            event_bridge_enabled=False,
        )

        cdk.Tags.of(bucket).add("Project", "FRED-Data-Extractor")
        cdk.Tags.of(bucket).add("ManagedBy", "CDK")

        return bucket

    def _get_lifecycle_rules(self) -> list[s3.LifecycleRule]:
        """
        Returns lifecycle rules for cost optimization.
        Transitions objects to cheaper storage classes and expires old data.
        """
        return [
            s3.LifecycleRule(
                id="TransitionToInfrequentAccess",
                enabled=True,
                transitions=[
                    s3.Transition(
                        storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                        transition_after=cdk.Duration.days(self.LIFECYCLE_TRANSITION_DAYS),
                    )
                ],
            ),
            s3.LifecycleRule(
                id="ExpireOldData",
                enabled=True,
                expiration=cdk.Duration.days(self.LIFECYCLE_EXPIRATION_DAYS),
                noncurrent_version_expiration=cdk.Duration.days(30),
            ),
        ]
