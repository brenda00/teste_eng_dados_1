
resource "aws_glue_job" "glue_job" {
  name              = "pipeline_clientes"
  role_arn          = aws_iam_role.glue_job.arn
  glue_version      = "5.0"
  worker_type       = "G.1X"
  number_of_workers = 10
  timeout           = 5

  command {
    script_location = "s3://${local.glue_bucket}/job/glue-etl.py"
    python_version  = "3"
  }

  default_arguments = {
    "--additional-python-modules" = "delta-spark==1.0.0"
    "--extra-jars" = "s3://${var.prefix}-${var.bucket_names[5]}/jars/delta-core_2.12-1.0.0.jar"
    "--conf spark.delta.logStore.class" = "org.apache.spark.sql.delta.storage.S3SingleDriverLogStore"
    "--conf spark.sql.extensions" = "io.delta.sql.DeltaSparkSessionExtension"
    
  }
  
}

resource "aws_glue_catalog_database" "silver" {
  name = "db_silver"
}

# Databases para Bronze e Silver
resource "aws_glue_catalog_database" "bronze" {
  name = "db_bronze"
}


# Crawler Bronze
resource "aws_glue_crawler" "bronze_crawler" {
  name          = "${var.prefix}-bronze-crawler"
  role          = aws_iam_role.glue_job.arn
  database_name = aws_glue_catalog_database.bronze.name
  description   = "Crawler para camada bronze do cliente"

  s3_target {
    path = "s3://etlproj-bronze/tabela_cliente_landing/"
  }

  schema_change_policy {
    update_behavior = "UPDATE_IN_DATABASE"
    delete_behavior = "LOG"
  }

  configuration = jsonencode({
    Version = 1.0,
    CrawlerOutput = {
      Partitions = {
        AddOrUpdateBehavior = "InheritFromTable"
      }
    }
  })

  tags = local.common_tags
}

# Crawler Silver
resource "aws_glue_crawler" "silver_crawler" {
  name          = "${var.prefix}-silver-crawler"
  role          = aws_iam_role.glue_job.arn
  database_name = aws_glue_catalog_database.silver.name
  description   = "Crawler para camada silver do cliente"

  s3_target {
    path = "s3://etlproj-silver/tb_cliente/"
  }

  schema_change_policy {
    update_behavior = "UPDATE_IN_DATABASE"
    delete_behavior = "LOG"
  }

  configuration = jsonencode({
    Version = 1.0,
    CrawlerOutput = {
      Partitions = {
        AddOrUpdateBehavior = "InheritFromTable"
      }
    }
  })

  tags = local.common_tags
}