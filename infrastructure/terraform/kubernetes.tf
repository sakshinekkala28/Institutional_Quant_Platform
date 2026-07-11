###############################################################################
# Institutional Quant Platform
# Kubernetes (EKS)
# Part 1 - IAM, Security Groups, EKS Cluster
###############################################################################

###############################################################################
# EKS Cluster IAM Role
###############################################################################

data "aws_iam_policy_document" "eks_cluster_assume_role" {

  statement {

    effect = "Allow"

    principals {

      type = "Service"

      identifiers = [

        "eks.amazonaws.com"

      ]

    }

    actions = [

      "sts:AssumeRole"

    ]

  }

}

resource "aws_iam_role" "eks_cluster" {

  name = "${local.name_prefix}-eks-cluster-role"

  assume_role_policy = data.aws_iam_policy_document.eks_cluster_assume_role.json

  tags = local.common_tags

}

resource "aws_iam_role_policy_attachment" "eks_cluster_policy" {

  role = aws_iam_role.eks_cluster.name

  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"

}

###############################################################################
# Worker Node IAM Role
###############################################################################

data "aws_iam_policy_document" "eks_node_assume_role" {

  statement {

    effect = "Allow"

    principals {

      type = "Service"

      identifiers = [

        "ec2.amazonaws.com"

      ]

    }

    actions = [

      "sts:AssumeRole"

    ]

  }

}

resource "aws_iam_role" "eks_nodes" {

  name = "${local.name_prefix}-eks-node-role"

  assume_role_policy = data.aws_iam_policy_document.eks_node_assume_role.json

  tags = local.common_tags

}

resource "aws_iam_role_policy_attachment" "worker_node_policy" {

  role = aws_iam_role.eks_nodes.name

  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"

}

resource "aws_iam_role_policy_attachment" "worker_cni_policy" {

  role = aws_iam_role.eks_nodes.name

  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"

}

resource "aws_iam_role_policy_attachment" "worker_ecr_policy" {

  role = aws_iam_role.eks_nodes.name

  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"

}

###############################################################################
# Cluster Security Group
###############################################################################

resource "aws_security_group" "eks_cluster" {

  name = "${local.name_prefix}-eks-cluster"

  description = "EKS Control Plane Security Group"

  vpc_id = aws_vpc.this.id

  ingress {

    description = "HTTPS"

    protocol = "tcp"

    from_port = 443

    to_port = 443

    cidr_blocks = [

      var.vpc_cidr

    ]

  }

  egress {

    protocol = "-1"

    from_port = 0

    to_port = 0

    cidr_blocks = [

      "0.0.0.0/0"

    ]

  }

  tags = merge(

    local.common_tags,

    {

      Name = "${local.name_prefix}-eks-cluster"

    }

  )

}

###############################################################################
# Worker Node Security Group
###############################################################################

resource "aws_security_group" "eks_nodes" {

  name = "${local.name_prefix}-eks-workers"

  description = "EKS Worker Nodes"

  vpc_id = aws_vpc.this.id

  ingress {

    description = "Node to Node"

    protocol = "-1"

    from_port = 0

    to_port = 0

    self = true

  }

  ingress {

    description = "Cluster API"

    protocol = "tcp"

    from_port = 443

    to_port = 443

    security_groups = [

      aws_security_group.eks_cluster.id

    ]

  }

  egress {

    protocol = "-1"

    from_port = 0

    to_port = 0

    cidr_blocks = [

      "0.0.0.0/0"

    ]

  }

  tags = merge(

    local.common_tags,

    {

      Name = "${local.name_prefix}-eks-workers"

    }

  )

}

###############################################################################
# CloudWatch Log Group
###############################################################################

resource "aws_cloudwatch_log_group" "eks" {

  name = "/aws/eks/${var.cluster_name}/cluster"

  retention_in_days = var.log_retention_days

  tags = local.common_tags

}

###############################################################################
# KMS Key
###############################################################################

resource "aws_kms_key" "eks" {

  description = "EKS Secrets Encryption"

  enable_key_rotation = var.kms_key_rotation

  tags = local.common_tags

}

resource "aws_kms_alias" "eks" {

  name = "alias/${local.name_prefix}-eks"

  target_key_id = aws_kms_key.eks.key_id

}

###############################################################################
# EKS Cluster
###############################################################################

