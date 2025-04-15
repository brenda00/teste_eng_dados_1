resource "aws_s3_bucket" "buckets" {
  count  = length(var.bucket_names)
  bucket = "${var.prefix}-${var.bucket_names[count.index]}"


  force_destroy = true
  tags = local.common_tags
}

resource "aws_s3_object" "upload_csv_landing" {
  bucket = "${var.prefix}-${var.bucket_names[0]}" 
  key    = "arquivo/clientes_sinteticos.csv"                     
  source = "../datasets/clientes_sinteticos.csv"  
  content_type = "text/csv"

  tags = local.common_tags
}

resource "aws_s3_object" "upload_script_glue" {
  bucket = "${var.prefix}-${var.bucket_names[5]}" 
  key    = "job/glue-etl.py"                     
  source = "../app/job/glue-etl.py"  
  content_type = "python"

  tags = local.common_tags
}

resource "aws_s3_object" "upload_jar_delta" {
  bucket = "${var.prefix}-${var.bucket_names[5]}" 
  key    = "jars/delta-core_2.12-1.0.0.jar"                     
  source = "../app/jars/delta-core_2.12-1.0.0.jar"  
  content_type = "jar"

  tags = local.common_tags
}

resource "aws_cloudwatch_log_group" "glue_log_group" {
  name              = "/aws-glue/jobs/${var.prefix}-logs"
  retention_in_days = 14

  tags = local.common_tags
}

resource "aws_s3_bucket_server_side_encryption_configuration" "bucket_sse" {
  count  = length(var.bucket_names)
  bucket = "${var.prefix}-${var.bucket_names[count.index]}"


  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }

   depends_on = [
    aws_s3_bucket.buckets
  ]

}


# Rules for public access block
resource "aws_s3_bucket_public_access_block" "public_access_block" {
  count  = length(var.bucket_names)
  bucket = "${var.prefix}-${var.bucket_names[count.index]}"


  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true

  depends_on = [
    aws_s3_bucket.buckets
  ]

}