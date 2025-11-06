# Terraform

This document provides a detailed reference for the Terraform configuration that defines the project's infrastructure. [Terraform](https://developer.hashicorp.com/terraform) is used to implement the principle of Infrastructure as Code (IaC), which allows us to manage and provision our infrastructure through code and configuration files.

The core Terraform configuration is located in the [`/terraform` directory](https://github.com/Office-of-Digital-Services/cdt-ods-disaster-recovery/tree/main/terraform).

The primary goal of this configuration is to create a secure, repeatable, and modular infrastructure on Microsoft Azure. The [Terraform Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs) defines the necessary resource blocks to enable this configuration in Terraform.

## Workspaces

The project uses [Terraform Workspaces](https://developer.hashicorp.com/terraform/cli/workspaces) to manage and deploy to multiple environments from the same codebase. Each workspace corresponds to a distinct environment and has its own state file, which prevents environments from interfering with each other.

The workspaces are:

- **`dev`**: Corresponds to the `dev` environment.
- **`test`**: Corresponds to the `test` environment.
- **`default`**: Corresponds to the `prod` environment.

While each workspace is distinct with its own state file, all 3 state files are stored in the `prod` environment.

The selection of the workspace is automated in the Azure DevOps pipeline. The `terraform/pipeline/workspace.py` script inspects the Git branch or tag that triggered the pipeline to determine which workspace to use. For example, a pull request to `main` will deploy to the `dev` environment, while a release tag will deploy to `test` or `prod`.

For more details on each Azure environment, see the [Environments section in the Infrastructure reference](./infrastructure.md#environments).

## Directory structure

The `/terraform` directory is organized to separate concerns between the root configuration, reusable modules, and Azure DevOps pipeline logic.

```text
/terraform
├── alerts.tf
├── azure-pipelines.yml
├── main.tf
├── modules.tf
├── security.tf
├── variables.tf
├── modules/
│   ├── application/
│   ├── database/
│   ├── email/
│   ├── key_vault/
│   ├── monitoring/
│   ├── network/
│   └── storage/
├── pipeline/
│   ├── deploy.yml
│   ├── tags.py
│   └── workspace.py
└── secrets/
    ├── file.sh
    ├── read.sh
    └── value.sh
```

### Root files

- `main.tf`: The entrypoint for the root module. It configures the Azure provider and backend state storage.
- `variables.tf`: Defines input variables for the root module, such as subscription and object IDs.
- `modules.tf`: The central wiring file that instantiates all the core modules from the `modules/` directory and connects their inputs and outputs.
- `security.tf`: Contains centralized security configurations, such as Network Security Group (NSG) rules and Key Vault access policies that span across multiple modules.
- `alerts.tf`: Defines monitoring alerts, such as the Application Insights error alert.

### `modules/`

This directory contains reusable, self-contained modules for different parts of the infrastructure. Each subdirectory is a separate Terraform module.

### `pipeline/`

Contains the definitions for the Azure DevOps pipeline that automates `terraform plan` and `terraform apply`.

### `secrets/`

Includes helper scripts for manually reading and writing secrets to Azure Key Vault.

## Root modules

The `.tf` files in the root of the `/terraform` directory define the core configuration and orchestrate the modules.

### `main.tf`

!!! abstract "Source"

    [`terraform/main.tf`](https://github.com/Office-of-Digital-Services/cdt-ods-disaster-recovery/tree/main/terraform/main.tf)

This file is the primary entrypoint for the Terraform configuration. It is responsible for:

- **Provider Configuration**: It declares the required providers, `azurerm` and `random`, and their versions.
- **Backend Configuration**: It configures the `azurerm` backend, which tells Terraform to store its state file in an Azure Storage Account. This is critical for a team environment to ensure that the state is shared and locked to prevent concurrent modifications.
- **Core Data Lookups**: It uses data sources to fetch information about the Azure environment at runtime, such as the current client configuration (`azurerm_client_config`) and the main resource group (`azurerm_resource_group`).

### `modules.tf`

!!! abstract "Source"

    [`terraform/modules.tf`](https://github.com/Office-of-Digital-Services/cdt-ods-disaster-recovery/tree/main/terraform/modules.tf)

This file acts as the central nervous system for the infrastructure, connecting all the individual modules defined in the `/terraform/modules` directory.

- **Orchestration**: It instantiates each core module (`network`, `monitoring`, `database`, etc.).
- **Wiring**: It passes the outputs from one module as inputs to another. This creates a dependency graph and ensures resources are created in the correct order. For example, the network module's subnet IDs are passed to the application and database modules.
- **Consistent Naming**: It defines a `locals` block that establishes a consistent naming convention for resources across all modules, based on the environment.

Here is an example of how `modules.tf` wires the `monitoring` and `network` modules together:

```terraform
module "monitoring" {
  source                        = "./modules/monitoring"
  # ... other variables
}

module "network" {
  source                     = "./modules/network"
  log_analytics_workspace_id = module.monitoring.log_analytics_workspace_id
  # ... other variables
}
```

### `security.tf`

!!! abstract "Source"

    [`terraform/security.tf`](https://github.com/Office-of-Digital-Services/cdt-ods-disaster-recovery/tree/main/terraform/security.tf)

This file centralizes security-related configurations that span across multiple modules. This separation of concerns makes it easier to manage and audit security settings. Its responsibilities include:

- **Key Vault Access Policies**: It creates `azurerm_key_vault_access_policy` resources to grant the managed identities of the application's container apps (`web`, `worker`, `functions`) the necessary permissions to read secrets from Key Vault.
- **Network Security Group (NSG) Rules**: It defines the specific `azurerm_network_security_rule` resources that allow or deny traffic between the different subnets. For example, it contains rules to allow the application subnet to communicate with the database subnet on the correct port.

### `alerts.tf`

!!! abstract "Source"

    [`terraform/alerts.tf`](https://github.com/Office-of-Digital-Services/cdt-ods-disaster-recovery/tree/main/terraform/alerts.tf)

This file is dedicated to defining monitoring alerts for the application. It creates an `azurerm_monitor_scheduled_query_rules_alert_v2` resource that:

- Runs a query against Application Insights logs on a schedule (e.g., every 5 minutes).
- The query checks for exceptions or high-severity traces.
- If the query returns any results, it triggers an alert that notifies the team via the action group configured in the `monitoring` module.

## Core modules (`terraform/modules/*`)

The `terraform/modules/` directory contains a set of reusable modules, each responsible for a specific piece of the infrastructure. This modular approach makes the configuration easier to manage and reason about.

The modules below are reflected in more-or-less "dependency" order, e.g. we need the network to exist before we can create a database, and that has to exist before we can create the apps.

### `network`

!!! abstract "Source"

    [`terraform/modules/network/`](https://github.com/Office-of-Digital-Services/cdt-ods-disaster-recovery/tree/main/terraform/modules/network)

Creates the foundational networking resources for the application.

**Key resources**:

- `azurerm_virtual_network`: The main VNet for the environment.
- `azurerm_subnet`: Creates multiple subnets for different components (e.g., `public`, `worker`, `db`, `key_vault`).
- `azurerm_nat_gateway`: Provides outbound internet access for resources in the private subnets.
- `azurerm_network_security_group`: Defines NSGs to control traffic flow.

### `monitoring`

!!! abstract "Source"

    [`terraform/modules/monitoring/`](https://github.com/Office-of-Digital-Services/cdt-ods-disaster-recovery/tree/main/terraform/modules/monitoring)

Sets up the shared monitoring, logging, and alerting infrastructure.

**Key resources**:

- `azurerm_log_analytics_workspace`: The central workspace for collecting logs and metrics.
- `azurerm_application_insights`: The Application Performance Management (APM) service for the application.
- `azurerm_monitor_action_group`: Defines a group of actions (like sending an email or calling a webhook) to take when an alert is triggered.

### `key_vault`

!!! abstract "Source"

    [`terraform/modules/key_vault/`](https://github.com/Office-of-Digital-Services/cdt-ods-disaster-recovery/tree/main/terraform/modules/key_vault)

Deploys a secure and private Azure Key Vault for managing secrets.

**Key resources**:

- `azurerm_key_vault`: The Key Vault instance.
- `azurerm_private_endpoint`: Exposes the Key Vault on a private IP address within the VNet.
- `azurerm_key_vault_access_policy`: Base policies for administrative groups.

### `database`

!!! abstract "Source"

    [`terraform/modules/database/`](https://github.com/Office-of-Digital-Services/cdt-ods-disaster-recovery/tree/main/terraform/modules/database)

Deploys the PostgreSQL database for the application.

**Key resources**:

- `azurerm_postgresql_flexible_server`: The managed PostgreSQL server.
- `azurerm_private_endpoint`: Exposes the database on a private IP address within the VNet.
- `azurerm_key_vault_secret`: Creates a secret in Key Vault for the generated database password.

### `storage`

!!! abstract "Source"

    [`terraform/modules/storage/`](https://github.com/Office-of-Digital-Services/cdt-ods-disaster-recovery/tree/main/terraform/modules/storage)

Creates the Azure Storage Account and file shares required by the application.

**Key resources**:

- `azurerm_storage_account`: The main storage account.
- `azurerm_storage_share`: Creates file shares for `config` and `requests`.
- `azurerm_private_endpoint`: Exposes the storage account's blob and file services on private IP addresses.

### `email`

!!! abstract "Source"

    [`terraform/modules/email/`](https://github.com/Office-of-Digital-Services/cdt-ods-disaster-recovery/tree/main/terraform/modules/email)

Configures the Azure Communication Service for sending emails.

**Key resources**:

- `azurerm_communication_service`: The core communication service.
- `azurerm_email_communication_service`: The email-specific service.
- `azurerm_email_communication_service_domain`: Configures the sending domain (`AzureManaged` for non-prod, `CustomerManaged` for prod).

### `application`

!!! abstract "Source"

    [`terraform/modules/application/`](https://github.com/Office-of-Digital-Services/cdt-ods-disaster-recovery/tree/main/terraform/modules/application)

Deploys the application components. This is the most complex module, bringing together many of the resources from other modules.

**Key resources**:

- `azurerm_container_app_environment`: Creates two environments, one for the public-facing `web` app and another for the internal `worker` and `functions` apps.
- `azurerm_container_app`: Deploys the `web`, `worker`, and `functions` container apps.
- `azurerm_user_assigned_identity`: Creates managed identities for each container app to enable secure access to other Azure resources (like Key Vault).
- `azurerm_key_vault_secret`: Creates application-specific secrets in Key Vault.

## Managing secrets

A robust secret management strategy is in place to handle sensitive information like passwords, API keys, and connection strings.

### Azure Key Vault

The primary storage for all secrets is Azure Key Vault. This provides a secure, centralized repository with access control and auditing.

### Terraform and Key Vault

- Terraform is configured to create secrets in Key Vault (e.g., generated database passwords).
- The application container apps are configured to read secrets directly from Key Vault using their managed identities. The `secrets` blocks in the `azurerm_container_app` resources and the associated `azurerm_key_vault_access_policy` resources manage this.

### Manual secret management

For secrets that are not generated by Terraform (e.g., third-party API keys), the `terraform/secrets/` directory contains helper scripts:

- `value.sh`: Sets a secret from a string value.
- `file.sh`: Sets a secret from the contents of a file.

### Local development

For local development, the `terraform.tfvars` file is used to provide secrets and other variables to Terraform. This file is explicitly ignored by Git (via `.gitignore`) to prevent accidental check-in of sensitive information. A `terraform.tfvars.sample` file is provided as a template.

This approach ensures that secrets are not hard-coded in the codebase and are securely managed throughout the development and deployment lifecycle.

## Infrastructure pipeline

The pipeline is triggered by PRs against the `main` branch and by the GitHub Actions [`deploy` workflow](https://github.com/Office-of-Digital-Services/cdt-ods-disaster-recovery/blob/main/.github/workflows/deploy.yml). The key characteristics of the pipeline are:

### `terraform plan`

For pull requests targeting the `main` branch, the pipeline runs a `terraform plan` to show a preview of the changes. This allows for a review of the potential impact before any changes are applied.

### `terraform apply`

The `terraform apply` command is run when:

- A pull request is merged into the `main` branch (deploying to the `dev` environment).
- A release candidate tag (e.g., `2025.10.1-rc1`) is pushed (deploying to the `test` environment).
- A release tag (e.g., `2025.10.1`) is pushed (deploying to the `prod` environment).

### Modular pipeline

The core deployment logic is encapsulated in the `terraform/pipeline/deploy.yml` template, which is called by the main pipeline. This template handles installing Terraform, setting up authentication, and running the Terraform commands.

### Dynamic configuration

- The `terraform/pipeline/workspace.py` script dynamically determines the correct Terraform workspace (`dev`, `test`, or `default`) to use based on the source branch or tag.
- The `terraform/pipeline/tags.py` script determines the container image tag to be deployed.

While the primary CI/CD automation for this project is done through GitHub Actions, we use an Azure Pipeline for a couple of reasons:

- Easier authentication with the Azure API using a service connnection
- Log output is hidden, avoiding accidentally leaking secrets