resource "aws_eks_cluster" "this" {

  name = var.cluster_name

  version = var.cluster_version

  role_arn = aws_iam_role.eks_cluster.arn

  enabled_cluster_log_types = [

    "api",

    "audit",

    "authenticator",

    "controllerManager",

    "scheduler"

  ]

  vpc_config {

    subnet_ids = aws_subnet.private[*].id

    security_group_ids = [

      aws_security_group.eks_cluster.id

    ]

    endpoint_private_access = true

    endpoint_public_access = var.endpoint_public_access

  }

  encryption_config {

    provider {

      key_arn = aws_kms_key.eks.arn

    }

    resources = [

      "secrets"

    ]

  }

  depends_on = [

    aws_iam_role_policy_attachment.eks_cluster_policy,

    aws_cloudwatch_log_group.eks

  ]

  tags = local.common_tags

}

###############################################################################
# Institutional Quant Platform
# Kubernetes (EKS)
# Part 2 - Launch Template & Managed Node Group
###############################################################################

###############################################################################
# Latest Amazon Linux 2023 EKS AMI
###############################################################################

data "aws_ssm_parameter" "eks_ami" {

  name = "/aws/service/eks/optimized-ami/${var.cluster_version}/amazon-linux-2023/x86_64/standard/recommended/image_id"

}

###############################################################################
# Launch Template
###############################################################################

resource "aws_launch_template" "eks_nodes" {

  name_prefix = "${local.name_prefix}-lt-"

  image_id = data.aws_ssm_parameter.eks_ami.value

  update_default_version = true

  instance_type = var.node_instance_types[0]

  ebs_optimized = true

  monitoring {

    enabled = true

  }

  block_device_mappings {

    device_name = "/dev/xvda"

    ebs {

      volume_size = var.disk_size

      volume_type = "gp3"

      encrypted = true

      delete_on_termination = true

      throughput = 125

      iops = 3000

    }

  }

  metadata_options {

    http_endpoint = "enabled"

    http_tokens = "required"

    http_put_response_hop_limit = 2

    instance_metadata_tags = "enabled"

  }

  network_interfaces {

    security_groups = [

      aws_security_group.eks_nodes.id

    ]

    delete_on_termination = true

  }

  tag_specifications {

    resource_type = "instance"

    tags = merge(

      local.common_tags,

      {

        Name = "${local.name_prefix}-worker"

      }

    )

  }

  tag_specifications {

    resource_type = "volume"

    tags = local.common_tags

  }

  tag_specifications {

    resource_type = "network-interface"

    tags = local.common_tags

  }

  tags = local.common_tags

}

###############################################################################
# Managed Node Group
###############################################################################

resource "aws_eks_node_group" "default" {

  cluster_name = aws_eks_cluster.this.name

  node_group_name = local.node_group_name

  node_role_arn = aws_iam_role.eks_nodes.arn

  subnet_ids = aws_subnet.private[*].id

  ami_type = "AL2023_x86_64_STANDARD"

  capacity_type = "ON_DEMAND"

  instance_types = var.node_instance_types

  version = var.cluster_version

  release_version = null

  launch_template {

    id = aws_launch_template.eks_nodes.id

    version = aws_launch_template.eks_nodes.latest_version

  }

  scaling_config {

    desired_size = var.desired_capacity

    min_size = var.min_capacity

    max_size = var.max_capacity

  }

  update_config {

    max_unavailable_percentage = 25

  }

  labels = {

    workload = "general"

    environment = var.environment

    platform = "institutional-quant"

  }

  taint {

    key = "dedicated"

    value = "general"

    effect = "NO_SCHEDULE"

  }

  tags = merge(

    local.common_tags,

    {

      Name = local.node_group_name

    }

  )

  depends_on = [

    aws_iam_role_policy_attachment.worker_node_policy,

    aws_iam_role_policy_attachment.worker_cni_policy,

    aws_iam_role_policy_attachment.worker_ecr_policy,

    aws_launch_template.eks_nodes

  ]

}

###############################################################################
# Node Group Autoscaling Tags
###############################################################################

resource "aws_ec2_tag" "cluster_autoscaler_enabled" {

  resource_id = aws_eks_node_group.default.resources[0].autoscaling_groups[0].name

  key = "k8s.io/cluster-autoscaler/enabled"

  value = "true"

}

resource "aws_ec2_tag" "cluster_autoscaler_cluster" {

  resource_id = aws_eks_node_group.default.resources[0].autoscaling_groups[0].name

  key = "k8s.io/cluster-autoscaler/${var.cluster_name}"

  value = "owned"

}

###############################################################################
# Institutional Quant Platform
# Kubernetes (EKS)
# Part 3 - OIDC Provider & IAM Roles for Service Accounts
###############################################################################

