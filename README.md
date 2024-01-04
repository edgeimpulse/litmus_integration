# Overview

This folder contains the infrastructure scripts needed to build a Litmus Edge Gateway to AWS IoT connector.

This deployment includes: 

- 1 AWS IoT Device
- 1 Lambda function (python)
- 1 Event Rule, which forwards the incoming AWS IoT messages to the Lambda

# Prerequisites

1. This module uses Terraform for deployment, and requires that the (Terraform CLI)[https://developer.hashicorp.com/terraform/install] be installed on the client machine that is running these scripts.

2. An AWS access_key and secret_key for a User who is able to create an IoT device, Event Rules, Lambda functions and to create and assign roles to projects.

3. A Litmus Edge Gateway installation, which will be configured to generate data and send it to AWS IoT. 

4. An Edge Impulse project, which will be receiving the data that the lambda will forward over

# Customize the Code

/python/lambda.py is the only code which is being run as part of this integration. 

Within this, there is a list of sensor values (called "Tags" in Litmus) which will be the features within your Edge Impulse dataset. These sensors are listed in a dictionary. If those sensors don't have values within a given set of messages, the value will be set to 0.0 for that sample. 

    whitelist_sensors = [...]

# AWS Deployment 

To deploy: 

1. Run the command to initialize a folder as a Terraform project: 

    terraform init

This only needs to be run once, but it is not harmful and can be run multiple times. 

2. Update the input.tfvars file to reflect the AWS secret key and access key for the User you will be performing this operation as. 

3. Run the command to build a "plan" which Terraform will use to configure the current AWS environment (which is defined by the Access_Key and Secret_Key)

    terraform plan -var-file input.tfvars -out tf.plan

4. This should create all of the infrastructure that is necessary to translate the messages coming from the Litmus Edge Gateway to the CBOR format, and post that to the Edge Impulse ingestion API

# Connecting the Litmus Edge Gateway 

The Litmus Edge Gateway has pre-built integration with AWS integration, which is described in their [https://docs.litmus.io/litmusedge/how-to-guides/integration-guides/aws-amazon-web-services](Solution Guide for AWS).

When choosing the AWS IoT topic name, this integration is pre-built to use "litmusedgetopic".