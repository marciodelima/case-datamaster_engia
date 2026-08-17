resource "azurerm_user_assigned_identity" "integration_identity" {
  name                = "integration-identity"
  location            = var.location
  resource_group_name = var.resource_group_name
  depends_on          = [azurerm_resource_group.rsg_datamaster]
}