###############################################################################
# EKS Cluster Identity
###############################################################################

data "tls_certificate" "eks_oidc" {

  url = aws_eks_cluster.this.identity[0].oidc[0].issuer

}

###############################################################################
# OIDC Provider
###############################################################################

resource "aws_iam_openid_connect_provider" "eks" {

  url = aws_eks_cluster.this.identity[0].oidc[0].issuer

  client_id_list = [

    "sts.amazonaws.com"

  ]

  thumbprint_list = [

    data.tls_certificate.eks_oidc.certificates[0].sha1_fingerprint

  ]

  tags = local.common_tags

}

###############################################################################
# IRSA Assume Role Policy
###############################################################################

data "aws_iam_policy_document" "irsa_assume_role" {

  statement {

    effect = "Allow"

    actions = [

      "sts:AssumeRoleWithWebIdentity"

    ]

    principals {

      type = "Federated"

      identifiers = [

        aws_iam_openid_connect_provider.eks.arn

      ]

    }

    condition {

      test = "StringEquals"

      variable = "${replace(
        aws_iam_openid_connect_provider.eks.url,
        "https://",
        ""
      )}:sub"

      values = [

        "system:serviceaccount:institutional-quant:institutional-quant-api",

        "system:serviceaccount:institutional-quant:institutional-quant-analytics",

        "system:serviceaccount:institutional-quant:institutional-quant-dashboard"

      ]

    }

  }

}

###############################################################################
# IRSA Role
###############################################################################

resource "aws_iam_role" "irsa" {

  name = "${local.name_prefix}-irsa"

  assume_role_policy = data.aws_iam_policy_document.irsa_assume_role.json

  tags = local.common_tags

}

###############################################################################
# S3 Access Policy
###############################################################################

data "aws_iam_policy_document" "s3_access" {

  statement {

    sid = "S3Access"

    effect = "Allow"

    actions = [

      "s3:GetObject",

      "s3:PutObject",

      "s3:DeleteObject",

      "s3:ListBucket"

    ]

    resources = [

      "arn:aws:s3:::institutional-quant-data",

      "arn:aws:s3:::institutional-quant-data/*"

    ]

  }

}

resource "aws_iam_policy" "s3_access" {

  name = "${local.name_prefix}-s3-access"

  description = "Institutional Quant Platform S3 Access"

  policy = data.aws_iam_policy_document.s3_access.json

  tags = local.common_tags

}

resource "aws_iam_role_policy_attachment" "s3_access" {

  role = aws_iam_role.irsa.name

  policy_arn = aws_iam_policy.s3_access.arn

}

###############################################################################
# CloudWatch Logs Policy
###############################################################################

data "aws_iam_policy_document" "cloudwatch_logs" {

  statement {

    effect = "Allow"

    actions = [

      "logs:CreateLogGroup",

      "logs:CreateLogStream",

      "logs:DescribeLogGroups",

      "logs:DescribeLogStreams",

      "logs:PutLogEvents"

    ]

    resources = [

      "*"

    ]

  }

}

resource "aws_iam_policy" "cloudwatch_logs" {

  name = "${local.name_prefix}-cloudwatch"

  policy = data.aws_iam_policy_document.cloudwatch_logs.json

  tags = local.common_tags

}

resource "aws_iam_role_policy_attachment" "cloudwatch_logs" {

  role = aws_iam_role.irsa.name

  policy_arn = aws_iam_policy.cloudwatch_logs.arn

}

###############################################################################
# Secrets Manager Policy
###############################################################################

data "aws_iam_policy_document" "secrets_manager" {

  statement {

    effect = "Allow"

    actions = [

      "secretsmanager:GetSecretValue",

      "secretsmanager:DescribeSecret"

    ]

    resources = [

      "*"

    ]

  }

}

resource "aws_iam_policy" "secrets_manager" {

  name = "${local.name_prefix}-secrets"

  policy = data.aws_iam_policy_document.secrets_manager.json

  tags = local.common_tags

}

resource "aws_iam_role_policy_attachment" "secrets_manager" {

  role = aws_iam_role.irsa.name

  policy_arn = aws_iam_policy.secrets_manager.arn

}

###############################################################################
# Parameter Store Policy
###############################################################################

data "aws_iam_policy_document" "ssm" {

  statement {

    effect = "Allow"

    actions = [

      "ssm:GetParameter",

      "ssm:GetParameters",

      "ssm:GetParametersByPath"

    ]

    resources = [

      "*"

    ]

  }

}

