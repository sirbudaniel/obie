data "aws_iam_policy_document" "instance_policy" {
  statement {
            sid = "VisualEditor0"
            effect = "Allow"
            actions= ["ecs:RunTask"]
            resources= ["*"]
        }

  statement {
            sid = "VisualEditor1"
            effect = "Allow"
            actions = ["iam:PassRole"]
            resources = ["arn:aws:iam::404771020307:role/obie_role"]
        }
}

resource "aws_iam_policy" "obie_policy" {
  name   = "${var.obie_policy_name}"
  path   = "/"
  policy = "${data.aws_iam_policy_document.instance_policy.json}"
}

resource "aws_iam_role" "obie_role_lambda" {
  name = "${var.obie_role_lambda}"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
  EOF
}

resource "aws_iam_role_policy_attachment" "obie_policy_attachment" {
  policy_arn = "${aws_iam_policy.obie_policy.arn}"
  role = "${aws_iam_role.obie_role_lambda.name}"
}

resource "aws_iam_role_policy_attachment" "ecs_fullAccess" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonECS_FullAccess"
  role = "${aws_iam_role.obie_role_lambda.name}"
}

resource "aws_iam_role" "obie_role" {
  name = "${var.obie_role}"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
  EOF
}

resource "aws_iam_role_policy_attachment" "ecs_policy" {
  role   = "${aws_iam_role.obie_role.name}"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy_attachment" "administrator_policy" {
  role   = "${aws_iam_role.obie_role.name}"
  policy_arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}
