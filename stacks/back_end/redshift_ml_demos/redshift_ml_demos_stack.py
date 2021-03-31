from aws_cdk import aws_redshift as _redshift
from aws_cdk import aws_secretsmanager as _sm
from aws_cdk import aws_iam as _iam
from aws_cdk import aws_ec2 as _ec2
from aws_cdk import core as cdk
from stacks.miztiik_global_args import GlobalArgs


class RedshiftMlDemosStack(cdk.Stack):

    def __init__(
        self,
        scope: cdk.Construct,
        construct_id: str,
        vpc,
        ec2_instance_type: str,
        data_src_bkt_name: str,
        stack_log_level: str,
        **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create Cluster Password
        churn_prediction_cluster_secret = _sm.Secret(
            self,
            "setRedshiftDemoClusterSecret",
            description="Redshift Demo Cluster Secret",
            generate_secret_string=_sm.SecretStringGenerator(
                exclude_punctuation=True
            ),
            secret_name="RedshiftDemoClusterSecret",
            removal_policy=cdk.RemovalPolicy.DESTROY
        )

        # Redshift IAM Role
        # https://docs.aws.amazon.com/redshift/latest/dg/cluster-setup.html
        _rs_cluster_role = _iam.Role(
            self, "redshiftClusterRole",
            assumed_by=_iam.CompositePrincipal(
                _iam.ServicePrincipal("redshift.amazonaws.com"),
                _iam.ServicePrincipal("sagemaker.amazonaws.com")
            ),
            managed_policies=[
                _iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonS3ReadOnlyAccess"
                )
            ]
        )
        _rs_cluster_role.add_to_policy(
            _iam.PolicyStatement(
                actions=[
                    "cloudwatch:PutMetricData",
                    "ecr:BatchCheckLayerAvailability",
                    "ecr:BatchGetImage",
                    "ecr:GetAuthorizationToken",
                    "ecr:GetDownloadUrlForLayer",
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:DescribeLogStreams",
                    "logs:PutLogEvents",
                    "sagemaker:*Job*"
                ],
                resources=["*"]
            )
        )

        _rs_cluster_role.add_to_policy(_iam.PolicyStatement(
            actions=[
                "iam:PassRole",
                "s3:AbortMultipartUpload",
                "s3:GetObject",
                "s3:DeleteObject",
                "s3:PutObject"
            ],
            resources=[
                f"arn:aws:iam::{cdk.Aws.ACCOUNT_ID}:role/{_rs_cluster_role.role_name}",
                f"arn:aws:s3:::{data_src_bkt_name}/*",
                f"arn:aws:s3:::raw-data-bkt-010/*",
                "arn:aws:s3:::redshift-downloads/*"
            ]
        )
        )

        _rs_cluster_role.add_to_policy(_iam.PolicyStatement(
            actions=[
                "s3:GetBucketLocation",
                "s3:ListBucket"
            ],
            resources=[
                f"arn:aws:iam::{cdk.Aws.ACCOUNT_ID}:role/{_rs_cluster_role.role_name}",
                f"arn:aws:s3:::{data_src_bkt_name}/*",
                f"arn:aws:s3:::raw-data-bkt-010/*",
                "arn:aws:s3:::redshift-downloads/*"
            ]
        )
        )

        # Allow permissions to use GUI Query Editor
        # https://docs.aws.amazon.com/redshift/latest/mgmt/generating-iam-credentials-role-permissions.html

        _rs_cluster_role.add_to_policy(_iam.PolicyStatement(
            actions=[
                "iam:PassRole",
                "redshift:GetClusterCredentials"
            ],
            resources=[
                f"arn:aws:redshift:{cdk.Aws.REGION}:{cdk.Aws.ACCOUNT_ID}:dbuser:*/ml_*",
            ]
        )
        )

        # Subnet Group for Cluster
        demo_cluster_subnet_group = _redshift.CfnClusterSubnetGroup(
            self,
            "redshiftDemoClusterSubnetGroup",
            subnet_ids=vpc.get_vpc_public_subnet_ids,
            description="Redshift Demo Cluster Subnet Group"
        )

        # Create Security Group for QuickSight
        quicksight_to_redshift_sg = _ec2.SecurityGroup(
            self,
            id="redshiftSecurityGroup",
            vpc=vpc.get_vpc,
            security_group_name=f"redshift_sg_{id}",
            description="Security Group for Quicksight"
        )

        # https://docs.aws.amazon.com/quicksight/latest/user/regions.html
        quicksight_to_redshift_sg.add_ingress_rule(
            peer=_ec2.Peer.ipv4("52.23.63.224/27"),
            connection=_ec2.Port.tcp(5439),
            description="Allow QuickSight connetions"
        )

        """
        # Create RedShift cluster
        demo_cluster = _redshift.CfnCluster(
            self,
            "redshiftDemoCluster",
            cluster_type="single-node",
            # number_of_nodes=1,
            db_name="churn_prediction_cluster",
            master_username="dwh_user",
            master_user_password=churn_prediction_cluster_secret.secret_value.to_string(),
            iam_roles=[_rs_cluster_role.role_arn],
            node_type=f"{ec2_instance_type}",
            cluster_subnet_group_name=demo_cluster_subnet_group.ref,
            vpc_security_group_ids=[
                quicksight_to_redshift_sg.security_group_id]
        )
        """
        ###########################################
        ################# OUTPUTS #################
        ###########################################
        output_0 = cdk.CfnOutput(
            self,
            "AutomationFrom",
            value=f"{GlobalArgs.SOURCE_INFO}",
            description="To know more about this automation stack, check out our github page."
        )

        output_1 = cdk.CfnOutput(
            self,
            "RedshiftIAMRole",
            value=(
                f"{_rs_cluster_role.role_arn}"
            ),
            description=f"Redshift Cluster IAM Role Arn"
        )

        output_2 = cdk.CfnOutput(
            self,
            "RedshiftClusterPassword",
            value=(
                f"https://console.aws.amazon.com/secretsmanager/home?region="
                f"{cdk.Aws.REGION}"
                f"#/secret?name="
                f"{churn_prediction_cluster_secret.secret_arn}"
            ),
            description=f"Redshift Cluster Password in Secrets Manager"
        )

        """
        output_3 = cdk.CfnOutput(
            self,
            "RedshiftCluster",
            value=f"{demo_cluster.attr_endpoint_address}",
            description=f"RedshiftCluster Endpoint"
        )
        """
