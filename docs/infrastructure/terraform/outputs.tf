###############################################################################
# Institutional Quant Platform
# Terraform Outputs
###############################################################################

###############################################################################
# General
###############################################################################

output "project_name" {

  description = "Project Name"

  value = var.project_name

}

output "environment" {

  description = "Deployment Environment"

  value = var.environment

}

output "aws_region" {

  description = "AWS Region"

  value = var.aws_region

}

###############################################################################
# Networking
###############################################################################

output "vpc_id" {

  description = "VPC ID"

  value = aws_vpc.this.id

}

output "vpc_cidr" {

  description = "VPC CIDR"

  value = aws_vpc.this.cidr_block

}

output "public_subnets" {

  description = "Public Subnet IDs"

  value = aws_subnet.public[*].id

}

output "private_subnets" {

  description = "Private Subnet IDs"

  value = aws_subnet.private[*].id

}

output "internet_gateway" {

  description = "Internet Gateway"

  value = aws_internet_gateway.this.id

}

output "nat_gateway" {

  description = "NAT Gateway"

  value = aws_nat_gateway.this.id

}

###############################################################################
# Security
###############################################################################

output "platform_security_group" {

  description = "Platform Security Group"

  value = aws_security_group.platform.id

}

output "eks_cluster_security_group" {

  description = "EKS Cluster Security Group"

  value = aws_security_group.eks_cluster.id

}

output "eks_worker_security_group" {

  description = "EKS Worker Security Group"

  value = aws_security_group.eks_nodes.id

}

###############################################################################
# Kubernetes
###############################################################################

output "cluster_name" {

  description = "EKS Cluster Name"

  value = aws_eks_cluster.this.name

}

output "cluster_version" {

  description = "Kubernetes Version"

  value = aws_eks_cluster.this.version

}

output "cluster_endpoint" {

  description = "Cluster Endpoint"

  value = aws_eks_cluster.this.endpoint

}

output "cluster_certificate_authority" {

  description = "Cluster Certificate"

  value = aws_eks_cluster.this.certificate_authority[0].data

  sensitive = true

}

output "cluster_oidc_provider" {

  description = "OIDC Provider"

  value = aws_iam_openid_connect_provider.eks.arn

}

output "node_group" {

  description = "Managed Node Group"

  value = aws_eks_node_group.default.node_group_name

}

###############################################################################
# IAM
###############################################################################

output "cluster_role_arn" {

  description = "EKS Cluster Role"

  value = aws_iam_role.eks_cluster.arn

}

output "worker_role_arn" {

  description = "Worker Node Role"

  value = aws_iam_role.eks_nodes.arn

}

output "irsa_role_arn" {

  description = "IRSA Role"

  value = aws_iam_role.irsa.arn

}

###############################################################################
# Encryption
###############################################################################

output "kms_key_arn" {

  description = "Platform KMS Key"

  value = aws_kms_key.platform.arn

}

###############################################################################
# Secrets
###############################################################################

output "platform_secret_arn" {

  description = "Secrets Manager Secret"

  value = aws_secretsmanager_secret.platform.arn

}

###############################################################################
# Storage
###############################################################################

output "market_data_bucket" {

  description = "Market Data Bucket"

  value = aws_s3_bucket.market_data.bucket

}

output "analytics_bucket" {

  description = "Analytics Bucket"

  value = aws_s3_bucket.analytics.bucket

}

output "reports_bucket" {

  description = "Reports Bucket"

  value = aws_s3_bucket.reports.bucket

}

output "backups_bucket" {

  description = "Backups Bucket"

  value = aws_s3_bucket.backups.bucket

}

###############################################################################
# Monitoring
###############################################################################

output "cloudwatch_dashboard" {

  description = "CloudWatch Dashboard"

  value = aws_cloudwatch_dashboard.platform.dashboard_name

}

output "alert_topic" {

  description = "SNS Alert Topic"

  value = aws_sns_topic.alerts.arn

}

###############################################################################
# Helm
###############################################################################

output "helm_release" {

  description = "Helm Release"

  value = helm_release.institutional_quant.name

}

###############################################################################
# Kubectl
###############################################################################

output "kubectl_configuration" {

  description = "Command to configure kubectl"

  value = "aws eks update-kubeconfig --region ${var.aws_region} --name ${aws_eks_cluster.this.name}"

}

###############################################################################
# Summary
###############################################################################

output "deployment_summary" {

  description = "Deployment Summary"

  value = {

    project     = var.project_name

    environment = var.environment

    region      = var.aws_region

    cluster     = aws_eks_cluster.this.name

    namespace   = "institutional-quant"

    helm        = helm_release.institutional_quant.name

  }

}