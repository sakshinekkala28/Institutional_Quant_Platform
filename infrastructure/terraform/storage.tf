###############################################################################
# Institutional Quant Platform
# Storage
###############################################################################

###############################################################################
# Market Data Bucket
###############################################################################

resource "aws_s3_bucket" "market_data" {

  bucket = "${local.name_prefix}-market-data"

  tags = merge(

    local.common_tags,

    {

      Name = "${local.name_prefix}-market-data"

    }

  )

}

resource "aws_s3_bucket_versioning" "market_data" {

  bucket = aws_s3_bucket.market_data.id

  versioning_configuration {

    status = "Enabled"

  }

}

resource "aws_s3_bucket_server_side_encryption_configuration" "market_data" {

  bucket = aws_s3_bucket.market_data.id

  rule {

    apply_server_side_encryption_by_default {

      sse_algorithm = "AES256"

    }

  }

}

resource "aws_s3_bucket_public_access_block" "market_data" {

  bucket = aws_s3_bucket.market_data.id

  block_public_acls = true

  block_public_policy = true

  ignore_public_acls = true

  restrict_public_buckets = true

}

###############################################################################
# Analytics Bucket
###############################################################################

resource "aws_s3_bucket" "analytics" {

  bucket = "${local.name_prefix}-analytics"

  tags = local.common_tags

}

resource "aws_s3_bucket_versioning" "analytics" {

  bucket = aws_s3_bucket.analytics.id

  versioning_configuration {

    status = "Enabled"

  }

}

resource "aws_s3_bucket_server_side_encryption_configuration" "analytics" {

  bucket = aws_s3_bucket.analytics.id

  rule {

    apply_server_side_encryption_by_default {

      sse_algorithm = "AES256"

    }

  }

}

resource "aws_s3_bucket_public_access_block" "analytics" {

  bucket = aws_s3_bucket.analytics.id

  block_public_acls = true

  block_public_policy = true

  ignore_public_acls = true

  restrict_public_buckets = true

}

###############################################################################
# Reports Bucket
###############################################################################

resource "aws_s3_bucket" "reports" {

  bucket = "${local.name_prefix}-reports"

  tags = local.common_tags

}

resource "aws_s3_bucket_versioning" "reports" {

  bucket = aws_s3_bucket.reports.id

  versioning_configuration {

    status = "Enabled"

  }

}

resource "aws_s3_bucket_server_side_encryption_configuration" "reports" {

  bucket = aws_s3_bucket.reports.id

  rule {

    apply_server_side_encryption_by_default {

      sse_algorithm = "AES256"

    }

  }

}

resource "aws_s3_bucket_public_access_block" "reports" {

  bucket = aws_s3_bucket.reports.id

  block_public_acls = true

  block_public_policy = true

  ignore_public_acls = true

  restrict_public_buckets = true

}

###############################################################################
# Backups Bucket
###############################################################################

resource "aws_s3_bucket" "backups" {

  bucket = "${local.name_prefix}-backups"

  tags = local.common_tags

}

resource "aws_s3_bucket_versioning" "backups" {

  bucket = aws_s3_bucket.backups.id

  versioning_configuration {

    status = "Enabled"

  }

}

resource "aws_s3_bucket_server_side_encryption_configuration" "backups" {

  bucket = aws_s3_bucket.backups.id

  rule {

    apply_server_side_encryption_by_default {

      sse_algorithm = "AES256"

    }

  }

}

resource "aws_s3_bucket_public_access_block" "backups" {

  bucket = aws_s3_bucket.backups.id

  block_public_acls = true

  block_public_policy = true

  ignore_public_acls = true

  restrict_public_buckets = true

}

###############################################################################
# Lifecycle Policies
###############################################################################

resource "aws_s3_bucket_lifecycle_configuration" "market_data" {

  bucket = aws_s3_bucket.market_data.id

  rule {

    id = "market-data"

    status = "Enabled"

    transition {

      days = 90

      storage_class = "STANDARD_IA"

    }

    transition {

      days = 365

      storage_class = "GLACIER"

    }

  }

}

resource "aws_s3_bucket_lifecycle_configuration" "analytics" {

  bucket = aws_s3_bucket.analytics.id

  rule {

    id = "analytics"

    status = "Enabled"

    transition {

      days = 180

      storage_class = "STANDARD_IA"

    }

  }

}

resource "aws_s3_bucket_lifecycle_configuration" "reports" {

  bucket = aws_s3_bucket.reports.id

  rule {

    id = "reports"

    status = "Enabled"

    expiration {

      days = 3650

    }

  }

}

resource "aws_s3_bucket_lifecycle_configuration" "backups" {

  bucket = aws_s3_bucket.backups.id

  rule {

    id = "backups"

    status = "Enabled"

    transition {

      days = 30

      storage_class = "STANDARD_IA"

    }

    transition {

      days = 180

      storage_class = "GLACIER"

    }

    expiration {

      days = 3650

    }

  }

}