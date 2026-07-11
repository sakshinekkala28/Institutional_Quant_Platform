###############################################################################
# Institutional Quant Platform
# Terraform Variables
###############################################################################

###############################################################################
# General
###############################################################################

variable "project_name" {

  description = "Project name"

  type = string

  default = "institutional-quant"

}

variable "environment" {

  description = "Deployment environment"

  type = string

  default = "production"

}

variable "aws_region" {

  description = "AWS Region"

  type = string

  default = "ap-south-1"

}

###############################################################################
# Networking
###############################################################################

variable "vpc_name" {

  description = "VPC Name"

  type = string

  default = "institutional-quant-vpc"

}

variable "vpc_cidr" {

  description = "VPC CIDR"

  type = string

  default = "10.0.0.0/16"

}

variable "availability_zones" {

  description = "Availability Zones"

  type = list(string)

  default = [

    "ap-south-1a",

    "ap-south-1b",

    "ap-south-1c"

  ]

}

variable "private_subnets" {

  description = "Private subnet CIDRs"

  type = list(string)

  default = [

    "10.0.1.0/24",

    "10.0.2.0/24",

    "10.0.3.0/24"

  ]

}

variable "public_subnets" {

  description = "Public subnet CIDRs"

  type = list(string)

  default = [

    "10.0.101.0/24",

    "10.0.102.0/24",

    "10.0.103.0/24"

  ]

}

###############################################################################
# EKS
###############################################################################

variable "cluster_name" {

  description = "EKS Cluster Name"

  type = string

  default = "institutional-quant"

}

variable "cluster_version" {

  description = "Kubernetes Version"

  type = string

  default = "1.30"

}

variable "endpoint_public_access" {

  description = "Enable public API endpoint"

  type = bool

  default = true

}

###############################################################################
# Node Group
###############################################################################

variable "node_instance_types" {

  description = "Worker Node Instance Types"

  type = list(string)

  default = [

    "m6i.large"

  ]

}

variable "desired_capacity" {

  description = "Desired node count"

  type = number

  default = 3

}

variable "min_capacity" {

  description = "Minimum node count"

  type = number

  default = 3

}

variable "max_capacity" {

  description = "Maximum node count"

  type = number

  default = 10

}

variable "disk_size" {

  description = "Node root disk size"

  type = number

  default = 100

}

###############################################################################
# Storage
###############################################################################

variable "storage_class" {

  description = "Default StorageClass"

  type = string

  default = "gp3"

}

###############################################################################
# Monitoring
###############################################################################

variable "enable_prometheus" {

  description = "Deploy Prometheus"

  type = bool

  default = true

}

variable "enable_grafana" {

  description = "Deploy Grafana"

  type = bool

  default = true

}

###############################################################################
# Logging
###############################################################################

variable "log_retention_days" {

  description = "CloudWatch Log Retention"

  type = number

  default = 30

}

###############################################################################
# Security
###############################################################################

variable "enable_irsa" {

  description = "Enable IAM Roles for Service Accounts"

  type = bool

  default = true

}

variable "kms_key_rotation" {

  description = "Enable KMS Key Rotation"

  type = bool

  default = true

}

###############################################################################
# Tags
###############################################################################

variable "additional_tags" {

  description = "Additional resource tags"

  type = map(string)

  default = {}

}