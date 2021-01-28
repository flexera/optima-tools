# Configure Terragrunt to automatically store tfstate files in an S3 bucket
remote_state {
  backend = "oss"

  config = {
      bucket  = "[YOUR_STATE_BUCKET]"
      region  = "eu-central-1"
      prefix  = ""
      key     = "${path_relative_to_include()}"
      encrypt = true
  }
}

terraform {
  extra_arguments "common_vars" {
    commands = [
      "apply",
      "destroy",
      "plan",
      "import",
      "push",
      "refresh"
    ]

    arguments = [
      "-no-color"
    ]
  }
}

generate "provider" {
  path = "backend.tf"
  if_exists = "overwrite_terragrunt"
  contents = <<EOF
terraform {
  backend "oss" {}
}

provider "alicloud" {
  region = var.region
  assume_role {
    role_arn           = var.provider_role_arn
  }
}

variable "region" {
  description = "Alibaba region"
  type        = string
}


variable "provider_role_arn" {
  description = "Provider role arn"
  type        = string
}
EOF
}

# Configure root level variables that all resources can inherit. This is especially helpful with multi-account configs
# where terraform_remote_state data sources are placed directly into the modules.
inputs =  merge(
{
  project = "infra"

  tags = {
    Project = "infra"
    TeamName = "infra"
    CreationMethod = "terraform"
    Owner = ""
  }
},
yamldecode(file("${find_in_parent_folders("account.yaml", find_in_parent_folders("empty.yaml"))}")),
yamldecode(file("${find_in_parent_folders("region.yaml", find_in_parent_folders("empty.yaml"))}"))

)
