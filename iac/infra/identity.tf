data "azurerm_user_assigned_identity" "integration_identity" {
  name                = "integration-identity"
  resource_group_name = var.resource_group_name
}

