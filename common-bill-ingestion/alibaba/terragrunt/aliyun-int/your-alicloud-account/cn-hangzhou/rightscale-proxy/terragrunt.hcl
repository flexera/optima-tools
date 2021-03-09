terraform {
  source = "../../../../../terraform//rightscale-proxy"
}

include {
  path = find_in_parent_folders()
}

inputs =  {
  create_trigger = true
  bucket_name = "[YOUR_EXPORT_BUCKET]"
  bucket_owner_id = "[YOUR_EXPORT_BUCKET_ACCOUNT_ID]"

  rightscale_token_url = "https://us-4.rightscale.com/api/oauth2"
  rightscale_base_upload_url = "https://optima-bill-upload-front.indigo.rightscale.com/optima/orgs"
  rightscale_org_id = "25638"
  rightscale_bill_connect_id = "cbi-oi-alibaba-1"
  rightscale_api_version = "1.5"
  
  #TODO
  kms_secret_path = "/kms_secret_path"
}
