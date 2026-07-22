###############################################################################
# Terraform Backend Configuration
# Environment : Staging
# Institutional Quant Platform
###############################################################################
#
# This file configures the remote Terraform state backend for the
# Staging environment.
#
# Replace the placeholder values below with your organization's
# actual backend configuration before running:
#
#   terraform init \
#       -backend-config=docs/infrastructure/terraform/environments/staging/backend.hcl
#
###############################################################################

bucket = "<terraform-state-bucket>"

key = "institutional-quant-platform/staging/terraform.tfstate"

region = "<aws-region>"

encrypt = true

dynamodb_table = "<terraform-lock-table>"