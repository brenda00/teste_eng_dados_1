variable "region" {
  description = "aws region"
  default     = "us-east-1"
}

variable "account_id" {
  default = 317634511592
}

variable "prefix" {
  description = "objects prefix"
  default     = "etlproj"
}

# Prefix configuration and project common tags
locals {
  glue_bucket = "${var.prefix}-${var.bucket_names[4]}"
  prefix      = var.prefix
  common_tags = {
    Project = "trn-cc-bg-aws"
  }
}

variable "bucket_names" {
  description = "s3 bucket names"
  type        = list(string)
  default = [
    "bucket-bronzee",
    "bucket-silveer",
    "processing-zone",
    "consumer-zone",
    "aws-glue-scripts"
  ]
}

variable "glue_job_role_arn" {
  description = "The ARN of the IAM role associated with this job."
  default     = null
}

variable "access_key" {
  description = "AWS Access Key"
  type        = string
  sensitive   = true
}

variable "secret_key" {
  description = "AWS Secret Key"
  type        = string
  sensitive   = true
}