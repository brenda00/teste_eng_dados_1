# ==================================================
# IAM Role: glue_job
# Cria uma role que o Glue Job usará para executar
# ==================================================
resource "aws_iam_role" "glue_job" {
  name        = "${local.prefix}-glue-job-role"           # Nome da role
  path        = "/"                                       # Caminho padrão
  description = "Provides write permissions to CloudWatch Logs and S3 Full Access"

  # Política de trust (quem pode assumir essa role) – normalmente, serviço glue.amazonaws.com
  assume_role_policy = file("./permissions/Role_GlueJobs.json")
}

# ==================================================
# IAM Policy: glue_job
# Cria uma política customizada para permitir acesso a S3 e CloudWatch
# ==================================================
resource "aws_iam_policy" "glue_job" {
  name        = "${local.prefix}-glue-job-policy"
  path        = "/"
  description = "Provides write permissions to CloudWatch Logs and S3 Full Access"

  # Define as permissões da policy (acesso ao S3, logs, etc.)
  policy = file("./permissions/Policy_GlueJobs.json")
}

# ==================================================
# Vincula a policy personalizada à role do Glue
# ==================================================
resource "aws_iam_role_policy_attachment" "glue_job" {
  role       = aws_iam_role.glue_job.name
  policy_arn = aws_iam_policy.glue_job.arn
}

# ==================================================
# IAM Policy extra para garantir que o Glue consiga gravar no CloudWatch e fazer PassRole
# ==================================================
resource "aws_iam_policy" "glue_logging" {
  name = "${var.prefix}-glue-logging-policy"

  # Define diretamente no Terraform a política de logging + permissão PassRole
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",      # Criar grupos de log
          "logs:CreateLogStream",     # Criar streams
          "logs:PutLogEvents"         # Escrever logs
        ],
        Resource = "*",
        Effect   = "Allow"
      },
      {
        "Sid": "AllowPassRoleToSelf",
        "Effect": "Allow",
        "Action": "iam:PassRole",     # Permite que o Glue passe a própria role para si
        "Resource": "arn:aws:iam::317634511592:role/etlproj-glue-job-role"
      }
    ]
  })
}

# ==================================================
# Anexa a política de logs à role do Glue
# ==================================================
resource "aws_iam_role_policy_attachment" "glue_logs_attach" {
  role       = aws_iam_role.glue_job.name
  policy_arn = aws_iam_policy.glue_logging.arn
}
