resource "aws_vpc" "vpc" {
  cidr_block = "${var.vpc_cidr}"
  tags       = {
    Name = "${var.vpc_name}"
  }
}

resource "aws_internet_gateway" "InternetGateway" {
  vpc_id = "${aws_vpc.vpc.id}"
  tags   = {
    Name = "${var.internet_gw_name}"
  }
}

resource "aws_subnet" "subnet_pub" {
  cidr_block = "${var.subnet_pub_cidr}"
  vpc_id = "${aws_vpc.vpc.id}"
  tags   = {
    Name = "${var.subnet_pub_name}"
  }
}

resource "aws_subnet" "subnet_priv" {
  cidr_block = "${var.subnet_priv_cidr}"
  vpc_id = "${aws_vpc.vpc.id}"
  tags   = {
    Name = "${var.subnet_priv_name}"
  }
}

resource "aws_route_table" "pub_route_table" {
  vpc_id = "${aws_vpc.vpc.id}"

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = "${aws_internet_gateway.InternetGateway.id}"
  }

  tags = {
    Name = "${var.route_table_name}"
  }
}

resource "aws_route_table_association" "generic_priv_subnet_association" {
  route_table_id = "${aws_route_table.pub_route_table.id}"
  subnet_id      = "${aws_subnet.subnet_pub.id}"
}
