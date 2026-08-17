resource "azurerm_role_assignment" "identity_storage_access" {
  principal_id         = data.azurerm_user_assigned_identity.integration_identity.principal_id
  role_definition_name = "Storage Blob Data Contributor"
  scope                = module.storage.storage_id
  depends_on = [
    module.storage
  ]
}

resource "azurerm_role_assignment" "identity_storage_access_dbx" {
  principal_id         = module.databricks.unity_catalog_access_connector_principal_id
  role_definition_name = "Storage Blob Data Contributor"
  scope                = module.storage.storage_id
  depends_on = [
    module.storage
  ]
}

resource "azurerm_role_assignment" "kv_secrets_user" {
  scope                = data.azurerm_key_vault.kv.id
  role_definition_name = "Key Vault Secrets User"
  principal_id         = module.databricks.unity_catalog_access_connector_principal_id
}

