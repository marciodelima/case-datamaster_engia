#!/bin/bash
set -e

echo "Instalando Databricks CLI e jq..."
sudo apt-get install -y jq || true
 curl -L https://github.com/databricks/cli/releases/download/v0.271.0/databricks_cli_0.271.0_linux_amd64.tar.gz -o databricks.tar.gz
 tar -xvzf databricks.tar.gz
 sudo mv databricks /usr/local/bin/

echo "Gerando token via Azure CLI..."
token_response=$(az account get-access-token --resource "$DATABRICKS_RESOURCE")
export DATABRICKS_AAD_TOKEN=$(jq -r .accessToken <<< "$token_response")
export DATABRICKS_HOST="https://${WORKSPACE_URL}"

echo "Configurando Databricks CLI..."
cat > ~/.databrickscfg <<EOF
[DEFAULT]
host = $DATABRICKS_HOST
token = $DATABRICKS_AAD_TOKEN
EOF

echo "Gerando token bootstrap para automações..."
BOOTSTRAP_TOKEN=$(databricks tokens create --comment "Bootstrap token" --lifetime-seconds 1209600 | jq -r ".token_value")

cat > ~/.databrickscfg <<EOF
[DEFAULT]
host = $DATABRICKS_HOST
token = $BOOTSTRAP_TOKEN
EOF

echo "Detectando catálogo atual..."
CATALOG_NAME=$(databricks catalogs list --output json | jq -r '.[] | select(.name | startswith("finance")) | .name' | head -n 1)

if [ -z "$CATALOG_NAME" ]; then
  echo "Nenhum catálogo encontrado com prefixo 'finance'. Abortando."
  exit 1
fi

echo "Catalogo detectado: $CATALOG_NAME"
echo "Criando schemas no catálogo..."
for schema in r-inv b-inv s-inv stage g-inv; do
  echo "Criando schema '$schema'..."
  databricks schemas create --json '{
    "name": "'"$schema"'",
    "catalog_name": "'"$CATALOG_NAME"'"
  }' || true
done

echo "Criando policy padrão para clusters..."
cat <<EOF > policy.json
{
  "spark_version": { "type": "fixed", "value": "16.4.x-scala2.12" },
  "node_type_id": { "type": "fixed", "value": "Standard_D4pds_v6" },
  "autotermination_minutes": { "type": "fixed", "value": 20 },
  "is_single_node": { "type": "fixed", "value": true },
  "enable_elastic_disk": { "type": "fixed", "value": true }
}
EOF
databricks cluster-policies create --name "inv-policy" --definition "$(cat policy.json)" || echo "Policy já existe ou falhou."

echo "Criando cluster SQL para consultas..."
databricks clusters create --json '{
  "cluster_name": "finance-sql",
  "spark_version": "16.4.x-scala2.12",
  "node_type_id": "Standard_D4pds_v6",
  "num_workers": 0,
  "runtime_engine": "STANDARD",
  "data_security_mode": "DATA_SECURITY_MODE_AUTO",
  "kind": "CLASSIC_PREVIEW",
  "policy_id": "'"$(databricks cluster-policies list -o json | jq -r '.[] | select(.name=="inv-policy") | .policy_id')"'"
}' || echo "Cluster já existe ou falhou."

echo "Salvando token bootstrap no Azure Key Vault..."
az keyvault secret set --vault-name "$KEYVAULT_NAME" --name "databricks-aad-token" --value "$DATABRICKS_AAD_TOKEN"
az keyvault secret set --vault-name "$KEYVAULT_NAME" --name "databricks-bootstrap-token" --value "$BOOTSTRAP_TOKEN"

echo "Provisionamento Databricks concluído com sucesso."
