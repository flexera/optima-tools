provider "oci" {
  tenancy_ocid = var.tenancy_ocid
  user_ocid = var.user_ocid
  fingerprint = var.fingerprint
  private_key_path = var.private_key_path
  region = var.region
}

# Get a list of Availability Domains
data "oci_identity_availability_domains" "ads" {
  compartment_id = var.tenancy_ocid
}

# Output the result
output "show-ads" {
  value = data.oci_identity_availability_domains.ads.availability_domains
}


resource "oci_functions_application" "test_application" {
    #Required
    compartment_id = var.compartment_id
    display_name = var.application_display_name
    subnet_ids = var.application_subnet_ids

    #Optional
    config = var.application_config
    defined_tags = {"Operations.CostCenter"= "42"}
    freeform_tags = {"Department"= "Finance"}
    syslog_url = var.application_syslog_url
}
