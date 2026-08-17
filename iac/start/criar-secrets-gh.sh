#!/bin/bash

# Lista todos os Key Vaults deletados na localização
vaults=$(az keyvault list-deleted --query "[].name" -o tsv)

for vault in $vaults; do
  echo "Purging Key Vault: $vault"
  az keyvault purge --name $vault
done

set -e

REPO="marciodelima/case-datamaster_engdados"

echo "Terraform apply..."
terraform init -upgrade
terraform apply -auto-approve

echo "Outputs do Terraform..."
AZURE_CLIENT_ID=$(terraform output -raw azure_client_id)
AZURE_CLIENT_SECRET=$(terraform output -raw azure_client_secret)
AZURE_TENANT_ID=$(terraform output -raw azure_tenant_id)
AZURE_CREDENTIALS=$(terraform output -raw azure_credentials_json)
MANAGED_IDENTITY_NAME=$(terraform output -raw azure_integration_identity)
RSG_NAME=$(terraform output -raw rsg_name)
IAC_NAME_STORAGE=$(terraform output -raw iac_name_storage)

echo "Criando secrets no GitHub..."
gh secret set RSG --body "$RSG_NAME" --repo $REPO
gh secret set MANAGED_IDENTITY_NAME --body "$MANAGED_IDENTITY_NAME" --repo $REPO
gh secret set IAC_NAME_STORAGE --body "$IAC_NAME_STORAGE" --repo $REPO

gh secret set AZURE_CLIENT_ID     --body "$AZURE_CLIENT_ID"     --repo $REPO
gh secret set AZURE_CLIENT_SECRET --body "$AZURE_CLIENT_SECRET" --repo $REPO
gh secret set AZURE_TENANT_ID     --body "$AZURE_TENANT_ID"     --repo $REPO
gh secret set AZURE_CREDENTIALS   --body "$AZURE_CREDENTIALS"   --repo $REPO

echo "Secrets criadas com sucesso!"
