variable "aws_access_key" {
  type = string
}

variable "aws_secret_key" {
  type = string
}


provider "aws" {
  region     = "us-west-2" # Change this to your desired region
  access_key = "${var.aws_access_key}"
  secret_key = "${var.aws_secret_key}"
}

resource "aws_iot_thing" "litmus_device" {
  name = "litmus-gateway"
}

resource "aws_lambda_function" "iot_to_edgeimpulse" {
  filename      = "${path.module}/ei-python.zip" # Replace with your Lambda function code
  function_name = "iot-to-edgeimpulse"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "index.lambda_handler"
  runtime       = "python3.12" # Change this based on your Lambda runtime
}

resource "aws_iam_role" "lambda_exec_role" {
  name = "lambda-exec-role2"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [{
      Action = "sts:AssumeRole",
      Effect = "Allow",
      Principal = {
        Service = "lambda.amazonaws.com"
      }
    }]
  })
}

resource "aws_iam_policy_attachment" "lambda_execution_policy" {
  name       = "lambda-execution-policy"
  roles      = [aws_iam_role.lambda_exec_role.name]
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iot_topic_rule" "iot_to_ei" {
  enabled                   = true
  name                      = "iot_to_ei_rule"
  sql                       = "SELECT * FROM 'litmusedgetopic'"
  description               = "This rule forwards the messages received on the litmusedgetopic AWS IoT topic to the iot-to-edgeimpulse Lambda function"
  sql_version               = "2016-03-23"
  lambda {
    function_arn = aws_lambda_function.iot_to_edgeimpulse.arn
  }
}

data "archive_file" "zip_the_python_code" {
  type        = "zip"
  source_dir  = "${path.module}/python/"
  output_path = "${path.module}/ei-python.zip"
}