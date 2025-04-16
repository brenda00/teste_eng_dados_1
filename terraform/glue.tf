# ===============================
# Glue Job: pipeline_clientes
# ===============================
resource "aws_glue_job" "glue_job" {
  name              = "pipeline_clientes"                     
  role_arn          = aws_iam_role.glue_job.arn              
  glue_version      = "5.0"                                  
  worker_type       = "G.1X"                                 
  number_of_workers = 2                                      
  timeout           = 5                                      

  command {
    script_location = "s3://${local.glue_bucket}/job/glue-etl.py"  # Caminho no S3 para o script
    python_version  = "3"
  }

  default_arguments = {
    "--additional-python-modules"           = "delta-spark==1.0.0"                            
    "--extra-jars"                          = "s3://${var.prefix}-${var.bucket_names[5]}/jars/delta-core_2.12-1.0.0.jar"  
    "--conf spark.delta.logStore.class"     = "org.apache.spark.sql.delta.storage.S3SingleDriverLogStore"  
    "--conf spark.sql.extensions"           = "io.delta.sql.DeltaSparkSessionExtension"                   
  }
}

# ===============================
# Trigger ON_DEMAND para iniciar o Glue Job
# ===============================
resource "aws_glue_trigger" "start_on_creation" {
  name     = "${var.prefix}-trigger-start-job"
  type     = "ON_DEMAND"                           # Esse tipo permite execução manual (não automática)

  actions {
    job_name = aws_glue_job.glue_job.name
  }

  depends_on = [aws_glue_job.glue_job]             # Garante que só roda após o Glue Job estar criado
}

# ===============================
# Glue Job: Data Quality
# ===============================
resource "aws_glue_job" "glue_job_dataquality" {
  name              = "dataquality"                               # Nome do segundo Glue Job
  role_arn          = aws_iam_role.glue_job.arn
  glue_version      = "5.0"
  worker_type       = "G.1X"
  number_of_workers = 2
  timeout           = 5

  command {
    script_location = "s3://${local.glue_bucket}/dataquality/script_data_quality.py"  # Script de data quality
    python_version  = "3"
  }

  default_arguments = {
    "--additional-python-modules"           = "delta-spark==1.0.0"
    "--extra-jars"                          = "s3://${var.prefix}-${var.bucket_names[5]}/jars/delta-core_2.12-1.0.0.jar"
    "--conf spark.delta.logStore.class"     = "org.apache.spark.sql.delta.storage.S3SingleDriverLogStore"
    "--conf spark.sql.extensions"           = "io.delta.sql.DeltaSparkSessionExtension"
  }
}

# ===============================
# Glue Catalog Databases
# ===============================

# Database para camada Silver
resource "aws_glue_catalog_database" "silver" {
  name = "db_silver"
}

# Database para camada Bronze
resource "aws_glue_catalog_database" "bronze" {
  name = "db_bronze"
}

# ===============================
# Glue Crawler: Bronze
# ===============================
resource "aws_glue_crawler" "bronze_crawler" {
  name          = "${var.prefix}-bronze-crawler"
  role          = aws_iam_role.glue_job.arn
  database_name = aws_glue_catalog_database.bronze.name
  description   = "Crawler para camada bronze do cliente"

  s3_target {
    path = "s3://etlproj-bronze/tabela_cliente_landing/"  # Caminho onde os dados bronze serão armazenados
  }

  schema_change_policy {
    update_behavior = "UPDATE_IN_DATABASE"
    delete_behavior = "LOG"
  }

  configuration = jsonencode({
    Version = 1.0,
    CrawlerOutput = {
      Partitions = {
        AddOrUpdateBehavior = "InheritFromTable"  # Inherda o particionamento do arquivo
      }
    }
  })

  tags = local.common_tags
}

# ===============================
# Glue Crawler: Silver
# ===============================
resource "aws_glue_crawler" "silver_crawler" {
  name          = "${var.prefix}-silver-crawler"
  role          = aws_iam_role.glue_job.arn
  database_name = aws_glue_catalog_database.silver.name
  description   = "Crawler para camada silver do cliente"

  s3_target {
    path = "s3://etlproj-silver/tb_cliente/"       # Caminho para a camada silver
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
