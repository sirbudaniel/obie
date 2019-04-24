variable "profile" {}
variable "region" {
  default = "us-east-1"
}

variable "vpc_cidr" {}
variable "subnet_pub_cidr" {}
variable "subnet_priv_cidr" {}

variable "vpc_name" {
  default =  "obie_pipeline_vpc"
}
variable "internet_gw_name" {
  default = "obie_internet_gw"
}
variable "subnet_pub_name" {
  default = "obie_pub_subnet"
}
variable "subnet_priv_name" {
  default = "obie_priv_subnet"
}
variable "route_table_name" {
  default = "obie_pub_rt"
}
variable "ecs_cluster_name" {}
variable "cloudwatch_log_group" {}
variable "obie_policy_name" {
  default = "obie_lambda"
}
variable "obie_role_lambda" {
  default = "obie_role_lambda"
}
variable "obie_role" {
  default = "obie_role"
}
variable "obie_lambda_function_name" {
  default = "obie_lambda_function"
}
variable "lambda_function_archive" {
  default = "../lambda/run_task_py.zip"
}
