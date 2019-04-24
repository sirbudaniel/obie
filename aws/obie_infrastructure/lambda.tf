resource "aws_lambda_function" "obie_lambda_function" {
  filename = "${var.lambda_function_archive}"
  function_name = "${var.obie_lambda_function_name}"
  role = "arn:aws:iam::404771020307:role/obie_role_lambda"
  handler = "run_task.handler"
  runtime = "python3.6"
}

resource "aws_api_gateway_api_key" "obie_api_gw_key" {
  name = "obie_api_key"
}

resource "aws_api_gateway_rest_api" "obie_rest_api" {
  name        = "Serverless Obie"
}

resource "aws_api_gateway_usage_plan" "demo_api_usage_plan" {
  name = "usage_obie"

  api_stages {
    api_id = "${aws_api_gateway_rest_api.obie_rest_api.id}"
    stage  = "${aws_api_gateway_deployment.example.stage_name}"
  }
}

resource "aws_api_gateway_usage_plan_key" "demo_api_usage_plan_key" {
  key_id        = "${aws_api_gateway_api_key.obie_api_gw_key.id}"
  key_type      = "API_KEY"
  usage_plan_id = "${aws_api_gateway_usage_plan.demo_api_usage_plan.id}"
}

resource "aws_api_gateway_resource" "proxy" {
  rest_api_id = "${aws_api_gateway_rest_api.obie_rest_api.id}"
  parent_id   = "${aws_api_gateway_rest_api.obie_rest_api.root_resource_id}"
  path_part   = "{proxy+}"
}

resource "aws_api_gateway_method" "proxy" {
  rest_api_id   = "${aws_api_gateway_rest_api.obie_rest_api.id}"
  resource_id   = "${aws_api_gateway_resource.proxy.id}"
  http_method   = "ANY"
  authorization = "NONE"
  api_key_required = true
}

resource "aws_api_gateway_integration" "lambda" {
  rest_api_id = "${aws_api_gateway_rest_api.obie_rest_api.id}"
  resource_id = "${aws_api_gateway_method.proxy.resource_id}"
  http_method = "${aws_api_gateway_method.proxy.http_method}"

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "${aws_lambda_function.obie_lambda_function.invoke_arn}"
}

resource "aws_api_gateway_deployment" "example" {
  depends_on = [
    "aws_api_gateway_integration.lambda",
  ]

  rest_api_id = "${aws_api_gateway_rest_api.obie_rest_api.id}"
  stage_name  = "prod"
}

resource "aws_lambda_permission" "apigw" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.obie_lambda_function.arn}"
  principal     = "apigateway.amazonaws.com"

  source_arn = "${aws_api_gateway_deployment.example.execution_arn}/*/*"
}

output "base_url" {
  value = "${aws_api_gateway_deployment.example.invoke_url}/${var.obie_lambda_function_name}"
}
output "x-api-key" {
  value = "${aws_api_gateway_api_key.obie_api_gw_key.value}"
}
