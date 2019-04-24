resource "aws_ecs_cluster" "ecs_cluster" {
  name = "${var.ecs_cluster_name}"
}

resource "aws_cloudwatch_log_group" "aws_logs" {
  name = "${var.cloudwatch_log_group}"
}
