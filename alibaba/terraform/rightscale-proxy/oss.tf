resource "alicloud_oss_bucket" "bucket" {
  count = var.bucket_name!=null?0:1

  bucket = local.bucket_name
  acl    = "private"
}
