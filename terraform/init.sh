#!/bin/bash
set -e

ENV=$1

if [ $# -ne 1 ]; then
  echo "Usage: $0 <env>"
  exit 1
fi

printf "Intializing Terraform...\n\n"

# automatically inject the subscription ID
PROD_ID=$(az account list --query "[?name == 'CDT/ODI Production'] | [0].id" --output tsv)
terraform init -backend-config="subscription_id=$PROD_ID"

# there's only a single subscription being used
SUBSCRIPTION="CDT/ODI Production"

if [ "$ENV" = "prod" ]; then
  terraform workspace select default
else
  terraform workspace select "$ENV"
fi

echo "Setting the subscription for the Azure CLI..."
az account set --subscription="$SUBSCRIPTION"

echo "Done!"
