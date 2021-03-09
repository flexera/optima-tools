locals {
  prefix = "infra-rightscale-poc"
  bucket_name = var.bucket_name!=null?var.bucket_name:"flexera-optima-cn-${data.alicloud_account.current.id}-${local.prefix}"
}
