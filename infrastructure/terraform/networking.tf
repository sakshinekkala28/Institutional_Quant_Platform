###############################################################################
# Institutional Quant Platform
# Networking
###############################################################################

###############################################################################
# VPC
###############################################################################

resource "aws_vpc" "this" {

  cidr_block = var.vpc_cidr

  enable_dns_support = true

  enable_dns_hostnames = true

  tags = merge(

    local.common_tags,

    {

      Name = local.vpc_name

    }

  )

}

###############################################################################
# Internet Gateway
###############################################################################

resource "aws_internet_gateway" "this" {

  vpc_id = aws_vpc.this.id

  tags = merge(

    local.common_tags,

    {

      Name = "${local.name_prefix}-igw"

    }

  )

}

###############################################################################
# Public Subnets
###############################################################################

resource "aws_subnet" "public" {

  count = length(var.public_subnets)

  vpc_id = aws_vpc.this.id

  cidr_block = var.public_subnets[count.index]

  availability_zone = var.availability_zones[count.index]

  map_public_ip_on_launch = true

  tags = merge(

    local.common_tags,

    {

      Name = local.public_subnet_names[count.index]

      "kubernetes.io/role/elb" = "1"

    }

  )

}

###############################################################################
# Private Subnets
###############################################################################

resource "aws_subnet" "private" {

  count = length(var.private_subnets)

  vpc_id = aws_vpc.this.id

  cidr_block = var.private_subnets[count.index]

  availability_zone = var.availability_zones[count.index]

  tags = merge(

    local.common_tags,

    {

      Name = local.private_subnet_names[count.index]

      "kubernetes.io/role/internal-elb" = "1"

    }

  )

}

###############################################################################
# Elastic IP
###############################################################################

resource "aws_eip" "nat" {

  domain = "vpc"

  depends_on = [

    aws_internet_gateway.this

  ]

  tags = merge(

    local.common_tags,

    {

      Name = "${local.name_prefix}-nat-eip"

    }

  )

}

###############################################################################
# NAT Gateway
###############################################################################

resource "aws_nat_gateway" "this" {

  allocation_id = aws_eip.nat.id

  subnet_id = aws_subnet.public[0].id

  tags = merge(

    local.common_tags,

    {

      Name = "${local.name_prefix}-nat"

    }

  )

  depends_on = [

    aws_internet_gateway.this

  ]

}

###############################################################################
# Public Route Table
###############################################################################

resource "aws_route_table" "public" {

  vpc_id = aws_vpc.this.id

  route {

    cidr_block = "0.0.0.0/0"

    gateway_id = aws_internet_gateway.this.id

  }

  tags = merge(

    local.common_tags,

    {

      Name = "${local.name_prefix}-public-rt"

    }

  )

}

###############################################################################
# Private Route Table
###############################################################################

resource "aws_route_table" "private" {

  vpc_id = aws_vpc.this.id

  route {

    cidr_block = "0.0.0.0/0"

    nat_gateway_id = aws_nat_gateway.this.id

  }

  tags = merge(

    local.common_tags,

    {

      Name = "${local.name_prefix}-private-rt"

    }

  )

}

###############################################################################
# Public Route Associations
###############################################################################

resource "aws_route_table_association" "public" {

  count = length(aws_subnet.public)

  subnet_id = aws_subnet.public[count.index].id

  route_table_id = aws_route_table.public.id

}

###############################################################################
# Private Route Associations
###############################################################################

resource "aws_route_table_association" "private" {

  count = length(aws_subnet.private)

  subnet_id = aws_subnet.private[count.index].id

  route_table_id = aws_route_table.private.id

}

###############################################################################
# Default Security Group
###############################################################################

resource "aws_security_group" "platform" {

  name = "${local.name_prefix}-platform"

  description = "Institutional Quant Platform"

  vpc_id = aws_vpc.this.id

  ingress {

    from_port = 443

    to_port = 443

    protocol = "tcp"

    cidr_blocks = [

      "0.0.0.0/0"

    ]

  }

  ingress {

    from_port = 80

    to_port = 80

    protocol = "tcp"

    cidr_blocks = [

      "0.0.0.0/0"

    ]

  }

  egress {

    from_port = 0

    to_port = 0

    protocol = "-1"

    cidr_blocks = [

      "0.0.0.0/0"

    ]

  }

  tags = merge(

    local.common_tags,

    {

      Name = "${local.name_prefix}-sg"

    }

  )

}