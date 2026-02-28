from aws_cdk import Duration
from aws_cdk import aws_stepfunctions as sfn
from aws_cdk import aws_stepfunctions_tasks as sfn_tasks
from aws_cdk.aws_events import Rule, Schedule
from aws_cdk.aws_events_targets import SfnStateMachine
from constructs import Construct


class FredSchedulerConstruct(Construct):
    def __init__(self, scope: Construct, id: str, lambda_function, **kwargs):
        super().__init__(scope, id)
        self.lambda_function = lambda_function

    def workflow(self):
        lambda_invoke = sfn_tasks.LambdaInvoke(self, "sfn-lambda-invocation", lambda_function=self.lambda_function)

        lambda_invoke.add_retry(
            errors=["Timeout", "ConnectTimeout", "ReadTimeout"],
            interval=Duration.seconds(5),
            max_attempts=3,
            backoff_rate=2.0,
        )

        state_machine = sfn.StateMachine(
            self,
            "state-machine",
            state_machine_name="fred-state-machine",
            definition_body=sfn.DefinitionBody.from_chainable(lambda_invoke),
        )
        return state_machine

    def apply_schedule(self, cron_expression: str) -> None:
        Rule(
            self,
            "fred-scheduler",
            schedule=Schedule.expression(cron_expression),
            targets=[SfnStateMachine(self.workflow())],
        )
