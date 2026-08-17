resource "azurerm_key_vault" "kv" {
  name                     = var.keyvault_name
  location                 = var.location
  resource_group_name      = var.resource_group_name
  tenant_id                = data.azurerm_client_config.current.tenant_id
  sku_name                 = "standard"
  purge_protection_enabled = false
  depends_on               = [azurerm_resource_group.rsg_datamaster]
}

# Permissões via Access Policy (se o Key Vault estiver com access policies habilitadas)
resource "azurerm_key_vault_access_policy" "databricks_identity" {
  key_vault_id = azurerm_key_vault.kv.id
  tenant_id = data.azurerm_client_config.current.tenant_id
  object_id = data.azurerm_user_assigned_identity.databricks_identity.principal_id
  secret_permissions = [
    "Get",
    "List",
    "Set",
    "Delete"
  ]
  depends_on         = [azurerm_databricks_workspace.dbx]
}

resource "azurerm_key_vault_access_policy" "access_connector" {
  key_vault_id = azurerm_key_vault.kv.id
  tenant_id = data.azurerm_client_config.current.tenant_id
  object_id = data.azurerm_databricks_access_connector.unity_catalog.identity[0].principal_id

  secret_permissions = [
    "Get",
    "List"
  ]
  depends_on         = [azurerm_databricks_workspace.dbx]
}

