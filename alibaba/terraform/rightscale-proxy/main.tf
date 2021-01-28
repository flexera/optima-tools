
data "alicloud_account" "current" {
}

data "alicloud_regions" "current" {
  current = true
}

resource "alicloud_log_project" "default" {
  name        = "${local.prefix}-${data.alicloud_account.current.id}"
  description = local.prefix
}

resource "alicloud_log_store" "default" {
  project          = alicloud_log_project.default.name
  name             = local.prefix
  retention_period = "3000"
  shard_count      = 1
}
resource "alicloud_fc_service" "default" {
  name        = local.prefix
  description = local.prefix

  log_config {
    project  = alicloud_log_project.default.name
    logstore = alicloud_log_store.default.name
  }
  role       = alicloud_ram_role.default.arn
  depends_on = [alicloud_ram_role_policy_attachment.default]
}

resource "alicloud_ram_role" "default" {
  name = local.prefix
  document = <<EOF
        {
          "Statement": [
            {
              "Action": "sts:AssumeRole",
              "Effect": "Allow",
              "Principal": {
                "Service": [
                  "fc.aliyuncs.com"
                ]
              }
            }
          ],
          "Version": "1"
        }
    EOF
  description = local.prefix
  force       = true
}

resource "alicloud_ram_role_policy_attachment" "default" {
  role_name   = alicloud_ram_role.default.name
  policy_name = "AliyunLogFullAccess"
  policy_type = "System"
}

resource "alicloud_ram_role_policy_attachment" "full" {
  role_name   = alicloud_ram_role.default.name
  policy_name = "AdministratorAccess"
  policy_type = "System"
}

data "archive_file" "zip" {
  type        = "zip"
  source_dir= "${path.module}/resources/src"
  output_path = "function.zip"
}

resource "alicloud_fc_function" "this" {
  service     = alicloud_fc_service.default.name
  name        = local.prefix
  description = local.prefix

  timeout = "60"
  filename = "function.zip"
  memory_size = "512"
  runtime     = "python3"
  handler     = "main.handler"
  code_checksum = data.archive_file.zip.output_base64sha256
  environment_variables = {
    BUCKET_NAME = local.bucket_name
    BUCKET_OWNER_ID = var.bucket_owner_id
    ACCOUNT_ID = data.alicloud_account.current.id
    REGION = data.alicloud_regions.current.regions[0].id
    RIGHTSCALE_BILL_CONNECT_ID = var.rightscale_bill_connect_id
    RIGHTSCALE_ORG_ID = var.rightscale_org_id
    RIGHTSCALE_API_VERSION = var.rightscale_api_version
    RIGHTSCALE_TOKEN_URL = var.rightscale_token_url
    RIGHTSCALE_BASE_UPLOAD_URL = var.rightscale_base_upload_url
  }
}

resource "alicloud_ram_role" "trigger" {
  count = var.create_trigger?1:0

  name     = "${local.prefix}-trigger"
  document = <<EOF
  {
    "Statement": [
      {
        "Action": "sts:AssumeRole",
        "Effect": "Allow",
        "Principal": {
          "Service": [
            "oss.aliyuncs.com"
          ]
        }
      }
    ],
    "Version": "1"
  }
  EOF
  description = "Rightscale bucket trigger"
  force = true
}

resource "alicloud_ram_policy" "trigger" {
  count = var.create_trigger?1:0

  name = "${local.prefix}-trigger"
  document = <<EOF
    {
        "Version": "1",
        "Statement": [
        {
            "Action": [
            "fc:InvokeFunction"
            ],
        "Resource": [
            "acs:fc:*:*:services/${local.prefix}/functions/*",
			"acs:fc:*:*:services/${local.prefix}/functions/*"
        ],
        "Effect": "Allow"
        }
        ]
    }
    EOF
  description = "Rightscale bucket trigger"
  force = true
}
resource "alicloud_ram_role_policy_attachment" "trigger" {
  count = var.create_trigger?1:0

  role_name = alicloud_ram_role.trigger.0.name
  policy_name = alicloud_ram_policy.trigger.0.name
  policy_type = "Custom"
}

resource "alicloud_fc_trigger" "default" {
  count = var.create_trigger?1:0

  depends_on = [alicloud_ram_role_policy_attachment.trigger]

  service = alicloud_fc_service.default.name
  function = alicloud_fc_function.this.name
  name = local.prefix
  role = alicloud_ram_role.trigger.0.arn
  source_arn = "acs:oss:${data.alicloud_regions.current.regions[0].id}:${data.alicloud_account.current.id}:${local.bucket_name}"
  type = "oss"

  config = <<EOF
    {
        "events": ["oss:ObjectCreated:CompleteMultipartUpload", "oss:ObjectCreated:PostObject","oss:ObjectCreated:PutObject"]
    }
  EOF
}

