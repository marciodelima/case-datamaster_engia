output "workspace_id" {
  description = "ID do workspace Databricks"
  value       = data.azurerm_databricks_workspace.dbx.id
}

output "workspace_name" {
  description = "Nome do workspace Databricks"
  value       = data.azurerm_databricks_workspace.dbx.name
}

output "workspace_url" {
  description = "URL do workspace Databricks"
  value       = data.azurerm_databricks_workspace.dbx.workspace_url
}

output "unity_catalog_access_connector_id" {
  value = data.azurerm_databricks_access_connector.unity_catalog.id
}

output "unity_catalog_access_connector_principal_id" {
  value = data.azurerm_databricks_access_connector.unity_catalog.identity[0].principal_id
}

