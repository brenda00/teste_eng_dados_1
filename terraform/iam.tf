resource "aws_iam_role" "glue_job" {
  name               = "${local.prefix}-glue-job-role"
  path               = "/"
  description        = "Provides write permissions to CloudWatch Logs and S3 Full Access"
  assume_role_policy = file("./permissions/Role_GlueJobs.json")
}

resource "aws_iam_policy" "glue_job" {
  name        = "${local.prefix}-glue-job-policy"
  path        = "/"
  description = "Provides write permissions to CloudWatch Logs and S3 Full Access"
  policy      = file("./permissions/Policy_GlueJobs.json")
}

resource "aws_iam_role_policy_attachment" "glue_job" {
  role       = aws_iam_role.glue_job.name
  policy_arn = aws_iam_policy.glue_job.arn
}

resource "aws_iam_policy" "glue_logging" {
  name = "${var.prefix}-glue-logging-policy"

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Resource = "*",
        Effect   = "Allow"
      },
      {
        "Sid": "AllowPassRoleToSelf",
        "Effect": "Allow",
        "Action": "iam:PassRole",
        "Resource": "arn:aws:iam::317634511592:role/etlproj-glue-job-role"
      }

    ]
  })
}

resource "aws_iam_role_policy_attachment" "glue_logs_attach" {
  role       = aws_iam_role.glue_job.name
  policy_arn = aws_iam_policy.glue_logging.arn
}

