from aws_cdk.aws_events import Rule, Schedule
from aws_cdk.aws_events_targets import LambdaFunction
from constructs import Construct


class FredSchedulerConstruct(Construct):
    def __init__(self, scope: Construct, id: str, lambda_function, **kwargs):
        super().__init__(scope, id)
        self.lambda_function = lambda_function

    def apply_schedule(self, cron_expression: str) -> None:
        Rule(
            self,
            'fred-scheduler',
            schedule=Schedule.expression(cron_expression),
            targets=[
                LambdaFunction(
                    self.lambda_function
                )
            ]
        )

