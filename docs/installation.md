# Installation

## GitHub Actions (recommended)

<img src="images/pipeline.png">

* deploy Domain Protect in your AWS Organization
* no need to clone or fork Domain Protect
* internal / private deployment repository to protect sensitive information
* uses OpenID Connect - no IAM user with long-lived access keys
* update to latest version of Domain Protect any time by running pipeline

Follow detailed instructions in separate [Domain Protect Deploy](https://github.com/domain-protect/domain-protect-deploy) repository with GitHub Actions deployment workflow

## Atlantis

* For atlantis to work, you can simply create a new stack (folder) in your environment with the name `domain-protect`. You will then make the necessary changes to the `atlantis.yaml` file, so atlantis knows where all the terraform code is from.

Example changes to `atlantis.yaml`:

```yaml
- name: domain-protect-security-audit
  dir: security/domain-protect
  workspace: security-audit
  workflow: security-audit
  terraform_version: 1.3.1
```

* In the `domain-protect` folder, you can just copy the content of `main.tf` file from this repo. For each of the module, make sure you change the source to this repo so you can reuse the module here without having to clone a version of this tool in your environment.

For example, update:

```terraform
module "kms" {
  source  = "./terraform-modules/kms"
  project = var.project
  region  = var.region
}
```

to

```terraform
module "kms" {
  source  =  "git::https://github.com/domain-protect/domain-protect.git//terraform-modules/kms"
  project = var.project
  region  = var.region
}
```

Also, because of the current way the lambda code modules are set up, you will need to copy the contents `scripts/lambda-build` folder with the same path to your `domain-protect` folder. In the end, you will have a structure like this:

* domain-protect
  * main.tf
  * scripts
    * lambda-build
      * create-package-for-each.sh
      * create-package.sh

## Manual installation (not recommended)

* replace the Terraform state S3 bucket fields in the command below as appropriate
* for local testing, duplicate terraform.tfvars.example, rename without the .example suffix
* enter details appropriate to your organization and save
* alternatively enter Terraform variables within your CI/CD pipeline
* deploy development environment for detection only
* default scan schedule for dev environment is 12 hours
```
terraform init -backend-config=bucket=TERRAFORM_STATE_BUCKET -backend-config=key=TERRAFORM_STATE_KEY -backend-config=region=TERRAFORM_STATE_REGION
terraform workspace new dev
terraform plan
terraform apply
```
* deploy production environment for detection and automated takeover
* default scan schedule for prd environment is 60 minutes
```
terraform workspace new prd
terraform plan
terraform apply
```

## adding notifications to extra Slack channels
* add an extra channel to your slack_channels variable list
* add an extra webhook URL or repeat the same webhook URL to your slack_webhook_urls variable list
* apply Terraform

[back to README](../README.md)