resource "aws_iam_policy" "ssm" {

  name = "${local.name_prefix}-ssm"

  policy = data.aws_iam_policy_document.ssm.json

  tags = local.common_tags

}

resource "aws_iam_role_policy_attachment" "ssm" {

  role = aws_iam_role.irsa.name

  policy_arn = aws_iam_policy.ssm.arn

}

###############################################################################
# KMS Access Policy
###############################################################################

data "aws_iam_policy_document" "kms" {

  statement {

    effect = "Allow"

    actions = [

      "kms:Decrypt",

      "kms:Encrypt",

      "kms:GenerateDataKey",

      "kms:DescribeKey"

    ]

    resources = [

      aws_kms_key.eks.arn

    ]

  }

}

resource "aws_iam_policy" "kms" {

  name = "${local.name_prefix}-kms"

  policy = data.aws_iam_policy_document.kms.json

  tags = local.common_tags

}

resource "aws_iam_role_policy_attachment" "kms" {

  role = aws_iam_role.irsa.name

  policy_arn = aws_iam_policy.kms.arn

}

###############################################################################
# Institutional Quant Platform
# Kubernetes (EKS)
# Part 4 - EKS Managed Add-ons
###############################################################################

###############################################################################
# EBS CSI Driver IAM Role
###############################################################################

data "aws_iam_policy_document" "ebs_csi_assume_role" {

  statement {

    effect = "Allow"

    actions = [

      "sts:AssumeRoleWithWebIdentity"

    ]

    principals {

      type = "Federated"

      identifiers = [

        aws_iam_openid_connect_provider.eks.arn

      ]

    }

    condition {

      test = "StringEquals"

      variable = "${replace(
        aws_iam_openid_connect_provider.eks.url,
        "https://",
        ""
      )}:sub"

      values = [

        "system:serviceaccount:kube-system:ebs-csi-controller-sa"

      ]

    }

  }

}

resource "aws_iam_role" "ebs_csi" {

  name = "${local.name_prefix}-ebs-csi"

  assume_role_policy = data.aws_iam_policy_document.ebs_csi_assume_role.json

  tags = local.common_tags

}

resource "aws_iam_role_policy_attachment" "ebs_csi" {

  role = aws_iam_role.ebs_csi.name

  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEBSCSIDriverPolicy"

}

###############################################################################
# Amazon VPC CNI
###############################################################################

resource "aws_eks_addon" "vpc_cni" {

  cluster_name = aws_eks_cluster.this.name

  addon_name = "vpc-cni"

  resolve_conflicts_on_create = "OVERWRITE"

  resolve_conflicts_on_update = "OVERWRITE"

  depends_on = [

    aws_eks_node_group.default

  ]

}

###############################################################################
# CoreDNS
###############################################################################

resource "aws_eks_addon" "coredns" {

  cluster_name = aws_eks_cluster.this.name

  addon_name = "coredns"

  resolve_conflicts_on_create = "OVERWRITE"

  resolve_conflicts_on_update = "OVERWRITE"

  depends_on = [

    aws_eks_node_group.default

  ]

}

###############################################################################
# kube-proxy
###############################################################################

resource "aws_eks_addon" "kube_proxy" {

  cluster_name = aws_eks_cluster.this.name

  addon_name = "kube-proxy"

  resolve_conflicts_on_create = "OVERWRITE"

  resolve_conflicts_on_update = "OVERWRITE"

  depends_on = [

    aws_eks_node_group.default

  ]

}

###############################################################################
# EBS CSI Driver
###############################################################################

resource "aws_eks_addon" "ebs_csi" {

  cluster_name = aws_eks_cluster.this.name

  addon_name = "aws-ebs-csi-driver"

  service_account_role_arn = aws_iam_role.ebs_csi.arn

  resolve_conflicts_on_create = "OVERWRITE"

  resolve_conflicts_on_update = "OVERWRITE"

  depends_on = [

    aws_iam_role_policy_attachment.ebs_csi,

    aws_eks_node_group.default

  ]

}

###############################################################################
# Pod Identity Agent
###############################################################################

resource "aws_eks_addon" "pod_identity" {

  cluster_name = aws_eks_cluster.this.name

  addon_name = "eks-pod-identity-agent"

  resolve_conflicts_on_create = "OVERWRITE"

  resolve_conflicts_on_update = "OVERWRITE"

  depends_on = [

    aws_eks_node_group.default

  ]

}

###############################################################################
# Metrics Server (Helm)
###############################################################################

