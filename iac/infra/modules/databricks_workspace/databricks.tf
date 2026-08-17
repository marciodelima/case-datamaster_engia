data "azurerm_databricks_workspace" "dbx" {
  name                = var.name
  resource_group_name = var.resource_group_name
}

data "azurerm_databricks_access_connector" "unity_catalog" {
  name                = "unity-catalog-access-connector"
  resource_group_name = "databricks-rg-${var.resource_group_name}"
}

