# Criação de múltiplos buckets S3, com base na lista var.bucket_names
resource "aws_s3_bucket" "buckets" {
  count  = length(var.bucket_names)
  bucket = "${var.prefix}-${var.bucket_names[count.index]}"  # Nome do bucket com prefixo padrão

  force_destroy = true  # Permite excluir o bucket mesmo se ele tiver arquivos dentro
  tags = local.common_tags  # Tags padronizadas aplicadas aos recursos
}

# Upload do CSV de clientes para a Landing Zone (primeiro bucket da lista)
resource "aws_s3_object" "upload_csv_landing" {
  bucket = "${var.prefix}-${var.bucket_names[0]}"  # Bucket da landing zone
  key    = "arquivo/clientes_sinteticos.csv"       # Caminho dentro do bucket
  source = "../datasets/clientes_sinteticos.csv"   # Caminho local do arquivo
  content_type = "text/csv"                        # Tipo do conteúdo para o S3

  tags = local.common_tags
}

# Upload do script de ETL para o bucket de scripts (índice 5 da lista)
resource "aws_s3_object" "upload_script_glue" {
  bucket = "${var.prefix}-${var.bucket_names[5]}" 
  key    = "job/glue-etl.py"
  source = "../app/job/glue-etl.py"
  content_type = "python"

  tags = local.common_tags
}

# Upload do arquivo requirements.txt para a DAG do Airflow
resource "aws_s3_object" "upload_requirements_airflow" {
  bucket = "${var.prefix}-${var.bucket_names[6]}"
  key    = "etlproj-airflow-pipeline-clientes/requirements.txt"
  source = "../requirements.txt" 
  content_type = "txt"

  tags = local.common_tags
}

# Upload da DAG do Airflow
resource "aws_s3_object" "upload_dag_airflow" {
  bucket = "${var.prefix}-${var.bucket_names[6]}"
  key    = "etlproj-airflow-pipeline-clientes/dags/dag_pipeline_clientes.py" 
  source = "../airflow/dags/dag_pipeline_clientes.py"
  content_type = "python"

  tags = local.common_tags
}

# Upload do script de data quality
resource "aws_s3_object" "upload_script_dataquality" {
  bucket = "${var.prefix}-${var.bucket_names[5]}"
  key    = "dataquality/script_data_quality.py"
  source = "../dataquality/script_data_quality.py"
  content_type = "python"

  tags = local.common_tags
}

# Upload da dependência .jar para suporte ao Delta Lake
resource "aws_s3_object" "upload_jar_delta" {
  bucket = "${var.prefix}-${var.bucket_names[5]}"
  key    = "jars/delta-core_2.12-1.0.0.jar"
  source = "../app/jars/delta-core_2.12-1.0.0.jar"
  content_type = "jar"

  tags = local.common_tags
}

# Grupo de logs do CloudWatch para monitorar os jobs do Glue
resource "aws_cloudwatch_log_group" "glue_log_group" {
  name              = "/aws-glue/jobs/${var.prefix}-logs"
  retention_in_days = 14  # Manter logs por 14 dias

  tags = local.common_tags
}

# Configuração de criptografia padrão para todos os buckets S3
resource "aws_s3_bucket_server_side_encryption_configuration" "bucket_sse" {
  count  = length(var.bucket_names)
  bucket = "${var.prefix}-${var.bucket_names[count.index]}"

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"  
    }
  }

  depends_on = [
    aws_s3_bucket.buckets  # Garantir que os buckets existam antes
  ]
}

# Bloqueio de acesso público nos buckets
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
