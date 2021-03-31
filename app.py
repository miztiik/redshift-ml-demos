#!/usr/bin/env python3

from stacks.back_end.vpc_stack import VpcStack
from stacks.back_end.redshift_ml_demos.redshift_ml_demos_stack import RedshiftMlDemosStack
from stacks.back_end.s3_stack.s3_stack import S3Stack
from aws_cdk import core as cdk


app = cdk.App()


# VPC Stack for hosting Secure workloads & Other resources
vpc_stack = VpcStack(
    app,
    f"{app.node.try_get_context('project')}-vpc-stack",
    stack_log_level="INFO",
    description="Miztiik Automation: Custom Multi-AZ VPC"
)


# S3 Bucket to hold our datasources
data_src_bkt_stack = S3Stack(
    app,
    f"{app.node.try_get_context('project')}-data-src-bkt-stack",
    stack_log_level="INFO",
    description="Miztiik Automation: S3 Bucket to hold our datasources"
)


# Deploy Redshift cluster and load data
redshift_demo = RedshiftMlDemosStack(
    app,
    f"{app.node.try_get_context('project')}-stack",
    vpc=vpc_stack,
    ec2_instance_type="dc2.large",
    data_src_bkt_name=data_src_bkt_stack.data_bkt.bucket_name,
    stack_log_level="INFO",
    description="Miztiik Automation: Deploy Redshift cluster and load data"
)


# Stack Level Tagging
_tags_lst = app.node.try_get_context("tags")

if _tags_lst:
    for _t in _tags_lst:
        for k, v in _t.items():
            cdk.Tags.of(app).add(k, v, apply_to_launched_instances=True)

app.synth()
