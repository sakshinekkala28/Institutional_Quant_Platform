###############################################################################
# Institutional Quant Platform
# Terraform Version Constraints
###############################################################################

terraform {

  required_version = ">= 1.8.0"

  required_providers {

    aws = {

      source = "hashicorp/aws"

      version = "~> 5.60"

    }

    kubernetes = {

      source = "hashicorp/kubernetes"

      version = "~> 2.36"

    }

    helm = {

      source = "hashicorp/helm"

      version = "~> 2.15"

    }

    tls = {

      source = "hashicorp/tls"

      version = "~> 4.0"

    }

    random = {

      source = "hashicorp/random"

      version = "~> 3.7"

    }

    local = {

      source = "hashicorp/local"

      version = "~> 2.5"

    }

    null = {

      source = "hashicorp/null"

      version = "~> 3.2"

    }

    archive = {

      source = "hashicorp/archive"

      version = "~> 2.6"

    }

    time = {

      source = "hashicorp/time"

      version = "~> 0.12"

    }

    http = {

      source = "hashicorp/http"

      version = "~> 3.4"

    }

  }

}