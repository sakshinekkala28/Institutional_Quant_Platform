###############################################################################
# Institutional Quant Platform
# Main Infrastructure Orchestration
###############################################################################

###############################################################################
# Local Data
###############################################################################

data "aws_availability_zones" "available" {

  state = "available"

}

###############################################################################
# Networking
###############################################################################

module "networking" {

  source = "./modules/networking"

  project_name = var.project_name

  environment = var.environment

  aws_region = var.aws_region

  vpc_cidr = var.vpc_cidr

  availability_zones = var.availability_zones

  public_subnets = var.public_subnets

  private_subnets = var.private_subnets

  tags = local.common_tags

}

###############################################################################
# Security
###############################################################################

module "security" {

  source = "./modules/security"

  project_name = var.project_name

  environment = var.environment

  cluster_name = var.cluster_name

  tags = local.common_tags

}

###############################################################################
# Storage
###############################################################################

module "storage" {

  source = "./modules/storage"

  project_name = var.project_name

  environment = var.environment

  kms_key_arn = module.security.kms_key_arn

  tags = local.common_tags

}

###############################################################################
# Kubernetes
###############################################################################

module "kubernetes" {

  source = "./modules/kubernetes"

  cluster_name = var.cluster_name

  cluster_version = var.cluster_version

  aws_region = var.aws_region

  vpc_id = module.networking.vpc_id

  private_subnets = module.networking.private_subnet_ids

  public_subnets = module.networking.public_subnet_ids

  node_instance_types = var.node_instance_types

  desired_capacity = var.desired_capacity

  min_capacity = var.min_capacity

  max_capacity = var.max_capacity

  disk_size = var.disk_size

  kms_key_arn = module.security.kms_key_arn

  log_retention_days = var.log_retention_days

  endpoint_public_access = var.endpoint_public_access

  tags = local.common_tags

  depends_on = [

    module.networking,

    module.security

  ]

}

###############################################################################
# Monitoring
###############################################################################

module "monitoring" {

  source = "./modules/monitoring"

  cluster_name = module.kubernetes.cluster_name

  aws_region = var.aws_region

  kms_key_arn = module.security.kms_key_arn

  tags = local.common_tags

  depends_on = [

    module.kubernetes

  ]

}

###############################################################################
# Helm Deployment
###############################################################################

resource "helm_release" "institutional_quant" {

  name = "institutional-quant"

  chart = "${path.module}/../helm"

  namespace = "institutional-quant"

  create_namespace = true

  dependency_update = true

  wait = true

  timeout = 900

  values = [

    file("${path.module}/../helm/values.yaml")

  ]

  depends_on = [

    module.kubernetes

  ]

}

###############################################################################
# Deployment Summary
###############################################################################

resource "local_file" "deployment_summary" {

  filename = "${path.module}/deployment-summary.txt"

  content = <<EOF

======================================================
Institutional Quant Platform
======================================================

Environment : ${var.environment}

Region      : ${var.aws_region}

Cluster     : ${module.kubernetes.cluster_name}

Namespace   : institutional-quant

Helm Release: institutional-quant

Dashboard:

https://quant.example.com

======================================================

EOF

}