resource "helm_release" "metrics_server" {

  name = "metrics-server"

  repository = "https://kubernetes-sigs.github.io/metrics-server/"

  chart = "metrics-server"

  namespace = "kube-system"

  create_namespace = false

  wait = true

  timeout = 600

  values = [

<<EOF
args:
  - --kubelet-insecure-tls
EOF

  ]

  depends_on = [

    aws_eks_addon.coredns,

    aws_eks_addon.kube_proxy,

    aws_eks_addon.vpc_cni

  ]

}

###############################################################################
# Cluster Autoscaler (Helm)
###############################################################################

resource "helm_release" "cluster_autoscaler" {

  name = "cluster-autoscaler"

  repository = "https://kubernetes.github.io/autoscaler"

  chart = "cluster-autoscaler"

  namespace = "kube-system"

  create_namespace = false

  wait = true

  timeout = 600

  set {

    name = "autoDiscovery.clusterName"

    value = aws_eks_cluster.this.name

  }

  set {

    name = "awsRegion"

    value = var.aws_region

  }

  depends_on = [

    aws_eks_node_group.default

  ]

}

###############################################################################
# Institutional Quant Platform
# Kubernetes (EKS)
# Part 5 - Access Entries, Authentication & Final Resources
###############################################################################

###############################################################################
# Current AWS Identity
###############################################################################

data "aws_caller_identity" "current" {}

###############################################################################
# EKS Access Entry
###############################################################################

resource "aws_eks_access_entry" "admin" {

  cluster_name = aws_eks_cluster.this.name

  principal_arn = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"

  type = "STANDARD"

}

###############################################################################
# Cluster Admin Policy
###############################################################################

resource "aws_eks_access_policy_association" "cluster_admin" {

  cluster_name = aws_eks_cluster.this.name

  principal_arn = aws_eks_access_entry.admin.principal_arn

  policy_arn = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"

  access_scope {

    type = "cluster"

  }

}

###############################################################################
# Storage Class
###############################################################################

resource "kubernetes_storage_class_v1" "gp3" {

  metadata {

    name = "gp3"

  }

  storage_provisioner = "ebs.csi.aws.com"

  reclaim_policy = "Delete"

  volume_binding_mode = "WaitForFirstConsumer"

  allow_volume_expansion = true

  parameters = {

    type = "gp3"

    encrypted = "true"

    fsType = "ext4"

  }

  depends_on = [

    aws_eks_addon.ebs_csi

  ]

}

###############################################################################
# Namespace
###############################################################################

resource "kubernetes_namespace" "institutional_quant" {

  metadata {

    name = "institutional-quant"

    labels = {

      app = "institutional-quant"

      environment = var.environment

    }

  }

}

###############################################################################
# Deploy Helm Chart
###############################################################################

resource "helm_release" "institutional_quant" {

  name = "institutional-quant"

  chart = "../helm"

  namespace = kubernetes_namespace.institutional_quant.metadata[0].name

  create_namespace = false

  timeout = 900

  wait = true

  dependency_update = true

  values = [

    file("../helm/values.yaml")

  ]

  depends_on = [

    kubernetes_storage_class_v1.gp3,

    helm_release.metrics_server,

    helm_release.cluster_autoscaler

  ]

}

###############################################################################
# Kubernetes Version
###############################################################################

data "kubernetes_all_namespaces" "all" {

  depends_on = [

    aws_eks_cluster.this

  ]

}

###############################################################################
# Local Kubeconfig
###############################################################################

resource "local_file" "kubeconfig" {

  filename = "${path.module}/generated-kubeconfig.txt"

  content = <<EOF

Run the following command to configure kubectl:

aws eks update-kubeconfig \
    --region ${var.aws_region} \
    --name ${aws_eks_cluster.this.name}

EOF

}

###############################################################################
# Terraform Completion
###############################################################################

resource "null_resource" "deployment_complete" {

  depends_on = [

    helm_release.institutional_quant

  ]

  provisioner "local-exec" {

    command = <<EOF
echo "=========================================="
echo "Institutional Quant Platform Ready"
echo "=========================================="
echo ""
echo "Cluster: ${aws_eks_cluster.this.name}"
echo "Region : ${var.aws_region}"
echo ""
echo "Run:"
echo "aws eks update-kubeconfig --region ${var.aws_region} --name ${aws_eks_cluster.this.name}"
echo ""
echo "kubectl get nodes"
echo "kubectl get pods -A"
echo "helm list -A"
echo ""
echo "=========================================="
EOF

  }

}