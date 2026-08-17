resource "azurerm_cognitive_account" "openai" {
  name                = "openai-ri"
  location            = "eastus2"
  resource_group_name = var.resource_group_name
  kind                = "OpenAI"
  sku_name            = "S0"
}

resource "azurerm_cognitive_deployment" "gpt-4o-mini" {
  name                 = "gpt-4o-mini"
  cognitive_account_id = azurerm_cognitive_account.openai.id

  model {
    format  = "OpenAI"
    name    = "gpt-4o-mini"
    version = "2024-07-18"
  }

  sku {
    name = "Standard"
  }
}

data "azurerm_key_vault" "openai_kv" {
  name                = var.keyvault_name
  resource_group_name = var.resource_group_name
}

# Armazena o endpoint no Key Vault
resource "azurerm_key_vault_secret" "openai_endpoint" {
  name         = "OpenAI-Endpoint"
  value        = azurerm_cognitive_account.openai.endpoint
  key_vault_id = data.azurerm_key_vault.openai_kv.id
}

resource "null_resource" "store_openai_key" {
  depends_on = [azurerm_cognitive_account.openai]

  provisioner "local-exec" {
    command = <<EOT
      OPENAI_KEY=$(az cognitiveservices account keys list \
        --resource-group ${var.resource_group_name} \
        --name ${azurerm_cognitive_account.openai.name} \
        --query key1 -o tsv)

      az keyvault secret set \
        --vault-name ${var.keyvault_name} \
        --name OpenAI-Key \
        --value "$OPENAI_KEY"
    EOT
    interpreter = ["/bin/bash", "-c"]
  }
}

