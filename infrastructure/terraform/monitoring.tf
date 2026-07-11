###############################################################################
# Institutional Quant Platform
# Monitoring
###############################################################################

###############################################################################
# SNS Topic for Alerts
###############################################################################

resource "aws_sns_topic" "alerts" {

  name = "${local.name_prefix}-alerts"

  kms_master_key_id = aws_kms_key.platform.arn

  tags = local.common_tags

}

###############################################################################
# CloudWatch Dashboard
###############################################################################

resource "aws_cloudwatch_dashboard" "platform" {

  dashboard_name = "${local.name_prefix}-dashboard"

  dashboard_body = jsonencode({

    widgets = [

      {

        type = "metric"

        x = 0

        y = 0

        width = 12

        height = 6

        properties = {

          title = "EKS CPU Utilization"

          region = var.aws_region

          metrics = [

            [

              "AWS/EKS",

              "cluster_failed_request_count",

              "ClusterName",

              var.cluster_name

            ]

          ]

        }

      },

      {

        type = "metric"

        x = 12

        y = 0

        width = 12

        height = 6

        properties = {

          title = "Node CPU"

          region = var.aws_region

          metrics = [

            [

              "CWAgent",

              "CPUUtilization"

            ]

          ]

        }

      }

    ]

  })

}

###############################################################################
# CPU Alarm
###############################################################################

resource "aws_cloudwatch_metric_alarm" "high_cpu" {

  alarm_name = "${local.name_prefix}-high-cpu"

  comparison_operator = "GreaterThanThreshold"

  evaluation_periods = 2

  metric_name = "CPUUtilization"

  namespace = "AWS/EC2"

  period = 300

  statistic = "Average"

  threshold = 80

  alarm_description = "Average CPU exceeds 80%"

  alarm_actions = [

    aws_sns_topic.alerts.arn

  ]

}

###############################################################################
# Memory Alarm
###############################################################################

resource "aws_cloudwatch_metric_alarm" "high_memory" {

  alarm_name = "${local.name_prefix}-high-memory"

  comparison_operator = "GreaterThanThreshold"

  evaluation_periods = 2

  metric_name = "mem_used_percent"

  namespace = "CWAgent"

  period = 300

  statistic = "Average"

  threshold = 85

  alarm_actions = [

    aws_sns_topic.alerts.arn

  ]

}

###############################################################################
# Disk Alarm
###############################################################################

resource "aws_cloudwatch_metric_alarm" "disk" {

  alarm_name = "${local.name_prefix}-disk"

  comparison_operator = "GreaterThanThreshold"

  evaluation_periods = 2

  metric_name = "disk_used_percent"

  namespace = "CWAgent"

  period = 300

  statistic = "Average"

  threshold = 85

  alarm_actions = [

    aws_sns_topic.alerts.arn

  ]

}

###############################################################################
# API Errors
###############################################################################

resource "aws_cloudwatch_log_metric_filter" "api_errors" {

  name = "api-errors"

  log_group_name = aws_cloudwatch_log_group.security.name

  pattern = "ERROR"

  metric_transformation {

    name = "ApiErrors"

    namespace = "InstitutionalQuant"

    value = "1"

  }

}

###############################################################################
# Alarm on API Errors
###############################################################################

resource "aws_cloudwatch_metric_alarm" "api_errors" {

  alarm_name = "${local.name_prefix}-api-errors"

  comparison_operator = "GreaterThanThreshold"

  evaluation_periods = 1

  metric_name = "ApiErrors"

  namespace = "InstitutionalQuant"

  period = 300

  statistic = "Sum"

  threshold = 10

  alarm_actions = [

    aws_sns_topic.alerts.arn

  ]

}

###############################################################################
# Container Insights
###############################################################################

resource "aws_cloudwatch_log_group" "container_insights" {

  name = "/aws/containerinsights/${var.cluster_name}/performance"

  retention_in_days = 30

  tags = local.common_tags

}

###############################################################################
# Outputs
###############################################################################

output "monitoring_dashboard" {

  value = aws_cloudwatch_dashboard.platform.dashboard_name

}

output "alert_topic" {

  value = aws_sns_topic.alerts.arn

}