###############################################################################
# Institutional Quant Platform
# Terraform Backend
###############################################################################

terraform {

  backend "s3" {

    bucket = "institutional-quant-terraform-state"

    key = "production/terraform.tfstate"

    region = "ap-south-1"

    dynamodb_table = "institutional-quant-terraform-lock"

    encrypt = true

  }

}