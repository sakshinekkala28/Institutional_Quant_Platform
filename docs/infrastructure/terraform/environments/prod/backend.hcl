###############################################################################
# Terraform Backend Configuration
# Environment : Production
# Institutional Quant Platform
###############################################################################
#
# This file configures the remote Terraform state backend for the
# Production environment.
#
# Replace the placeholder values below with your organization's
# actual backend configuration before running:
#
#   terraform init \
#       -backend-config=docs/infrastructure/terraform/environments/prod/backend.hcl
#
# Production Terraform state should be:
# - Stored remotely
# - Versioned
# - Encrypted
# - Access-controlled
# - Protected with state locking
#
###############################################################################

bucket = "<terraform-state-bucket>"

key = "institutional-quant-platform/prod/terraform.tfstate"

region = "<aws-region>"

encrypt = true

dynamodb_table = "<terraform-lock-table>"