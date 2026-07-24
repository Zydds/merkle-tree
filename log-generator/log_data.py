EVENT_NAMES = [
    "ConsoleLogin", "AssumeRole", "GetObject", "PutObject", "DeleteObject",
    "DescribeInstances", "StartInstances", "StopInstances", "TerminateInstances",
    "CreateBucket", "DeleteBucket", "ListBuckets",
    "CreateUser", "DeleteUser", "AttachUserPolicy", "DetachUserPolicy",
    "AuthorizeSecurityGroupIngress", "RevokeSecurityGroupIngress",
    "CreateKeyPair", "DeleteKeyPair",
    "GetSecretValue", "PutSecretValue",
    "InvokeFunction", "UpdateFunctionCode",
    "RunInstances", "ModifyInstanceAttribute",
]

EVENT_SOURCES = [
    "ec2.amazonaws.com", "s3.amazonaws.com", "iam.amazonaws.com",
    "sts.amazonaws.com", "lambda.amazonaws.com", "secretsmanager.amazonaws.com",
    "cloudtrail.amazonaws.com", "rds.amazonaws.com",
]

AWS_REGIONS = [
    "us-east-1", "us-west-2", "ap-southeast-1",
    "ap-northeast-1", "eu-west-1", "eu-central-1",
]

USER_AGENTS = [
    "aws-cli/2.13.0",
    "console.amazonaws.com",
    "cloudformation.amazonaws.com",
    "Boto3/1.28.0 Python/3.11.0",
    "aws-sdk-java/1.12.0",
]

ERROR_CODES = [
    None, None, None,
    "AccessDenied", "UnauthorizedOperation",
    "InvalidParameterValue", "NoSuchBucket", "NoSuchKey",
]

USER_TYPES = ["IAMUser", "AssumedRole", "Root", "FederatedUser"]
