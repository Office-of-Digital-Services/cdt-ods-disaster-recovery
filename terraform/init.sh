#!/bin/bash
set -e

ENV=$1

if [ $# -ne 1 ]; then
  echo "Usage: $0 <env>"
  exit 1
fi

printf "Intializing Terraform...\n\n"

# there's only a single subscription being used
SUBSCRIPTION="CDT/ODI Production"

# automatically inject the subscription ID
PROD_ID=$(az account list --query "[?name == '$SUBSCRIPTION'] | [0].id" --output tsv)
terraform init -upgrade -backend-config="subscription_id=$PROD_ID"

if [ "$ENV" = "prod" ]; then
  terraform workspace select default
else
  terraform workspace select -or-create "$ENV"
fi

echo "Setting the subscription for the Azure CLI..."
az account set --subscription="$SUBSCRIPTION"

echo "Done!"
