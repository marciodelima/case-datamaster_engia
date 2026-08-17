resource "azurerm_databricks_workspace" "dbx" {
  name                = var.name_databricks
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = "premium"
  depends_on          = [azurerm_resource_group.rsg_datamaster]
}

data "azurerm_databricks_access_connector" "unity_catalog" {
  name                = "unity-catalog-access-connector"
  resource_group_name = "databricks-rg-${var.resource_group_name}"
  depends_on          = [azurerm_databricks_workspace.dbx]
}

data "azurerm_user_assigned_identity" "databricks_identity" {
  name                = "dbmanagedidentity"
  resource_group_name = "databricks-rg-${var.resource_group_name}"
  depends_on          = [azurerm_databricks_workspace.dbx]
}

resource "null_resource" "provision_databricks" {
  provisioner "local-exec" {
    command = "bash ${path.module}/databricks_user.sh"

    environment = {
      WORKSPACE_URL        = azurerm_databricks_workspace.dbx.workspace_url
      ADMIN_EMAIL          = var.admin_email
      DATABRICKS_RESOURCE  = var.databricks_resource
      REGION               = var.location
      KEYVAULT_NAME        = var.keyvault_name
      KEYVAULT_DNS         = azurerm_key_vault.kv.vault_uri
      KEYVAULT_RESOURCE_ID = azurerm_key_vault.kv.id
      WORKSPACE_ID         = azurerm_databricks_workspace.dbx.id
    }
  }
  depends_on = [azurerm_databricks_workspace.dbx]
  triggers = {
    always_run = timestamp()
  }  
}

