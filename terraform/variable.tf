# ================================
# Variáveis de Configuração
# ================================

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

# ================================
# Definições Locais
# ================================

locals {
  # Nome do bucket onde os scripts do Glue estão armazenados
  glue_bucket = "${var.prefix}-${var.bucket_names[5]}"
  
  prefix = var.prefix

  # Tags padrão aplicadas a todos os recursos (útil para rastreabilidade e custo)
  common_tags = {
    projeto = "teste_eng_dados"
  }
}

# ================================
# Lista dos Buckets S3 utilizados no projeto
# ================================
variable "bucket_names" {
  description = "s3 bucket names"
  type        = list(string)
  default = [
    "landing-zone",                # Armazena o arquivo inicial (origem dos dados)
    "bronze",                      # Camada bronze do Data Lake
    "silver",                      # Camada silver do Data Lake
    "gold",                        # Camada gold (não usada diretamente neste projeto)
    "logs",                        # Usada para logs
    "aws-glue-scripts",           # Armazena scripts do Glue e .jar do Delta
    "airflow-pipeline-clientes"   # Contém artefatos do Airflow (requirements, dags)
  ]
}

# ================================
# IAM Role para Glue Jobs
# ================================
variable "glue_job_role_arn" {
  description = "The ARN of the IAM role associated with this job."
  default     = null
}

# ================================
# Credenciais AWS
# ================================
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
