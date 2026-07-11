###############################################################################
# Institutional Quant Platform
# Security
###############################################################################

###############################################################################
# KMS Key
###############################################################################

resource "aws_kms_key" "platform" {

  description             = "Institutional Quant Platform KMS Key"

  enable_key_rotation     = true

  deletion_window_in_days = 30

  tags = merge(

    local.common_tags,

    {

      Name = "${local.name_prefix}-kms"

    }

  )

}

resource "aws_kms_alias" "platform" {

  name = "alias/${local.name_prefix}"

  target_key_id = aws_kms_key.platform.key_id

}

###############################################################################
# Secrets Manager
###############################################################################

resource "aws_secretsmanager_secret" "platform" {

  name = "${local.name_prefix}-application"

  kms_key_id = aws_kms_key.platform.arn

  recovery_window_in_days = 30

  tags = local.common_tags

}

resource "aws_secretsmanager_secret_version" "platform" {

  secret_id = aws_secretsmanager_secret.platform.id

  secret_string = jsonencode({

    database = {

      host = "postgres"

      port = 5432

      username = "CHANGE_ME"

      password = "CHANGE_ME"

    }

    redis = {

      password = "CHANGE_ME"

    }

    jwt = {

      secret = "CHANGE_ME"

    }

  })

}

###############################################################################
# CloudTrail
###############################################################################

resource "aws_s3_bucket" "cloudtrail" {

  bucket = "${local.name_prefix}-cloudtrail"

  tags = local.common_tags

}

resource "aws_cloudtrail" "platform" {

  name = "${local.name_prefix}-trail"

  s3_bucket_name = aws_s3_bucket.cloudtrail.id

  include_global_service_events = true

  is_multi_region_trail = true

  enable_logging = true

  kms_key_id = aws_kms_key.platform.arn

  tags = local.common_tags

}

###############################################################################
# GuardDuty
###############################################################################

resource "aws_guardduty_detector" "platform" {

  enable = true

  tags = local.common_tags

}

###############################################################################
# Security Hub
###############################################################################

resource "aws_securityhub_account" "platform" {}

###############################################################################
# AWS Config
###############################################################################

resource "aws_s3_bucket" "config" {

  bucket = "${local.name_prefix}-config"

  tags = local.common_tags

}

resource "aws_iam_role" "config" {

  name = "${local.name_prefix}-config"

  assume_role_policy = jsonencode({

    Version = "2012-10-17"

    Statement = [

      {

        Effect = "Allow"

        Principal = {

          Service = "config.amazonaws.com"

        }

        Action = "sts:AssumeRole"

      }

    ]

  })

  tags = local.common_tags

}

resource "aws_iam_role_policy_attachment" "config" {

  role = aws_iam_role.config.name

  policy_arn = "arn:aws:iam::aws:policy/service-role/AWS_ConfigRole"

}

resource "aws_config_configuration_recorder" "platform" {

  name = "${local.name_prefix}-recorder"

  role_arn = aws_iam_role.config.arn

  recording_group {

    all_supported = true

    include_global_resource_types = true

  }

}

resource "aws_config_delivery_channel" "platform" {

  name = "${local.name_prefix}-delivery"

  s3_bucket_name = aws_s3_bucket.config.bucket

  depends_on = [

    aws_config_configuration_recorder.platform

  ]

}

###############################################################################
# IAM Password Policy
###############################################################################

resource "aws_iam_account_password_policy" "platform" {

  minimum_password_length = 16

  require_lowercase_characters = true

  require_uppercase_characters = true

  require_numbers = true

  require_symbols = true

  allow_users_to_change_password = true

  max_password_age = 90

  password_reuse_prevention = 24

  hard_expiry = false

}

###############################################################################
# SNS Security Alerts
###############################################################################

resource "aws_sns_topic" "security" {

  name = "${local.name_prefix}-security"

  kms_master_key_id = aws_kms_key.platform.arn

  tags = local.common_tags

}

###############################################################################
# CloudWatch Log Group
###############################################################################

resource "aws_cloudwatch_log_group" "security" {

  name = "/institutional-quant/security"

  retention_in_days = 365

  kms_key_id = aws_kms_key.platform.arn

  tags = local.common_tags

}

###############################################################################
# Security Outputs
###############################################################################

output "kms_key_arn" {

  value = aws_kms_key.platform.arn

}

output "secret_arn" {

  value = aws_secretsmanager_secret.platform.arn

}

output "security_topic" {

  value = aws_sns_topic.security.arn

}