variable "bucket_name" {
  default = null
}

variable "bucket_owner_id" {
  default = null
}

variable "create_trigger" {
  type = bool
  default = false
}

variable "rightscale_org_id" {}

variable "rightscale_bill_connect_id" {}

variable "rightscale_token_url" {}

variable "rightscale_base_upload_url" {}

variable "kms_secret_path" {
  default = null
}

variable "rightscale_api_version" {
}
