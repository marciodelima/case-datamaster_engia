data "azurerm_key_vault" "kv" {
  name                = var.keyvault_name
  resource_group_name = var.resource_group_name
}

