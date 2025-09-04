# Making infrastructure changes via Terraform

## Setup for local development

1. [Get access to the Azure account through the DevSecOps team.](../../reference/infrastructure/#getting-started)
1. Install dependencies:

   - [Azure CLI](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
   - [Terraform](https://www.terraform.io/downloads) - see exact version in [`deploy.yml`](https://github.com/Office-of-Digital-Services/cdt-ods-disaster-recovery/blob/main/terraform/pipeline/deploy.yml)

1. [Authenticate using the Azure CLI](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/guides/azure_cli).

   ```sh
   az login
   ```

1. Outside the [dev container](../../guides/development), navigate to the [`terraform/`](https://github.com/Office-of-Digital-Services/cdt-ods-disaster-recovery/tree/main/terraform) directory.
1. [Initialize Terraform.](https://www.terraform.io/cli/commands/init) You can also use this script later to switch between [environments](../../reference/infrastructure/#environments).

   ```sh
   ./init.sh <env>
   ```

1. Create a local `terraform.tfvars` file (ignored by git) from the sample; fill in the `*_OBJECT_ID` variables with values from the Azure Pipeline definition.

## Development process

When configuration changes to infrastructure resources are needed, they should be made to the resource definitions in Terraform and submitted via pull request.

1. Make changes to Terraform files.
1. Preview the changes, as necessary.

   ```sh
   terraform plan
   ```

1. [Submit the changes via pull request.](../commits-branches-merging)

!!! info "Azure tags"
   For Azure resources, you need to [ignore changes](https://www.terraform.io/language/meta-arguments/lifecycle#ignore_changes) to tags, since they are [automatically created by an Azure Policy managed by CDT](https://docs.microsoft.com/en-us/azure/azure-resource-manager/management/tag-policies).

    ```hcl
    lifecycle {
        ignore_changes = [tags]
    }
    ```
