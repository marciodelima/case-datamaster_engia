data "azurerm_subscription" "primary" {}

output "azure_client_id" {
  value = azuread_application.github_app.client_id
}

output "azure_client_secret" {
  value     = azuread_application_password.github_secret.value
  sensitive = true
}

output "azure_tenant_id" {
  value = data.azurerm_client_config.current.tenant_id
}

output "azure_integration_identity" {
  value = azurerm_user_assigned_identity.integration_identity.name
}

output "azure_credentials_json" {
  value = jsonencode({
    clientId       = azuread_application.github_app.client_id
    clientSecret   = azuread_application_password.github_secret.value
    tenantId       = data.azurerm_client_config.current.tenant_id
    subscriptionId = data.azurerm_subscription.primary.subscription_id
  })
  sensitive = true
}

output "rsg_name" {
  value = var.resource_group_name
}

output "iac_name_storage" {
  value = var.iac_terraform_storage
}

